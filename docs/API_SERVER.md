# API Server

This document covers `scripts/api_server.py`.

The API server is the HTTP wrapper for Dataspider. It keeps a long-running process alive, listens for HTTP requests, and forwards scanner-related requests to `scripts/scanner.py`.

It does not fetch candles by itself. Candle fetching, database inserts, scanner status, and scanner stop/start behavior are handled by the scanner module.

For scanner controls, see `docs/SCANNER.md`.

## What the API server does

| Responsibility | Owner |
| --- | --- |
| Opens a local HTTP server | `api_server.py` |
| Reads host and port settings | `api_server.py` |
| Parses JSON request bodies | `api_server.py` |
| Returns JSON responses | `api_server.py` |
| Starts, stops, or checks scanners | `scanner.py`, called by `api_server.py` |
| Fetches Binance candles | `scanner.py` |
| Saves candles to the database | `scanner.py` through DB modules |

## Start the API server

Run from the project root:

```bash
python3 -m scripts.api_server
```

By default, the server listens on:

```text
http://127.0.0.1:8000
```

The command stays running because the API server must remain alive while other terminals or programs send requests to it.

## Override host or port

Use command-line arguments:

```bash
python3 -m scripts.api_server --host 127.0.0.1 --port 8001
```

Or use environment variables:

```bash
DATASPIDER_API_PORT=8001 python3 -m scripts.api_server
```

That environment-variable form only applies `DATASPIDER_API_PORT=8001` to that one command.

## Configuration

These API server settings are read from `config/config.py`.

| Setting | Environment variable | Default | Purpose |
| --- | --- | --- | --- |
| `API_HOST` | `DATASPIDER_API_HOST` | `127.0.0.1` | API bind host |
| `API_PORT` | `DATASPIDER_API_PORT` | `8000` | API bind port |

Scanner settings such as `SYMBOL`, `BASE_URL`, and `SCAN_INTERVAL_SECONDS` are used by `scripts/scanner.py`. They are documented in `docs/SCANNER.md`.

Database settings still come from `DATABASE_TYPE` and `DATABASE_URL`. The API server can start without connecting to the database, but a scanner will need a working database setup when it starts saving candles.

## Health check

Use the health endpoint to confirm that the API server itself is running:

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{
  "ok": true
}
```

This only proves the HTTP server is alive. It does not prove that a scanner is running or that the database is connected.

## Routes exposed by the server

The API server currently exposes these routes:

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check whether the HTTP server is alive |
| `POST` | `/scanner/start` | Forward a start request to the scanner manager |
| `GET` | `/scanner/status` | Forward a status request to the scanner manager |
| `POST` | `/scanner/stop` | Forward a stop request to the scanner manager |

The `/scanner/...` routes are documented in `docs/SCANNER.md` because they control scanner behavior.

## Running multiple API servers

Run each API server process on a different port:

```bash
DATASPIDER_API_PORT=8001 python3 -m scripts.api_server
DATASPIDER_API_PORT=8002 python3 -m scripts.api_server
```

Use separate API server processes when you want separate ports, separate process lifetimes, or separate database environment variables.
