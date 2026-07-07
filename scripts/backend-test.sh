#!/usr/bin/env bash
# Ejecuta lint, tipado y tests del backend dentro del contenedor.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose run --rm backend ruff check .
docker compose run --rm backend mypy app
docker compose run --rm backend pytest
