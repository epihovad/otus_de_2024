FROM apache/airflow:2.10.3-python3.11

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        vim && \
    # Очистка ненужных пакетов и кэша для уменьшения размера образа
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

# установка python пакетов
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-warn-script-location --no-cache-dir -r requirements.txt

COPY dags /opt/airflow/dags

RUN chmod -R 775 /opt/airflow/dags/tmp

USER airflow