import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from scripts.db.database import DatabaseAdapter


class Database(DatabaseAdapter):
    def connect(self):
        return psycopg.connect(self.settings["url"])

    def initialize(self):
        database_url = self.settings["url"]
        connection_settings = conninfo_to_dict(database_url)
        database_name = connection_settings.get("dbname")
        if not database_name:
            raise ValueError("The PostgreSQL DATABASE_URL must include a database name")

        maintenance_url = make_conninfo(database_url, dbname="postgres")
        with psycopg.connect(maintenance_url, autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
                    )

        with self.connect() as connection:
            with connection.cursor() as cursor:
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

    def insert_ohlcv(self, item):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(self._insert_query(), self._to_row(item))

    def insert_ohlcv_batch(self, items):
        rows = [self._to_row(item) for item in items]
        if not rows:
            return

        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(self._insert_query(), rows)

    def fetch_recent_ohlcv(self, limit=5):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM ohclv ORDER BY open_time DESC LIMIT %s",
                    (limit,),
                )
                columns = [column.name for column in cursor.description]
                return columns, cursor.fetchall()

    @staticmethod
    def _insert_query():
        return """
            INSERT INTO ohclv (open_time, close_time, pair, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (open_time) DO NOTHING
        """

    @staticmethod
    def _to_row(item):
        return (
            item["open_time"],
            item["close_time"],
            item["pair"],
            item["open"],
            item["high"],
            item["low"],
            item["close"],
            item["volume"],
        )
