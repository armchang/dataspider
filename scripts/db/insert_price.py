from scripts.db.connection import database

def run(ohclv):
    database.insert_ohlcv(ohclv)

    
