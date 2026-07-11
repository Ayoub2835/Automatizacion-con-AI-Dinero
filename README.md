# GestorIA (nombre de trabajo)

> SaaS de IA para gestorías españolas. El MVP ("Empleado Documental":
> reclamar, recibir y clasificar documentación de clientes) está terminado
> y funcionando de punta a punta. Ya no se construyen funcionalidades
> nuevas — la fase actual es conseguir el primer cliente de pago.

**Estado del proyecto:** 📣 Validación comercial (MVP terminado, sin
funcionalidades nuevas hasta que 3 gestorías distintas las pidan). Ver
[`ROADMAP.md`](ROADMAP.md), [`docs/decisions/`](docs/decisions) y
[`docs/go-to-market/`](docs/go-to-market/README.md) para el proceso de
venta, onboarding y feedback.

## Dos productos, una base técnica

Este repositorio aloja dos productos independientes sobre la misma base
multi-tenant (auth, PostgreSQL, backend hexagonal, panel Next.js con
patrón BFF):

- **GestorIA** — el SaaS de gestión documental descrito arriba. En fase de
  validación comercial: **sin funcionalidades nuevas** hasta que 3
  gestorías reales las pidan (ver ADR 0000).
- **[BookAgent AI](docs/decisions/0014-bookagent-ai-product.md)** — agente
  autónomo de creación y publicación de libros digitales: investiga
  mercado, escribe el manuscrito completo, lo exporta a EPUB/PDF y prepara
  (con revisión humana obligatoria) su publicación en Amazon KDP, Apple
  Books, Google Play Books y Kobo. Código en
  `backend/app/domain/entities/book.py`, `publishing.py` y sus capas
  asociadas; panel en `/dashboard/books` y `/dashboard/publishing`. La
  política de "sin features sin validar" de ADR 0000 es específica de
  GestorIA — no aplica a este segundo producto.

## ¿Qué es esto?

Un punto de partida profesional para construir un SaaS de IA dirigido a
gestorías (asesorías fiscales, laborales y contables) en España. Incluye:

- Backend en **Python + FastAPI** con arquitectura limpia (hexagonal).
- Base de datos **PostgreSQL** con un modelo de datos multi-tenant flexible.
- Panel web en **Next.js + TypeScript**, con el MVP "Empleado Documental"
  funcionando de punta a punta (clientes, campañas, envío, subida pública,
  clasificación con Claude, panel de estado, recordatorios).
- Entorno de desarrollo con **Docker Compose**.
- CI/CD con **GitHub Actions** (lint, tipado, tests).
- Documentación de arquitectura y decisiones técnicas (ADRs).

Lo que **no** incluye todavía, a propósito (ver
[`docs/go-to-market/roadmap-validado.md`](docs/go-to-market/roadmap-validado.md)):

- Integraciones con software de gestorías (A3, Sage, etc.).
- Automatizaciones o agentes de IA complejos.
- Multi-usuario, WhatsApp, importación masiva, exportación de datos, y
  cualquier otra cosa que no haya sido pedida o validada por al menos 3
  gestorías reales.

Ver [`docs/decisions/0000-no-features-before-validation.md`](docs/decisions/0000-no-features-before-validation.md)
para el razonamiento completo.

## Estructura del repositorio

```
.
├── backend/            # API en FastAPI (arquitectura hexagonal)
├── frontend/            # Panel web en Next.js
├── docs/
│   ├── architecture/    # Diagramas y documentación técnica detallada
│   └── decisions/       # Architecture Decision Records (ADRs)
├── scripts/             # Scripts de desarrollo (setup, lint, test, etc.)
├── .github/workflows/   # Pipelines de CI/CD
├── docker-compose.yml   # Entorno de desarrollo completo
├── ARCHITECTURE.md       # Visión general de la arquitectura
└── ROADMAP.md            # Plan de evolución del producto
```

Cada carpeta (`backend/`, `frontend/`) tiene su propio `README.md` con
detalles específicos de esa parte del sistema.

## Empezar a desarrollar

Requisitos: Docker y Docker Compose. Opcionalmente Python 3.12+ y Node.js 20+
si quieres correr backend/frontend fuera de contenedores.

```bash
# 1. Clonar y configurar variables de entorno
cp .env.example .env

# 2. Levantar todo el entorno (Postgres + backend + frontend)
./scripts/dev-up.sh

# Backend disponible en   http://localhost:8000  (docs en /docs)
# Frontend disponible en  http://localhost:3000
# Emails enviados (Mailpit) en http://localhost:8025
```

Ver [`scripts/README.md`](scripts/README.md) para el resto de scripts
disponibles (tests, lint, migraciones, etc.).

## Documentación

| Documento | Contenido |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Visión general del sistema, principios de diseño, capas |
| [`ROADMAP.md`](ROADMAP.md) | Fases del producto y qué se ha decidido posponer |
| [`docs/decisions/`](docs/decisions) | ADRs: por qué se tomó cada decisión técnica relevante |
| [`docs/architecture/`](docs/architecture) | Diagramas y documentación técnica en detalle |
| [`docs/go-to-market/`](docs/go-to-market/README.md) | Objeciones, guion de venta, onboarding, feedback y roadmap validado por clientes reales |
| [`backend/README.md`](backend/README.md) | Cómo trabajar en el backend |
| [`frontend/README.md`](frontend/README.md) | Cómo trabajar en el frontend |

## Filosofía de este repositorio

Todavía no sabemos exactamente qué funcionalidad va a validar el mercado.
Por eso esta base se ha diseñado para que **cambiar de idea sea barato**:

1. **Arquitectura hexagonal en el backend**: la lógica de negocio no depende
   de frameworks ni de la base de datos, así que se puede reescribir el 80%
   de las funcionalidades sin tocar el 20% de infraestructura.
2. **Modelo de datos multi-tenant desde el día uno** con campos de metadatos
   flexibles (JSONB), para no tener que migrar el esquema cada vez que
   aprendemos algo nuevo de un cliente.
3. **Sin integraciones ni automatizaciones prematuras**: cada una de estas
   piezas es cara de construir y mantener; se añaden cuando un cliente real
   las pide, no antes.

Cuando el equipo valide el problema con clientes reales, este repositorio
está pensado para crecer durante años, no para tirarse.
