import requests
import time
import datetime

BASE_URL = "https://api.binance.com/api/v3/ticker/price"
SYMBOL = "ETHUSDT"

def get_price(base_url=BASE_URL, symbol=SYMBOL):
    try:
        url = f"{base_url}?symbol={symbol}"
        response = requests.get(url)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print("Error getting price:", e)
        return None
    
def run(base_url=BASE_URL, symbol=SYMBOL):
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        price = get_price(base_url=base_url, symbol=symbol)
        if price:
            print(f"[{now}] {symbol} Price: {price}")
            # Add your logic here: alerts, trade, log, etc.
        else:
            print(f"[{now}] Failed to retrieve price.")
        time.sleep(15)