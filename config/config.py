import os
from datetime import datetime


# Binance collection settings.
BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))
API_HOST = os.getenv("DATASPIDER_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("DATASPIDER_API_PORT", "8000"))
START_DATE = datetime.strptime("2026-06-24", "%Y-%m-%d")
END_DATE = datetime.strptime("2026-06-25", "%Y-%m-%d")

# connection.py passes these backend-neutral values to database.py.
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql").lower()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:genius1019@localhost:5433/dataspider",
)
