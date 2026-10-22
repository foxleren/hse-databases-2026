# PostgreSQL 17 с учебной базой hse_databases: демобаза авиаперевозок Postgres Pro
# (версия 2016-10-13, small) и две дополнительные базы, каждая в своей схеме.
# Дамп демобазы скачивается с сайта Postgres Pro при сборке образа, дампы остальных
# лежат в папке dumps/, поэтому на своём компьютере ничего, кроме Docker, не нужно.

# Шаг 1. Скачать архив демобазы и перепаковать в .sql.gz: в образе postgres нет unzip, а gunzip есть.
FROM alpine:3.20 AS dump
ADD https://edu.postgrespro.ru/demo-small-20161013.zip /tmp/demo.zip
RUN unzip -p /tmp/demo.zip | gzip > /demo-small-20161013.sql.gz

# Шаг 2. Образ базы: дампы и скрипты, которые заливают их при первом старте.
FROM postgres:17
COPY --from=dump /demo-small-20161013.sql.gz /dump/
COPY dumps/ /dump/
COPY init/ /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/*.sh
