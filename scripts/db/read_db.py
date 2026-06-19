import pandas as pd
from scripts.db.connection import get_connection

def run():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM ohclv ORDER BY open_time DESC", conn)

    print(df.head())

