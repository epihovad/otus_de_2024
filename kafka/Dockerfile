FROM debezium/connect:2.7.3.Final

# Скопировать ClickHouse коннектор в директорию плагинов
COPY plugins/*.jar /kafka/connect

USER root

RUN update-crypto-policies --set LEGACY