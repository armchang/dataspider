# Scanner

This document covers the scanner classes and methods in `scripts/scanner.py`.

The scanner fetches the latest Binance OHLCV candle for one trading pair and stores it in the configured database. It scans immediately after it starts, then waits `scan_interval_seconds` before each next scan.

The scanner can be controlled two ways:

- Through HTTP routes exposed by `scripts/api_server.py`.
- Directly from Python by importing `scanner` from `scripts.scanner`.

## Configuration

These scanner settings are read from `config/config.py`.

| Setting                 | Environment variable    | Default            | Purpose                     |
| ----------------------- | ----------------------- | ------------------ | --------------------------- |
| `SCAN_INTERVAL_SECONDS` | `SCAN_INTERVAL_SECONDS` | `60`               | Default delay between scans |
| `SYMBOL`                | none                    | `BTCUSDT`          | Default trading pair        |
| `BASE_URL`              | none                    | Binance klines URL | Binance OHLCV endpoint      |

Database settings still come from `DATABASE_TYPE` and `DATABASE_URL`.

## HTTP control through the API server

Start the API server first:

```bash
python3 -m scripts.api_server
```

Then use these routes from another terminal or another application.

### `POST /scanner/start`

Starts a scanner. If no body is provided, it starts the configured default pair (BTCUSDT).

```bash
curl -X POST http://127.0.0.1:8000/scanner/start
```

Start a specific pair:

```bash
curl -X POST http://127.0.0.1:8000/scanner/start \
  -H "Content-Type: application/json" \
  -d '{"symbol":"ETHUSDT"}'
```

Start a pair with a custom scan interval:

```bash
curl -X POST http://127.0.0.1:8000/scanner/start \
  -H "Content-Type: application/json" \
  -d '{"symbol":"ETHUSDT","scan_interval_seconds":60}'
```

Accepted JSON fields:

| Field                   | Default                 | Purpose                                 |
| ----------------------- | ----------------------- | --------------------------------------- |
| `symbol`                | `SYMBOL`                | Trading pair to scan, such as `BTCUSDT` |
| `base_url`              | `BASE_URL`              | Binance klines endpoint                 |
| `interval`              | `1m`                    | Binance candle interval                 |
| `scan_interval_seconds` | `SCAN_INTERVAL_SECONDS` | Seconds to wait between scans           |

Response:

```json
{
  "running": true,
  "settings": {
    "symbol": "ETHUSDT",
    "base_url": "https://api.binance.com/api/v3/klines",
    "interval": "1m",
    "scan_interval_seconds": 60
  },
  "last_run_at": null,
  "last_open_time": null,
  "last_error": null,
  "saved_rows": 0
}
```

### `GET /scanner/status`

Shows every scanner known to the API process.

```bash
curl http://127.0.0.1:8000/scanner/status
```

Response:

```json
{
  "BTCUSDT": {
    "running": true,
    "settings": {
      "symbol": "BTCUSDT",
      "base_url": "https://api.binance.com/api/v3/klines",
      "interval": "1m",
      "scan_interval_seconds": 60
    },
    "last_run_at": "2026-06-24T12:00:00.000000",
    "last_open_time": "2026-06-24T11:59:00",
    "last_error": null,
    "saved_rows": 3
  }
}
```

Check one pair only:

```bash
curl "http://127.0.0.1:8000/scanner/status?symbol=ETHUSDT"
```

### `POST /scanner/stop`

Stops all scanners managed by this API process.

```bash
curl -X POST http://127.0.0.1:8000/scanner/stop
```

Stop one pair only:

```bash
curl -X POST http://127.0.0.1:8000/scanner/stop \
  -H "Content-Type: application/json" \
  -d '{"symbol":"ETHUSDT"}'
```

You can also pass the pair as a query parameter:

```bash
curl -X POST "http://127.0.0.1:8000/scanner/stop?symbol=ETHUSDT"
```

## Python API

Most code should use the module-level manager:

```python
from scripts.scanner import scanner
```

The manager keeps one `CandleScanner` per trading pair inside the current Python process.

## `scanner.start(...)`

Starts one scanner for a trading pair.

```python
scanner.start(
    symbol="BTCUSDT",
    base_url="https://api.binance.com/api/v3/klines",
    interval="1m",
    scan_interval_seconds=60,
)
```

Arguments:

| Argument                | Default                                         | Purpose                       |
| ----------------------- | ----------------------------------------------- | ----------------------------- |
| `symbol`                | `SYMBOL` from `config/config.py`                | Trading pair to scan          |
| `base_url`              | `BASE_URL` from `config/config.py`              | Binance klines endpoint       |
| `interval`              | `1m`                                            | Binance candle interval       |
| `scan_interval_seconds` | `SCAN_INTERVAL_SECONDS` from `config/config.py` | Seconds to wait between scans |

Returns a status dictionary:

```json
{
  "running": true,
  "settings": {
    "symbol": "BTCUSDT",
    "base_url": "https://api.binance.com/api/v3/klines",
    "interval": "1m",
    "scan_interval_seconds": 60
  },
  "last_run_at": null,
  "last_open_time": null,
  "last_error": null,
  "saved_rows": 0
}
```

If a scanner for the pair is already running, `start(...)` returns its current status instead of starting a duplicate worker.

## `scanner.status(symbol=None)`

Returns scanner status.

```python
scanner.status()
scanner.status(symbol="BTCUSDT")
```

When `symbol` is omitted, the result is a dictionary keyed by pair:

```json
{
  "BTCUSDT": {
    "running": true,
    "settings": {
      "symbol": "BTCUSDT",
      "base_url": "https://api.binance.com/api/v3/klines",
      "interval": "1m",
      "scan_interval_seconds": 60
    },
    "last_run_at": "2026-06-24T12:00:00.000000",
    "last_open_time": "2026-06-24T11:59:00",
    "last_error": null,
    "saved_rows": 3
  }
}
```

When `symbol` is provided, the result is only that pair's status.

## `scanner.stop(symbol=None)`

Stops scanner threads.

```python
scanner.stop()
scanner.stop(symbol="BTCUSDT")
```

When `symbol` is omitted, every scanner managed by this process is stopped. When `symbol` is provided, only that pair is stopped.

`stop(...)` returns status after the stop request. Each scanner waits up to 5 seconds for its background thread to exit.

## `CandleScanner`

Controls one background scanner thread for one trading pair.

Main methods:

| Method       | Purpose                                                                                           |
| ------------ | ------------------------------------------------------------------------------------------------- |
| `start(...)` | Starts the scanner thread                                                                         |
| `stop()`     | Requests the thread to stop and waits up to 5 seconds                                             |
| `status()`   | Returns running state, settings, last run time, last candle time, last error, and saved row count |

Most code should use `ScannerManager` instead of constructing `CandleScanner` directly.

## `ScannerManager`

Keeps one `CandleScanner` per pair inside the current Python process.

Main methods:

| Method                | Purpose                                                             |
| --------------------- | ------------------------------------------------------------------- |
| `start(...)`          | Creates or reuses the scanner for a pair and starts it              |
| `stop(symbol=None)`   | Stops one pair, or all pairs when `symbol` is omitted               |
| `status(symbol=None)` | Returns one pair's status, or all statuses when `symbol` is omitted |

## Running multiple pairs in one process

Start one scanner per pair:

```python
from scripts.scanner import scanner

scanner.start(symbol="BTCUSDT")
scanner.start(symbol="ETHUSDT")
```

Or through the API server:

```bash
curl -X POST http://127.0.0.1:8000/scanner/start \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT"}'

curl -X POST http://127.0.0.1:8000/scanner/start \
  -H "Content-Type: application/json" \
  -d '{"symbol":"ETHUSDT"}'
```

Use this when you want one controller process managing many pairs.

## Notes

- `last_error` contains the most recent worker error. For example, missing database dependencies or connection failures appear there.
- The database table should use `(pair, open_time)` as the uniqueness key so multiple pairs can store candles for the same minute.
- The scanner imports the database modules lazily when the worker starts, so the API server can still import even if the database dependency is not ready yet.
