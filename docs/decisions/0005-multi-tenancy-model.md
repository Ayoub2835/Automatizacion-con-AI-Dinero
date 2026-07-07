# 0005 — Multi-tenancy a nivel de fila desde el primer commit

**Estado**: Aceptado
**Fecha**: 2026-07-07

## Contexto

El cliente de este SaaS es una gestoría (una organización con varios
empleados), no un usuario individual. Añadir multi-tenancy después de
tener datos de producción es una migración costosa y arriesgada.

Alternativas consideradas: base de datos separada por tenant (aislamiento
fuerte, pero mucha complejidad operativa para una fase de validación), y
aislamiento a nivel de fila con `organization_id` (más simple
operativamente, suficiente aislamiento para esta fase).

## Decisión

Multi-tenancy **a nivel de fila**: toda tabla de negocio incluye una
columna `organization_id` (FK a `organizations`) obligatoria y NOT NULL. El
acceso a datos siempre se filtra por la organización del usuario
autenticado; esto se centraliza en la capa de repositorios
(`infrastructure/database/repositories`), no en cada endpoint.

## Consecuencias

- Cualquier tabla nueva que un desarrollador añada debe llevar
  `organization_id` — se documenta como regla en `ARCHITECTURE.md`.
- Si en el futuro un cliente enterprise exige aislamiento físico de datos,
  se puede migrar a base de datos por tenant partiendo de este modelo
  (cada organización ya está delimitada), pero no se construye esa
  complejidad ahora sin necesidad demostrada.
