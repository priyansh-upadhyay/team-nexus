#!/bin/sh
set -e

echo "=========================================="
echo "Team Nexus Backend Starting"
echo "=========================================="

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

echo "[INFO] Waiting for PostgreSQL at $DB_HOST:$DB_PORT ..."

max_retries=30
retry_count=0

until python -c "
import socket, sys
try:
    s = socket.create_connection(('$DB_HOST', $DB_PORT), timeout=2)
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    retry_count=$((retry_count + 1))
    if [ "$retry_count" -ge "$max_retries" ]; then
        echo "[ERROR] PostgreSQL not ready after $max_retries attempts. Exiting."
        exit 1
    fi
    echo "[WAIT] Attempt $retry_count/$max_retries — retrying in 2s..."
    sleep 2
done

echo "[OK] PostgreSQL is ready."

echo "[INFO] Running Alembic migrations..."
alembic upgrade head
echo "[OK] Migrations complete."

echo "[INFO] Starting uvicorn production server on 0.0.0.0:8000 ..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
