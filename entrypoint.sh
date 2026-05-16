#!/bin/sh
set -e

echo "=========================================="
echo "Team Nexus Backend Starting"
echo "=========================================="

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
