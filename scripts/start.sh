#!/usr/bin/env sh
set -eu

python /app/scripts/validate_env.py
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
