import sqlite3
from pathlib import Path
from urllib.parse import unquote

from scripts.db.database import DatabaseAdapter


class Database(DatabaseAdapter):
    def __init__(self, settings):
        super().__init__(settings)
        self.database_path = self._database_path(settings["url"])

    def connect(self):
        return sqlite3.connect(self.database_path)

    def initialize(self):
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)

        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS ohclv (
                    open_time TIMESTAMP PRIMARY KEY,
                    close_time TIMESTAMP,
                    pair TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL
                )
            """)

    def insert_ohlcv(self, item):
        with self.connect() as connection:
            connection.execute(self._insert_query(), self._to_row(item))

    def insert_ohlcv_batch(self, items):
        rows = [self._to_row(item) for item in items]
        if not rows:
            return

        with self.connect() as connection:
            connection.executemany(self._insert_query(), rows)

    def fetch_recent_ohlcv(self, limit=5):
        with self.connect() as connection:
            cursor = connection.execute(
                "SELECT * FROM ohclv ORDER BY open_time DESC LIMIT ?",
                (limit,),
            )
            columns = [column[0] for column in cursor.description]
            return columns, cursor.fetchall()

    @staticmethod
    def _insert_query():
        return """
            INSERT INTO ohclv (open_time, close_time, pair, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

    @staticmethod
    def _database_path(database_url):
        prefix = "sqlite:///"
        if not database_url.startswith(prefix):
            raise ValueError("SQLite DATABASE_URL must use sqlite:///path or sqlite:///:memory:")

        database_path = unquote(database_url[len(prefix):])
        if not database_path:
            raise ValueError("SQLite DATABASE_URL must include a database path")
        return database_path
