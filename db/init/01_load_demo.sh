#!/bin/bash
# Заливает демобазу авиаперевозок Postgres Pro (версия 2016-10-13, small)
# при первом старте контейнера и переименовывает базу demo в hse_databases.
#
# Дамп выполняется как есть, без правок: он сам создаёт базу demo и схему bookings.
# На чистом сервере две его команды ожидаемо заканчиваются ошибкой — DROP DATABASE demo
# (базы ещё нет) и CREATE SCHEMA public (она уже есть), — поэтому psql запускается без
# остановки на первой ошибке, а результат проверяется отдельно, в конце.
set -euo pipefail

dump=$(ls /dump/demo-small-*.sql.gz | head -1)
echo "Загружаю $dump"
gunzip -c "$dump" | psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -q
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -q -c "ALTER DATABASE demo RENAME TO hse_databases"

tables=$(psql --username "$POSTGRES_USER" --dbname hse_databases -At \
              -c "SELECT count(*) FROM pg_tables WHERE schemaname = 'bookings'")
if [ "$tables" != "8" ]; then
    echo "Демобаза загружена не полностью: таблиц в схеме bookings — $tables, должно быть 8" >&2
    exit 1
fi
echo "Демобаза загружена в базу hse_databases, схема bookings"
