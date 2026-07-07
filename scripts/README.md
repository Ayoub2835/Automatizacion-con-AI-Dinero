# Scripts de desarrollo

Todos se ejecutan desde cualquier carpeta (resuelven la raíz del repo
internamente) y asumen Docker Compose.

| Script | Qué hace |
|---|---|
| `dev-up.sh` | Levanta el entorno completo (Postgres + backend + frontend) con hot-reload |
| `dev-down.sh` | Detiene y limpia los contenedores del entorno de desarrollo |
| `migrate.sh` | Aplica las migraciones de Alembic pendientes a la base de datos |
| `backend-test.sh` | Lint (ruff) + tipado (mypy) + tests (pytest) del backend |
| `frontend-test.sh` | Lint (eslint) + tipado (tsc) + tests (vitest) del frontend |

Uso:

```bash
chmod +x scripts/*.sh   # solo la primera vez
./scripts/dev-up.sh
```
