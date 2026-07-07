# Backend

API en **Python 3.12 + FastAPI**, con arquitectura hexagonal (Ports &
Adapters). Ver [`/ARCHITECTURE.md`](../ARCHITECTURE.md) para la visión
general del sistema completo.

## Estructura

```
app/
├── api/              # Adaptador de entrada: rutas HTTP, DTOs (Pydantic), dependencias
├── application/      # Casos de uso: orquestan el dominio
├── domain/           # Entidades y reglas de negocio puras (sin imports de infra/api)
├── infrastructure/   # Adaptadores de salida: SQLAlchemy, clientes externos
└── core/             # Config, logging, seguridad, manejo de errores
```

**Regla de dependencia**: `api → application → domain`. `infrastructure`
implementa interfaces (`Protocol`) definidas en `domain`, pero `domain`
nunca importa de `infrastructure` ni de `api`. Antes de añadir un import,
comprueba que no rompe esta dirección.

## Desarrollo local

Desde la raíz del repo:

```bash
cp .env.example .env
./scripts/dev-up.sh
```

O directamente con Python (requiere Postgres accesible en `DATABASE_URL`):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Documentación interactiva de la API en `http://localhost:8000/docs`.

## Migraciones (Alembic)

```bash
./scripts/migrate.sh                                   # aplicar migraciones pendientes
docker compose run --rm backend alembic revision -m "descripción"  # crear una nueva (vacía, a rellenar a mano)
```

Este proyecto no usa `alembic revision --autogenerate` a ciegas: revisa
siempre el SQL generado antes de aplicarlo.

## Tests

```bash
./scripts/backend-test.sh
```

Los tests de integración (`tests/test_auth.py`) necesitan una base de
datos PostgreSQL real (usan tipos específicos de Postgres — `JSONB`,
`UUID`). En CI se levanta como servicio (ver
`.github/workflows/backend-ci.yml`); en local, `docker compose` ya expone
el servicio `db`.

## Añadir una funcionalidad nueva

1. **Entidad de dominio** en `domain/entities/` (si aplica) — sin
   dependencias de frameworks.
2. **Interfaz de repositorio** en `domain/repositories/` si necesita
   persistencia.
3. **Caso de uso** en `application/services/`.
4. **Implementación del repositorio** en `infrastructure/database/repositories/`
   + modelo SQLAlchemy en `infrastructure/database/models/` + migración
   Alembic.
5. **Router + schemas** en `api/v1/`.

Recuerda: toda tabla de negocio nueva lleva `organization_id` (ver ADR
0005) y toda decisión no trivial se documenta como ADR.
