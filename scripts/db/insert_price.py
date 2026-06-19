from scripts.db.connection import get_connection

def run(ohclv):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ohclv (open_time, close_time, pair, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (open_time) DO NOTHING
            """, (
                ohclv['open_time'], ohclv['close_time'], ohclv['pair'], ohclv['open'],
                ohclv['high'], ohclv['low'], ohclv['close'], ohclv['volume'],
            ))

    
