import datetime
import time

import requests

BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
REQUEST_TIMEOUT = 30

def get_ohlcv(base_url=BASE_URL, symbol="BTCUSDT", interval="1m", limit=1):
    response = requests.get(
        base_url,
        params={
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        },
        timeout=REQUEST_TIMEOUT,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        raise RuntimeError(
            f"Binance OHLCV request failed with HTTP {response.status_code}: "
            f"{response.text}"
        ) from error

    data = response.json()

    if not data or not isinstance(data, list):
        raise RuntimeError(f"Unexpected Binance OHLCV response: {data}")

    ohlcv = data[-1]  # Get the most recent candle
    return {
        "open_time": datetime.datetime.fromtimestamp(ohlcv[0] / 1000),
        "pair": symbol,
        "open": float(ohlcv[1]),
        "high": float(ohlcv[2]),
        "low": float(ohlcv[3]),
        "close": float(ohlcv[4]),
        "volume": float(ohlcv[5]),
        "close_time": datetime.datetime.fromtimestamp(ohlcv[6] / 1000)
    }
    
def run(base_url=BASE_URL, symbol=SYMBOL, interval="1m", limit=1):
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            result = get_ohlcv(base_url=base_url, symbol=symbol, interval=interval, limit=limit)
            print(f"[{now}] {symbol} - Open: {result['open']}, High: {result['high']}, Low: {result['low']}, Close: {result['close']}, Volume: {result['volume']}")
        except Exception as error:
            print(f"[{now}] Failed to retrieve {symbol} HLCV: {error}")
        time.sleep(15)
