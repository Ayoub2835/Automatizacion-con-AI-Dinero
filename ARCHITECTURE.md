# Arquitectura del sistema

Este documento describe la arquitectura técnica actual y los principios que
la guían. Las decisiones puntuales con su justificación están en
[`docs/decisions/`](docs/decisions) (formato ADR); aquí se describe la
imagen completa.

## 1. Principios de diseño

1. **Optimizar para el cambio, no para la escala.** Todavía no sabemos qué
   funcionalidad exacta va a validar el mercado. La arquitectura prioriza
   que sea barato reescribir lógica de negocio, no que soporte millones de
   usuarios desde el día uno.
2. **Arquitectura limpia / hexagonal en el backend.** El dominio (reglas de
   negocio) no conoce ni FastAPI ni SQLAlchemy ni Next.js. Los frameworks
   son detalles de infraestructura, intercambiables.
3. **Multi-tenant desde el primer commit.** El cliente de este SaaS es una
   gestoría (organización), no una persona individual. Todo el modelo de
   datos parte de esa premisa para no tener que hacer una migración masiva
   más adelante.
4. **Extensibilidad explícita.** Donde todavía no sabemos qué construir
   (integraciones, automatizaciones, agentes IA), se deja un punto de
   extensión documentado en vez de una implementación especulativa.
5. **Todo lo aburrido, resuelto ya.** Logging, manejo de errores,
   configuración por entorno, tests, CI/CD y Docker están resueltos desde el
   principio para que cada nueva funcionalidad se enfoque solo en lógica de
   negocio.

## 2. Vista general

```
┌─────────────────┐        HTTPS/JSON        ┌──────────────────────┐
│   Frontend       │ ───────────────────────▶ │   Backend (FastAPI)  │
│   Next.js + TS   │ ◀─────────────────────── │   API REST           │
└─────────────────┘                           └──────────┬───────────┘
                                                          │
                                                          ▼
                                               ┌──────────────────────┐
                                               │   PostgreSQL          │
                                               │   (multi-tenant)      │
                                               └──────────────────────┘
```

Ambos servicios se ejecutan en contenedores Docker independientes,
orquestados por `docker-compose.yml` en desarrollo. La comunicación es
exclusivamente vía API REST (sin acoplamiento de código entre frontend y
backend), lo que permite reemplazar cualquiera de los dos sin tocar el otro.

## 3. Backend: arquitectura hexagonal (Ports & Adapters)

```
backend/app/
├── api/              # Adaptador de entrada: rutas HTTP, DTOs, dependencias
│   ├── v1/
│   │   ├── routers/
│   │   └── schemas/  # Pydantic: contratos de request/response
│   └── deps.py
├── application/      # Casos de uso: orquestan el dominio, sin lógica HTTP
│   └── services/
├── domain/           # Núcleo: entidades y reglas de negocio puras
│   ├── entities/
│   ├── repositories/ # Interfaces (puertos) — sin implementación
│   └── exceptions.py
├── infrastructure/    # Adaptadores de salida: DB, servicios externos
│   ├── database/
│   │   ├── models/    # Modelos SQLAlchemy (detalle de infraestructura)
│   │   └── repositories/ # Implementaciones concretas de los puertos
│   └── external/      # Clientes a servicios externos (ej. proveedor LLM)
└── core/              # Config, logging, seguridad, manejo de errores
```

**Regla de dependencia**: las flechas de import solo pueden apuntar hacia
adentro. `api` depende de `application`, que depende de `domain`.
`infrastructure` implementa interfaces definidas en `domain`, pero `domain`
nunca importa `infrastructure`. Esto es lo que permite cambiar de
PostgreSQL a otra cosa, o añadir un cliente LLM distinto, sin tocar la
lógica de negocio.

Ver [`backend/README.md`](backend/README.md) para el detalle de cada capa
y las convenciones de código.

## 4. Base de datos: modelo flexible multi-tenant

Entidades del núcleo (ver [`docs/decisions/0004-database-postgresql.md`](docs/decisions/0004-database-postgresql.md)
y [`docs/decisions/0005-multi-tenancy-model.md`](docs/decisions/0005-multi-tenancy-model.md)):

- **Organization** (la gestoría, el tenant).
- **User** (pertenece a una Organization, con un rol).

Ambas tablas incluyen una columna `metadata_ (JSONB)` pensada explícitamente
como **punto de extensión**: permite guardar atributos específicos de un
cliente o experimento sin necesitar una migración de esquema, hasta que ese
atributo demuestre ser importante y merezca convertirse en una columna real
e indexada.

Toda tabla de negocio que se añada en el futuro debe incluir
`organization_id` como clave foránea obligatoria — es la regla de
aislamiento multi-tenant del sistema.

## 5. Frontend: base de panel

Next.js (App Router) + TypeScript. Por ahora es intencionalmente mínimo:
autenticación contra el backend y un shell de dashboard vacío, sin
funcionalidades de negocio. Ver [`frontend/README.md`](frontend/README.md).

El navegador nunca llama directamente a la API de FastAPI: todas las
llamadas pasan por Route Handlers de Next.js, que gestionan la sesión con
una cookie `httpOnly` (patrón "Backend for Frontend"). Ver
[ADR 0007](docs/decisions/0007-frontend-backend-for-frontend.md).

## 6. Transversales (Fase 1)

| Aspecto | Solución actual |
|---|---|
| Configuración | Variables de entorno vía `pydantic-settings` (backend) y `.env.local` (frontend), un `.env.example` documentado en la raíz |
| Logging | Logging estructurado (JSON) en backend, con nivel configurable por entorno |
| Manejo de errores | Excepciones de dominio propias + manejador global en FastAPI que las traduce a respuestas HTTP consistentes |
| Tests | `pytest` (backend), `vitest`/Playwright (frontend, base) |
| CI/CD | GitHub Actions: lint + tipado + tests en cada PR, para backend y frontend por separado |
| Contenedores | Dockerfile por servicio + `docker-compose.yml` para desarrollo local |

## 7. Decisiones explícitamente pospuestas

Estas decisiones se dejan abiertas a propósito porque dependen de aprender
de clientes reales. Están documentadas para que quien retome el proyecto
sepa que son pendientes deliberadas, no descuidos:

- **Modelo de suscripción y facturación** (planes, límites de uso).
- **Integraciones con software de gestorías** (A3, Sage, etc.) — requiere
  saber qué usa cada cliente objetivo.
- **Automatizaciones y agentes de IA** — requiere saber qué tarea manual
  duele lo suficiente como para automatizarla.
- **Modelo de permisos granular** (más allá de rol admin/miembro).
- **Estrategia de despliegue en producción** (proveedor cloud, orquestación).
  Docker Compose cubre desarrollo local; producción se decide cuando haya
  tráfico real que dimensionar.

Cuando se tome cada una de estas decisiones, debe documentarse como un ADR
nuevo en `docs/decisions/`.
