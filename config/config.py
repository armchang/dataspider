import os
from datetime import datetime


# Binance collection settings.
BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "PAXGUSDT"
START_DATE = datetime.strptime("2026-01-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2026-06-21", "%Y-%m-%d")

# connection.py passes these backend-neutral values to database.py.
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql").lower()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:PASSWORD@localhost:5433/dataspider",
)

