# Guía de contribución

## Flujo de trabajo

1. Rama a partir de `main`: `feature/nombre-corto` o `fix/nombre-corto`.
2. Commits pequeños y descriptivos (ver convención abajo).
3. Antes de abrir PR: `./scripts/backend-test.sh` y/o `./scripts/frontend-test.sh`
   según lo que hayas tocado. El CI ejecuta lo mismo.
4. Toda decisión de arquitectura no trivial se documenta como ADR en
   `docs/decisions/` (ver [`docs/decisions/0001-record-architecture-decisions.md`](docs/decisions/0001-record-architecture-decisions.md)).

## Convención de commits

Formato: `tipo: descripción corta en imperativo`

Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`.

Ejemplos:

```
feat(backend): añadir endpoint de login con JWT
docs: registrar ADR sobre modelo multi-tenant
chore(frontend): configurar eslint y prettier
```

## Reglas de arquitectura a respetar

- Backend: el código en `app/domain/` no puede importar nada de
  `app/infrastructure/` ni de `app/api/`. Ver [`ARCHITECTURE.md`](ARCHITECTURE.md).
- Cualquier tabla de negocio nueva lleva `organization_id` obligatorio.
- No añadir integraciones externas ni automatizaciones sin que estén
  motivadas por una conversación real con un cliente — ver
  [`docs/decisions/0000-no-features-before-validation.md`](docs/decisions/0000-no-features-before-validation.md).

## Estilo de código

- Backend: `ruff` (lint + formato) y `mypy` (tipado estricto). Configurado
  en `backend/pyproject.toml`.
- Frontend: `eslint` + `prettier` + `tsc --noEmit`. Configurado en
  `frontend/package.json`.

Ambos se ejecutan automáticamente en CI (`.github/workflows/`).
