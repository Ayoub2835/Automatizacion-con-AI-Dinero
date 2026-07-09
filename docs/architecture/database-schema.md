# Esquema de base de datos (Fase 0/1)

Motor: PostgreSQL 16. Migraciones gestionadas con Alembic
(`backend/alembic/versions/`). Ver [ADR 0004](../decisions/0004-database-postgresql.md)
y [ADR 0005](../decisions/0005-multi-tenancy-model.md) para el razonamiento.

## Tablas actuales

### `organizations`

La gestoría (tenant).

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID (PK) | |
| `name` | text | |
| `metadata` | JSONB | Punto de extensión — ver ADR 0004 |
| `created_at` | timestamptz | `server_default=now()` |

### `users`

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID (PK) | |
| `organization_id` | UUID (FK → organizations.id) | Obligatorio, indexado |
| `email` | text | Único a nivel global (no por organización) |
| `hashed_password` | text | bcrypt |
| `role` | text con CHECK (`admin` \| `member`) | Ver nota abajo |
| `metadata` | JSONB | Punto de extensión |
| `created_at` | timestamptz | |

**Nota sobre `role`**: se implementa como `VARCHAR` con restricción `CHECK`
(`native_enum=False` en SQLAlchemy) en vez de un tipo `ENUM` nativo de
Postgres. Añadir un rol nuevo es una migración simple (`ALTER TABLE ...
DROP CONSTRAINT` + `ADD CONSTRAINT`); con un ENUM nativo, añadir un valor
requiere `ALTER TYPE ... ADD VALUE`, que tiene restricciones dentro de
transacciones. Se prioriza flexibilidad sobre la validación extra que da
un tipo nativo.

### `clients`

Un cliente de la gestoría (destinatario de solicitudes de documentación,
ver [ADR 0008](../decisions/0008-mvp-empleado-documental.md)).

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID (PK) | |
| `organization_id` | UUID (FK → organizations.id) | Obligatorio, indexado |
| `name` | text | |
| `email` | text | No único: una gestoría puede tener clientes con el mismo email de contacto (ej. una gestoría) |
| `phone` | text (nullable) | |
| `metadata` | JSONB | Punto de extensión |
| `created_at` | timestamptz | |

### `campaigns`

Una campaña de solicitud de documentación.

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID (PK) | |
| `organization_id` | UUID (FK → organizations.id) | Obligatorio, indexado |
| `name` | text | |
| `metadata` | JSONB | Punto de extensión |
| `created_at` | timestamptz | |

### `campaign_document_types`

Los tipos de documento que pide una campaña (texto libre, ver ADR 0008).

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID (PK) | |
| `campaign_id` | UUID (FK → campaigns.id) | Obligatorio, indexado |
| `name` | text | Único por campaña (`UNIQUE(campaign_id, name)`) |
| `created_at` | timestamptz | |

## Regla para tablas futuras

Toda tabla de negocio nueva:

1. Incluye `organization_id UUID NOT NULL REFERENCES organizations(id)`
   (salvo que sea explícitamente global al sistema, lo cual debe
   justificarse en el PR).
2. Considera si necesita una columna `metadata JSONB` para atributos aún
   no consolidados.
3. Se añade vía una migración de Alembic escrita/revisada a mano — no se
   usa `--autogenerate` sin revisar el SQL resultante.

## Entidades pendientes de diseñar (no crear todavía)

Cualquier entidad de negocio (documentos, clientes de la gestoría,
tareas, etc.) se diseña cuando la Fase 1 de validación (ver
[`/ROADMAP.md`](../../ROADMAP.md)) confirme qué necesita el producto. No
existen todavía tablas "preparadas por si acaso".
