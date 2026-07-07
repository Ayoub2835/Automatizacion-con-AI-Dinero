# 0006 — Monorepo para backend y frontend

**Estado**: Aceptado
**Fecha**: 2026-07-07

## Contexto

Con un equipo pequeño y un producto aún sin validar, backend y frontend
cambian juntos con frecuencia (nuevos endpoints + su consumo inmediato en
el panel).

## Decisión

Un único repositorio con `backend/` y `frontend/` como proyectos
independientes (cada uno con su propio gestor de dependencias, Dockerfile
y pipeline de CI), en vez de repositorios separados.

## Consecuencias

- Un solo PR puede cambiar API y consumidor a la vez, lo que reduce
  fricción mientras el equipo es pequeño y el producto cambia rápido.
- Si en el futuro hay equipos separados para backend y frontend, se puede
  dividir el monorepo (cada carpeta ya es independiente en dependencias y
  build) sin reescribir código.
