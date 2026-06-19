from psycopg import sql

from config.config import POSTGRES_DB, POSTGRES_MAINTENANCE_DB
from scripts.db.connection import get_connection

def run():
    # CREATE DATABASE cannot run inside a transaction.
    with get_connection(POSTGRES_MAINTENANCE_DB, autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES_DB,))
            if cursor.fetchone() is None:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(POSTGRES_DB)))

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ohclv (
                    open_time TIMESTAMP PRIMARY KEY,
                    close_time TIMESTAMP,
                    pair TEXT,
                    open DOUBLE PRECISION,
                    high DOUBLE PRECISION,
                    low DOUBLE PRECISION,
                    close DOUBLE PRECISION,
                    volume DOUBLE PRECISION
                )
            """)
