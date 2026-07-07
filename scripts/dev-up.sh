#!/usr/bin/env bash
# Levanta el entorno de desarrollo completo (db + backend + frontend).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "No existe .env — copiando .env.example"
  cp .env.example .env
fi

docker compose up --build
