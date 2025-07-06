import sqlite3
from config.config import DATABASE_PATH

def run(ohclv):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""INSERT OR IGNORE INTO ohclv (open_time, open, high, low, close, volume, close_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", (ohclv['open_time'], ohclv['open'], ohclv['high'], ohclv['low'], ohclv['close'], ohclv['volume'], ohclv['close_time']))
    
    conn.commit()
    conn.close()

    