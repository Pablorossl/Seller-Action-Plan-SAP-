#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Una única ejecución pre-deploy, nunca por worker ni durante la compilación.
python backend/manage.py migrate --noinput
python backend/manage.py migrate --check
python backend/manage.py check --deploy --fail-level WARNING
