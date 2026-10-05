# PostgreSQL 17 с демобазой авиаперевозок Postgres Pro (версия 2016-10-13, small).
# Дамп скачивается с сайта Postgres Pro при сборке образа, поэтому на своём
# компьютере ничего, кроме Docker, не нужно.

# Шаг 1. Скачать архив и перепаковать в .sql.gz: в образе postgres нет unzip, а gunzip есть.
FROM alpine:3.20 AS dump
ADD https://edu.postgrespro.ru/demo-small-20161013.zip /tmp/demo.zip
RUN unzip -p /tmp/demo.zip | gzip > /demo-small-20161013.sql.gz

# Шаг 2. Образ базы: дамп и скрипт, который заливает его при первом старте.
FROM postgres:17
COPY --from=dump /demo-small-20161013.sql.gz /dump/
COPY init/ /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/*.sh
