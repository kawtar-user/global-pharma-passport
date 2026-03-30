#!/bin/sh
set -eu

echo "[startup] Running database migrations..."
alembic -c /app/alembic.ini upgrade head
echo "[startup] Database migrations completed."
echo "[startup] Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
