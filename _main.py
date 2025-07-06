import requests
import time
import datetime
import scripts.fetch.get_price as get_price  # Assuming get_price.py is in the same directory
import scripts.fetch.get_ohclv as get_ohclv  # Assuming ohclv.py is in the same directory
import scripts.db.create_db as create_db  # Assuming create_db.py is in the same directory
import scripts.db.read_db as read_db  # Assuming read_db.py is in the same directory  
import scripts.db.insert_price as insert_price  # Assuming insert_price.py is in the same directory

# Simple Crypto Price Tracker Bot

# Global variables
BASE_URL = "https://api.binance.com/api/v3/ticker/price"
SYMBOL = "ETHUSDT"
    
if __name__ == "__main__":
    #get_ohclv.run_bot(symbol=SYMBOL)
    #create_db.run()  # Create the database and table if not exists
    #read_db.run()  # Read and display the OHLCV data
    while True:
        ohclv = get_ohclv.get_ohlcv(symbol=SYMBOL)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if ohclv:
            print(f"[{now}] {SYMBOL} - Open: {ohclv['open']}, High: {ohclv['high']}, Low: {ohclv['low']}, Close: {ohclv['close']}, Volume: {ohclv['volume']}")
        else:
            print(f"[{now}] Failed to retrieve {SYMBOL} HLCV.")
        insert_price.run(ohclv)
        time.sleep(15)  # Sleep for 15 seconds before the next iteration