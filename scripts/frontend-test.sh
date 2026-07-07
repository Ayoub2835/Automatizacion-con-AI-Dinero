#!/usr/bin/env bash
# Ejecuta lint, tipado y tests del frontend dentro del contenedor.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose run --rm frontend npm run lint
docker compose run --rm frontend npm run type-check
docker compose run --rm frontend npm run test
