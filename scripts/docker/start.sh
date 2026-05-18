#!/bin/sh
set -e

echo "Waiting for PostgreSQL at ${POSTGRES_SERVER}:${POSTGRES_PORT}..."
until nc -z "${POSTGRES_SERVER}" "${POSTGRES_PORT}"; do
  sleep 1
done

echo "Running Alembic migrations..."
cd /app/src
alembic upgrade head

echo "Starting FastAPI..."
cd /app
uvicorn src.app.main:app --host 0.0.0.0 --port 8000
