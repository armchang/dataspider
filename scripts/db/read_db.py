import pandas as pd
import sqlite3
from config.config import DATABASE_PATH

#open -a "DB Browser for SQLite"

def run():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Create a DataFrame from the OHLCV table
    df = pd.read_sql_query("SELECT * FROM ohclv ORDER BY open_time DESC", conn)
    
    # Display the most recent OHLCV data
    print(df.head())
    
    # Close the database connection
    conn.close()

