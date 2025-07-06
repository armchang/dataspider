import sqlite3
from config.config import DATABASE_PATH

def run():
    # Connect to or create the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ohclv (
        open_time TEXT PRIMARY KEY,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        close_time TEXT
    )
    ''')

    # Example data to insert
    cursor.execute("""
    INSERT OR IGNORE INTO ohclv (open_time, open, high, low, close, volume, close_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("2024-06-22 12:00:00", 35000, 35500, 34800, 35300, 23.5, "2024-06-22 12:01:00"))

    conn.commit()
    conn.close()