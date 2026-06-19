import pandas as pd
from scripts.db.connection import database

def run():
    columns, rows = database.fetch_recent_ohlcv(limit=5)
    df = pd.DataFrame(rows, columns=columns)
    print(df.head())

