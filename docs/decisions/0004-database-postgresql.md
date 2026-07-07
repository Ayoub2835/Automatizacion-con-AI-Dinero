# 0004 — Base de datos PostgreSQL con columnas de metadatos flexibles

**Estado**: Aceptado
**Fecha**: 2026-07-07

## Contexto

Todavía no sabemos qué atributos de negocio necesitaremos guardar a medida
que se valide el producto. Un esquema completamente rígido implicaría
migraciones constantes; un esquema completamente "schemaless" (ej. Mongo)
renunciaría a integridad referencial y a la capacidad de hacer queries
relacionales complejas, que sí necesitaremos (el dominio es
inherentemente relacional: organizaciones, usuarios, roles).

## Decisión

**PostgreSQL** como base de datos principal, con SQLAlchemy 2.0 + Alembic
para migraciones. Como mecanismo de flexibilidad, las tablas núcleo
incluyen una columna `metadata_ JSONB` pensada como zona de aterrizaje
para atributos que aún no sabemos si merecen ser una columna propia.

Regla práctica: un atributo vive en `metadata_` hasta que se necesite
indexarlo, validarlo a nivel de base de datos, o hacer joins/filtros
frecuentes sobre él — en ese momento se "gradúa" a columna real vía
migración.

## Consecuencias

- Evitamos parálisis por migraciones prematuras sin renunciar a
  integridad relacional donde importa (claves foráneas, constraints).
- Riesgo a vigilar: que `metadata_` se convierta en un cajón de sastre sin
  disciplina. Mitigación: cualquier campo en `metadata_` que se use en más
  de un endpoint debe evaluarse para graduarse a columna.
