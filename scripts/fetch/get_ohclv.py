import datetime
import requests
import time

BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"

def get_ohlcv(base_url=BASE_URL, symbol="BTCUSDT", interval="1m", limit=1):
    try:
        url = f"{base_url}?symbol={symbol}&interval={interval}&limit={limit}"
        #print(f"Requesting URL: {url}")  # Debug output
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if status is not 200
        data = response.json()

        if not data or not isinstance(data, list):
            print("Unexpected response format:", data)
            return None

        ohlcv = data[-1]  # Get the most recent candle
        return {
            "open_time": datetime.datetime.fromtimestamp(ohlcv[0] / 1000),
            "open": float(ohlcv[1]),
            "high": float(ohlcv[2]),
            "low": float(ohlcv[3]),
            "close": float(ohlcv[4]),
            "volume": float(ohlcv[5]),
            "close_time": datetime.datetime.fromtimestamp(ohlcv[6] / 1000)
        }

    except Exception as e:
        print("Error getting OHLCV:", e)
        return None
    
def run(base_url=BASE_URL, symbol=SYMBOL, interval="1m", limit=1):
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = get_ohlcv(base_url=base_url, symbol=symbol, interval=interval, limit=limit)
        if result:
            print(f"[{now}] {symbol} - Open: {result['open']}, High: {result['high']}, Low: {result['low']}, Close: {result['close']}, Volume: {result['volume']}")
        else:
            print(f"[{now}] Failed to retrieve {symbol} HLCV.")
        time.sleep(15)