#!/bin/bash
# Заливает в базу hse_databases две дополнительные учебные базы, каждую в свою схему:
# film_rental (Pagila, прокат DVD) и music_store (Chinook, магазин музыки).
# Дампы готовятся заранее и лежат в образе.
set -euo pipefail

for item in film_rental:15 music_store:11; do
    schema=${item%%:*}
    expected=${item##*:}
    echo "Загружаю схему $schema"
    gunzip -c "/dump/$schema.sql.gz" \
        | psql --username "$POSTGRES_USER" --dbname hse_databases -q -v ON_ERROR_STOP=1 >/dev/null
    tables=$(psql --username "$POSTGRES_USER" --dbname hse_databases -At \
                  -c "SELECT count(*) FROM pg_tables WHERE schemaname = '$schema'")
    if [ "$tables" != "$expected" ]; then
        echo "Схема $schema загружена не полностью: таблиц $tables, должно быть $expected" >&2
        exit 1
    fi
done
echo "Все учебные базы загружены"
