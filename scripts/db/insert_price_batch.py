from scripts.db.connection import get_connection

def run(items):
    if isinstance(items, dict):
        items = [items]

    rows = [
                (item['open_time'],
                 item['close_time'],
                 item['pair'], 
                 item['open'], 
                 item['high'], 
                 item['low'], 
                 item['close'], 
                 item['volume']) for item in items]
    if not rows:
        return

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO ohclv (open_time, close_time, pair, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (open_time) DO NOTHING
            """, rows)

    
