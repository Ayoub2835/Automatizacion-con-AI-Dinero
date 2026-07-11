# 0014 — BookAgent AI: agente autónomo de creación y publicación de libros

**Estado**: Aceptado
**Fecha**: 2026-07-11

## Contexto

Se pidió ampliar el repositorio con un segundo producto, **BookAgent AI**:
un agente autónomo que investiga mercado, escribe un libro completo
(título, esquema, capítulos, edición, copy comercial, SEO, categorías,
idea de portada) a partir de un brief del usuario, lo exporta a EPUB/PDF,
y prepara — con revisión humana obligatoria — su publicación en tiendas
de autopublicación (Amazon KDP, Apple Books, Google Play Books, Kobo).

Este repositorio no tenía previamente ningún código de BookAgent AI: el
producto existente (GestorIA, ver ADR 0000/0008) es un SaaS de gestión
documental para gestorías españolas, con una política explícita de "sin
funcionalidades nuevas hasta validar con clientes reales" — esa política
es específica de GestorIA, no aplica a un producto distinto.

Se decidió construir BookAgent AI como **segundo producto sobre la misma
base técnica multi-tenant** (Organization/User, autenticación JWT,
PostgreSQL, backend hexagonal, panel Next.js con patrón BFF) en vez de
levantar un proyecto aparte desde cero: es exactamente el escenario para
el que esa base se diseñó (ver ARCHITECTURE.md, "Optimizar para el
cambio"), y compartir auth/multi-tenancy es la diferencia entre un
prototipo y algo con forma de SaaS profesional desde el primer commit.

## Decisión

### Dominio y pipeline de generación

Nuevas entidades (`app/domain/entities/book.py`, `publishing.py`):
`Book`, `Chapter`, `PublishingAccount`, `Publication`, `SalesRecord` —
todas con `organization_id`, siguiendo la regla de aislamiento
multi-tenant existente.

El pipeline autónomo (`BookGenerationService.run_pipeline`) ejecuta, en
orden, sobre el puerto `BookContentGenerator`
(`ClaudeBookContentGenerator` como única implementación, sobre la API de
Claude con structured outputs igual que ADR 0011):

1. `research_market` — tendencias, ángulos con demanda, competidores, SEO.
2. `generate_title` — título y subtítulo.
3. `generate_outline` — esquema de capítulos (nº de capítulos derivado de
   `target_pages`, ~300 palabras/página).
4. `write_chapter` — redacción de cada capítulo.
5. `edit_chapter` — pasada de gramática/calidad por capítulo.
6. `generate_sales_copy` — blurb, keywords SEO, categorías.
7. `generate_cover_brief` — brief de portada en texto (no genera la
   imagen: fuera de alcance del MVP, ver "Explícitamente pospuesto").
8. Exportación a EPUB (`ebooklib`) y PDF (`fpdf2`) — librerías puras en
   Python, sin dependencias de sistema.

Cada etapa se persiste (`Book.generation_stage`) y confirma
individualmente, así el panel puede mostrar progreso incremental
("escribiendo capítulo 3/7") y un fallo a mitad de pipeline no pierde el
trabajo previo (`Book.status` pasa a `failed` con `error_message`, no se
pierde título/esquema/capítulos ya generados). Se lanza como
`BackgroundTask` de FastAPI al crear el libro — suficiente para el
volumen de un MVP; si el volumen crece, el punto de extensión es
sustituir `BackgroundTasks` por una cola real (Celery/RQ) sin tocar
`BookGenerationService`, que no conoce el mecanismo de disparo.

### Publishing Agent

Puerto `PublishingConnector` (`app/domain/ports/publishing_connector.py`)
con una máquina de estados en `Publication.status`:

```
DRAFT/METADATA_READY → PENDING_REVIEW → APPROVED → SUBMITTED → LIVE
                              ↓
                          REJECTED
```

`PENDING_REVIEW`→`APPROVED` es un paso humano obligatorio antes de poder
enviar nada a una plataforma — cubre el requisito de "permitir revisar
antes de publicar".

**Ninguna de las cuatro plataformas pedidas ofrece hoy una API pública de
autopublicación para autores individuales**:

| Plataforma | Estado de la API | Conector |
|---|---|---|
| Amazon KDP | Sin API pública; ToS prohíbe automatizar la subida | `KdpConnector` — manual/asistido permanente |
| Apple Books | Sin API pública de publicación (solo Apple Books for Authors / iTunes Producer, sin API HTTP) | `AppleBooksConnector` — manual/asistido permanente |
| Kobo Writing Life | Sin API pública | `KoboConnector` — manual/asistido permanente |
| Google Play Books | **Sí** tiene una API de partners (Partner Center), pero requiere acuerdo firmado con Google | `GooglePlayBooksConnector` — manual por defecto, con `api_enabled` como punto de extensión explícito |

Todos heredan de `ManualAssistedConnector`: en vez de fallar,
`submit()` genera un paquete de instrucciones (checklist de campos,
ficheros preparados, URL de subida de la plataforma) para que un humano
complete la publicación, y deja `Publication.status = SUBMITTED`. El
paso a `LIVE` es siempre una confirmación manual explícita
(`PublishingService.mark_live`) — nunca se asume que algo se publicó.

Esto es el "sistema preparado para integración futura y proceso
asistido" que pide la spec: cuando una plataforma abra una API real
(o la organización consiga un acuerdo de partner con Google), se
sustituye/activa el conector correspondiente sin tocar
`PublishingService` ni el modelo de datos — `PublishingConnector` ya es
el punto de extensión.

### Ventas e ingresos

`SalesRecord` con `source="manual"` — no hay integración con las APIs de
ventas de cada plataforma en este MVP (KDP Reports, etc. no tienen todas
API pública, y las que sí requieren OAuth por plataforma). El panel
agrega estos registros manuales (`PublishingService.dashboard_summary`).
La estructura ya tiene el campo `source` para cuando se añada una
sincronización real por API.

### Panel

`/dashboard/books` (crear + listar + progreso) y `/dashboard/publishing`
(cuentas conectadas + estadísticas agregadas), reutilizando el layout,
autenticación y patrón BFF ya existentes en el panel Next.js.

## Explícitamente pospuesto (MVP realista)

- **Generación real de la imagen de portada**: `generate_cover_brief`
  produce un brief en texto, no una imagen. Añadir un generador de
  imágenes es un punto de extensión (`CoverImageGenerator`, nuevo puerto)
  para cuando se valide que hace falta.
- **Investigación de mercado con datos reales en vivo**: `research_market`
  usa el conocimiento del modelo, no una API de búsqueda externa. El
  puerto está aislado (`BookContentGenerator.research_market`) para que
  cambiar la implementación a una que use un proveedor de búsqueda real
  (Brave, Serper...) no toque el resto del pipeline.
- **Cola de tareas real** para el pipeline (Celery/RQ) — `BackgroundTasks`
  de FastAPI es suficiente para el volumen de un MVP.
- **OAuth por plataforma / credenciales reales de cuenta conectada** —
  `PublishingAccount.connection_status` ya distingue `MANUAL` de
  `CONNECTED`, pero solo `MANUAL` se usa hasta que exista una integración
  real que lo justifique.
- **Sincronización automática de ventas** por API de cada plataforma.

## Consecuencias

- Comparte multi-tenancy, autenticación y CI/CD con GestorIA sin fricción
  — dos productos, una base técnica.
- El coste de generación es cero hasta que se configure
  `ANTHROPIC_API_KEY` (igual que ADR 0011): sin ella, el pipeline falla
  de forma controlada (`Book.status = failed`) sin romper el resto del
  flujo.
- La arquitectura de conectores hace explícito, en vez de ocultar, que
  la autopublicación en KDP/Apple Books/Kobo es fundamentalmente un
  proceso asistido a día de hoy — evita prometer una automatización que
  las plataformas no permiten.
