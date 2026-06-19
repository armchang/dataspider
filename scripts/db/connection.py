import psycopg
from psycopg.conninfo import make_conninfo

from config.config import (
    DATABASE_URL,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


def get_connection(database=None, *, autocommit=False):
    """Return a PostgreSQL connection using environment-backed settings."""
    if DATABASE_URL:
        conninfo = make_conninfo(DATABASE_URL, dbname=database) if database else DATABASE_URL
        return psycopg.connect(conninfo, autocommit=autocommit)

    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=database or POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        autocommit=autocommit,
    )
