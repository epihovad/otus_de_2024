#!/bin/bash
set -e

# Запускаем ClickHouse сервер в фоне
clickhouse-server --config-file=/etc/clickhouse-server/config.xml --daemon

# Ждем, пока сервер станет доступен
until clickhouse-client --query "SELECT 1" &>/dev/null; do
  echo "Waiting for ClickHouse to start..."
  sleep 1
done

# Поддерживаем контейнер активным
echo "ClickHouse server is running. Press Ctrl+C to stop."
tail -f /dev/null