#!/usr/bin/env bash
# Aplica las migraciones de base de datos pendientes.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose run --rm backend alembic upgrade head
