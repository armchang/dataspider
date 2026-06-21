import datetime
import time
import requests

BASE_URL = "https://api.binance.com/api/v3/klines"
INTERVAL = "1m"
LIMIT = 1000  # Binance max per request
REQUEST_TIMEOUT = 30


def _coerce_date(value):
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.min)
    if isinstance(value, str):
        return datetime.datetime.strptime(value, "%Y-%m-%d")
    raise TypeError("date value must be a datetime, date, or YYYY-MM-DD string")


def _to_utc_milliseconds(value):
    return int(value.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)


def _from_utc_milliseconds(value):
    return datetime.datetime.fromtimestamp(
        value / 1000,
        tz=datetime.timezone.utc,
    ).replace(tzinfo=None)


def get_ohlcv_for_day(symbol, date, base_url=BASE_URL):
    start_dt = _coerce_date(date)
    end_dt = start_dt + datetime.timedelta(days=1)

    start_ts = _to_utc_milliseconds(start_dt)
    end_ts = _to_utc_milliseconds(end_dt)
    rows = []

    while start_ts < end_ts:
        response = requests.get(
            base_url,
            params={
                "symbol": symbol,
                "interval": INTERVAL,
                "startTime": start_ts,
                "endTime": end_ts,
                "limit": LIMIT,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        candles = response.json()

        if not candles:
            break

        for candle in candles:
            open_time = _from_utc_milliseconds(candle[0])
            if open_time >= end_dt:
                break

            rows.append({
                "open_time": open_time,
                "close_time": _from_utc_milliseconds(candle[6]),
                "pair": symbol,
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
            })

        start_ts = candles[-1][0] + 1
        time.sleep(0.5)

    return rows


def get_ohlcv_range(symbol, start_date, end_date, base_url=BASE_URL):
    current = _coerce_date(start_date)
    end = _coerce_date(end_date)
    if end < current:
        raise ValueError("end_date must be on or after start_date")

    rows = []
    while current <= end:
        rows.extend(get_ohlcv_for_day(symbol, current, base_url=base_url))
        current += datetime.timedelta(days=1)
        time.sleep(1)

    return rows
