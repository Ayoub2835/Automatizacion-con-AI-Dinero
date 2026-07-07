#!/usr/bin/env bash
# Detiene el entorno de desarrollo.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose down
