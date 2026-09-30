#!/bin/sh
set -e
echo "==> Running Alembic migrations..."
alembic upgrade head
echo "==> Running production seed (idempotent)..."
python /scripts/seed_production.py
echo "==> Starting uvicorn on port 10000..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 10000 \
  --workers 2 \
  --proxy-headers \
  --forwarded-allow-ips='*' \
  --log-level info
