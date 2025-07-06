import datetime
import requests
import time

BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 1000  # Binance max per request

def get_ohlcv_for_day(symbol, date):
    start_dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    end_dt = start_dt + datetime.timedelta(days=1)
    
    start_ts = int(start_dt.timestamp() * 1000)
    end_ts = int(end_dt.timestamp() * 1000)

    all_data = []

    while start_ts < end_ts:
        url = (
            f"{BASE_URL}?symbol={symbol}&interval={INTERVAL}"
            f"&startTime={start_ts}&endTime={end_ts}&limit={LIMIT}"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        for ohlcv in data:
            all_data.append({
                "open_time": datetime.datetime.fromtimestamp(ohlcv[0] / 1000),
                "open": float(ohlcv[1]),
                "high": float(ohlcv[2]),
                "low": float(ohlcv[3]),
                "close": float(ohlcv[4]),
                "volume": float(ohlcv[5]),
                "close_time": datetime.datetime.fromtimestamp(ohlcv[6] / 1000)
            })

        start_ts = data[-1][0] + 1  # Move to next candle

        time.sleep(0.5)  # Be nice to the API

    return all_data

def get_ohlcv_range(symbol, start_date, end_date):
    current = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    while current < end:
        date_str = current.strftime("%Y-%m-%d")
        print(f"Fetching data for {date_str}...")
        daily_data = get_ohlcv_for_day(symbol, date_str)

        # You can save to file/db here instead
        for item in daily_data:
            print(item)

        current += datetime.timedelta(days=1)
        time.sleep(1)  # Avoid rate limits

