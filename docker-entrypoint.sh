#!/bin/sh
set -e

# Run database table initialization at runtime (works with SQLite volume or Postgres)
echo "[Entrypoint] Verifying/creating database schema..."
python -c "from app import create_tables; create_tables()"

# Bind to dynamically assigned host PORT (Render, Cloud Run, Railway, etc.) or default to 5000
PORT="${PORT:-5000}"
WORKERS="${WEB_CONCURRENCY:-2}"
THREADS="${GUNICORN_THREADS:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-60}"

echo "[Entrypoint] Starting Gunicorn on 0.0.0.0:${PORT} (${WORKERS} workers, ${THREADS} threads)..."
exec gunicorn \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WORKERS}" \
    --threads "${THREADS}" \
    --timeout "${TIMEOUT}" \
    --access-logfile - \
    --error-logfile - \
    app:app
