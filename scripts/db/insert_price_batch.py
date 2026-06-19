from scripts.db.connection import database

def run(items):
    if isinstance(items, dict):
        items = [items]

    database.insert_ohlcv_batch(items)

    
