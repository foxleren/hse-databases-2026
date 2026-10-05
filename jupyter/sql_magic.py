"""Магия %%sql: выполняет ячейку в демобазе и показывает результат таблицей.

Ноутбук подключает её так:

    import sys; sys.path.insert(0, "../jupyter")
    %load_ext sql_magic

Использование:

    %%sql
    SELECT * FROM bookings.airports LIMIT 5;

Логин, пароль и порт берутся из файла .env в корне репозитория — того же, что читает
docker compose. Если Jupyter запущен в контейнере, адрес базы приходит из переменных
окружения PGHOST и PGPORT (их задаёт docker-compose.yml); без них — localhost и порт из .env.

В ячейке может быть несколько команд через «;»: показывается результат последней
команды, которая вернула строки, остальные печатают статус (CREATE TABLE, INSERT 0 3...).
"""
import os
from pathlib import Path

import pandas as pd
import psycopg
from IPython.display import display

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

pd.options.display.max_rows = 50
pd.options.display.max_colwidth = 200

_conn = None


def _read_env(path):
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


def _connection_error_hint(error):
    return (
        "НЕ УДАЛОСЬ ПОДКЛЮЧИТЬСЯ К БАЗЕ.\n"
        "Проверьте, что Docker запущен и база поднята: команда `docker compose ps`\n"
        "в папке репозитория должна показать hse-db-postgres в состоянии healthy.\n"
        f"Текст ошибки: {error}".rstrip()
    )


def _connect():
    global _conn
    if _conn is None or _conn.closed:
        env = _read_env(ENV_FILE)
        _conn = psycopg.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=os.environ.get("PGPORT") or env.get("POSTGRES_PORT", "5432"),
            dbname="demo",
            user=env["POSTGRES_USER"],
            password=env["POSTGRES_PASSWORD"],
            autocommit=True,
        )
    return _conn


BOOL_OID = 16


def _as_text_table(cur):
    """Значения — ровно в том виде, в каком их вывел PostgreSQL.

    Если отдать строки pandas как Python-объекты, он превратит NULL в NaN, целые
    рядом с NULL — в 5.0, а float4 округлит при выводе. Для семинара про типы и NULL
    это недопустимо, поэтому берём текстовое представление из ответа сервера.
    """
    res = cur.pgresult
    columns = [c.name for c in cur.description]
    is_bool = [c.type_code == BOOL_OID for c in cur.description]
    rows = []
    for r in range(res.ntuples):
        row = []
        for c in range(res.nfields):
            value = res.get_value(r, c)
            if value is None:
                row.append("NULL")
            elif is_bool[c]:
                row.append("true" if value == b"t" else "false")
            else:
                row.append(value.decode())
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def sql(line, cell):
    try:
        conn = _connect()
    except (psycopg.OperationalError, OSError) as e:
        print(_connection_error_hint(e))
        return

    try:
        cur = conn.cursor()
        cur.execute(cell)
    except psycopg.Error as e:
        print(f"ОШИБКА: {e}".rstrip())
        return

    table = None
    while True:
        if cur.description:
            table = _as_text_table(cur)
        elif cur.statusmessage:
            print(cur.statusmessage)
        if not cur.nextset():
            break

    if table is not None:
        display(table)
        print(f"Строк: {len(table)}")


def load_ipython_extension(ipython):
    ipython.register_magic_function(sql, magic_kind="cell")
