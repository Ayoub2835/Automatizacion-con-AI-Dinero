# GestorIA (nombre de trabajo)

> SaaS de IA para gestorías españolas. Este repositorio contiene la **base
> técnica** del producto: todavía estamos validando el problema exacto con
> clientes reales, por lo que el código prioriza modularidad y facilidad de
> cambio sobre funcionalidades específicas.

**Estado del proyecto:** 🏗️ Fase de fundación técnica (pre-validación de mercado).
No hay funcionalidades de negocio implementadas todavía a propósito — ver
[`docs/decisions/`](docs/decisions) y [`ROADMAP.md`](ROADMAP.md) para el razonamiento.

## ¿Qué es esto?

Un punto de partida profesional para construir un SaaS de IA dirigido a
gestorías (asesorías fiscales, laborales y contables) en España. Incluye:

- Backend en **Python + FastAPI** con arquitectura limpia (hexagonal).
- Base de datos **PostgreSQL** con un modelo de datos multi-tenant flexible.
- Panel web en **Next.js + TypeScript** (base, sin funcionalidades de negocio).
- Entorno de desarrollo con **Docker Compose**.
- CI/CD con **GitHub Actions** (lint, tipado, tests).
- Documentación de arquitectura y decisiones técnicas (ADRs).

Lo que **no** incluye todavía, a propósito:

- Integraciones con software de gestorías (A3, Sage, etc.).
- Automatizaciones o agentes de IA complejos.
- Cualquier funcionalidad que dependa de hipótesis de producto sin validar
  con clientes reales.

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
