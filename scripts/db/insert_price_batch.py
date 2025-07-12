import sqlite3
from config.config import DATABASE_PATH

def run(list):
    if isinstance(list, dict):
        list = [list]
    
    with sqlite3.connect(DATABASE_PATH, timeout=120) as conn:
        cursor = conn.cursor()
        cursor.executemany("""INSERT OR IGNORE INTO ohclv (open_time, close_time, pair, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", [
                (item['open_time'].strftime("%Y-%m-%d %H:%M:%S"), 
                 item['close_time'].strftime("%Y-%m-%d %H:%M:%S"), 
                 item['pair'], 
                 item['open'], 
                 item['high'], 
                 item['low'], 
                 item['close'], 
                 item['volume']) for item in list])
        conn.commit()

    