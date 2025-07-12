import requests
import time
from datetime import datetime
import scripts.fetch.get_price as get_price  # Assuming get_price.py is in the same directory
import scripts.fetch.get_ohclv as get_ohclv  # Assuming ohclv.py is in the same directory
import scripts.fetch.get_ohclv_range as get_ohlcv_range  # Assuming get_ohclv_range.py is in the same directory
import scripts.db.create_db as create_db  # Assuming create_db.py is in the same directory
import scripts.db.read_db as read_db  # Assuming read_db.py is in the same directory  
import scripts.db.insert_price as insert_price  # Assuming insert_price.py is in the same directory
import scripts.db.insert_price_batch as insert_price_batch
from scripts.util import date_util  # Assuming insert_price_batch.py is in the same directory

# Simple Crypto Price Tracker Bot

# Global variables
BASE_URL = "https://api.binance.com/api/v3/ticker/price"
SYMBOL = "ETHUSDT"
START_DATE = datetime.strptime("2024-07-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2024-07-02", "%Y-%m-%d")

if __name__ == "__main__":
    #data = get_ohlcv_range.get_ohlcv_range(SYMBOL, START_DATE, END_DATE)
    #print(data)
    # Create the database if it doesn't exist
    create_db.run()

    for day in date_util.date_range(START_DATE, END_DATE):
        print(f"📅 Fetching from {day}...")
        # Make sure your get_ohlcv_range can handle datetime input or convert to string
        data = get_ohlcv_range.get_ohlcv_range(
            symbol=SYMBOL,
            start_date=day,
            end_date=day
        )
        # Save data to the database
        print(f"💾 Saving {len(data)} OHLCV records for {SYMBOL} to database...")
        insert_price_batch.run(data)
        print(f"✅ Done saving {SYMBOL} data to DB.\n")
