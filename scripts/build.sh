#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -r backend/requirements.txt
python -m pip check
npm --prefix frontend ci
npm --prefix frontend run build
python backend/manage.py collectstatic --noinput
python backend/manage.py check --deploy --fail-level WARNING
