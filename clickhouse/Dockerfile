# Используем базовый образ Ubuntu 22.04
FROM ubuntu:22.04

# Устанавливаем переменную окружения для неинтерактивной установки
ENV DEBIAN_FRONTEND=noninteractive

# Обновление списка пакетов и установка необходимых инструментов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg2 \
        curl \
        nano \
        vim && \
    # Добавление ключа и репозитория ClickHouse
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754 && \
    echo "deb https://packages.clickhouse.com/deb stable main" | tee /etc/apt/sources.list.d/clickhouse.list && \
    # Повторное обновление списка пакетов и установка необходимых пакетов
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        clickhouse-server \
        clickhouse-client && \
    # Очистка ненужных пакетов и кэша для уменьшения размера образа
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./config/config.xml /etc/clickhouse-server/config.d/config.xml
COPY ./config/users.xml /etc/clickhouse-server/users.d/users.xml

# Создаем необходимые директории и устанавливаем права
RUN mkdir -p /var/lib/clickhouse && chown -R clickhouse:clickhouse /var/lib/clickhouse
RUN mkdir -p /var/log/clickhouse-server && chown -R clickhouse:clickhouse /var/log/clickhouse-server

# Устанавливаем рабочую директорию
WORKDIR /var/lib/clickhouse

# Копируем скрипт запуска
COPY on_start.sh /opt/on_start.sh
RUN chmod +x /opt/on_start.sh

# Переключаемся на пользователя clickhouse
USER clickhouse

# Установка скрипта как entrypoint
ENTRYPOINT ["/opt/on_start.sh"]
