#!/bin/sh
set -eu

echo "[startup] Running database migrations..."
alembic -c /app/alembic.ini upgrade head
echo "[startup] Database migrations completed."
echo "[startup] Ensuring MVP catalog seed..."
python -m app.seeds.bootstrap_mvp_catalog
echo "[startup] MVP catalog seed check completed."
echo "[startup] Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
