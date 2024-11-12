#!/bin/bash
set -e

# Запускаем PostgreSQL в фоне
docker-entrypoint.sh postgres &

# Ждем, пока сервер станет доступен
until pg_isready -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL to start..."
  sleep 1
done

# Выполняем ваш SQL-скрипт
echo "Running initialization script..."
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /tmp/csv/data.sql

# Поддерживаем контейнер активным
echo "PostgreSQL server is running. Press Ctrl+C to stop."
tail -f /dev/null
