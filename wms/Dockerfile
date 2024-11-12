FROM postgres:15.3

# Обновление списка пакетов и установка необходимых инструментов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        procps \
        vim && \
    # Очистка ненужных пакетов и кэша для уменьшения размера образа
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование CSV файлов для импорта в PG
COPY csv /tmp/csv

# Копирование SQL-скриптов инициализации
RUN chmod +x /tmp/csv/on_start.sh

# Установка скрипта как entrypoint
ENTRYPOINT ["/tmp/csv/on_start.sh"]