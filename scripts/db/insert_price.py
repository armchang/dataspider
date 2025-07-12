import sqlite3
from config.config import DATABASE_PATH

def run(ohclv):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""INSERT OR IGNORE INTO ohclv (open_time, close_time, pair, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (ohclv['open_time'], ohclv['close_time'], ohclv['pair'], ohclv['open'], ohclv['high'], ohclv['low'], ohclv['close'], ohclv['volume']))
    
    conn.commit()
    conn.close()

    