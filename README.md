# Dataspider

Dataspider is a small Python data collector that downloads one-minute OHLCV (open, high, low, close, and volume) candles from the Binance public API and stores them in PostgreSQL.

The current entry point is configured to collect historical `PAXGUSDT` candles from 1 March 2024 through 30 June 2024. These values are constants near the top of `_main.py` and can be changed before running the collector.

## How it works

When `_main.py` runs, it:

1. Creates the configured PostgreSQL database if it does not exist.
2. Creates the `ohclv` table if it does not exist.
3. Builds an inclusive list of dates between `START_DATE` and `END_DATE`.
4. Requests one-minute Binance klines for each day, in batches of up to 1,000 candles.
5. Inserts each day's candles into PostgreSQL as a batch.
6. Ignores a candle when its `open_time` already exists.

The Binance endpoints used by the project are public, so no Binance API key is required.

## Requirements

- Python 3.11
- PostgreSQL
- A PostgreSQL role that can connect to the server and create the configured database
- Python packages:
  - `pandas`
  - `psycopg[binary]`
  - `requests`
  - `tqdm`

## PostgreSQL configuration

Database settings are read from environment variables. The defaults are:

| Variable | Default | Purpose |
| --- | --- | --- |
| `POSTGRES_HOST` | `localhost` | PostgreSQL server host |
| `POSTGRES_PORT` | `5432` | PostgreSQL server port |
| `POSTGRES_DB` | `dataspider` | Application database |
| `POSTGRES_USER` | `postgres` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_MAINTENANCE_DB` | `postgres` | Existing database used while creating the application database |
| `DATABASE_URL` | unset | Optional PostgreSQL connection string; takes precedence for normal connections |

An example is provided in `.env.example`. The application does not load `.env` files itself, so export the variables in your shell or load them with your preferred environment/process manager.

PowerShell example:

```powershell
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_DB = "dataspider"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "your-password"
$env:POSTGRES_MAINTENANCE_DB = "postgres"
```

Bash example:

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=dataspider
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your-password
export POSTGRES_MAINTENANCE_DB=postgres
```

Alternatively:

```bash
export DATABASE_URL=postgresql://postgres:your-password@localhost:5432/dataspider
```

## Installation

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pandas requests tqdm "psycopg[binary]"
```

On Windows PowerShell, activate the environment with:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pandas requests tqdm "psycopg[binary]"
```

macOS/Linux users with `pyenv` can also run `setup/setup_venv.sh`. That script installs Python 3.11.0, recreates `venv`, and installs the required packages.

## Running the collector

Make sure PostgreSQL is running and the environment variables are set, then run:

```bash
python _main.py
```

The progress bar advances one day at a time. The initial database setup is idempotent, and repeated candle inserts are ignored based on the `open_time` primary key.

To create only the database and table:

```bash
python -c "from scripts.db.create_db import run; run()"
```

To print the five newest stored candles:

```bash
python -c "from scripts.db.read_db import run; run()"
```

## Database schema

The project creates this table:

```sql
CREATE TABLE IF NOT EXISTS ohclv (
    open_time TIMESTAMP PRIMARY KEY,
    close_time TIMESTAMP,
    pair TEXT,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION
);
```

The table is named `ohclv` in the current codebase (rather than the more common spelling `ohlcv`).

## Project structure

```text
dataspider/
|-- _main.py                         # Historical collection entry point
|-- config/
|   `-- config.py                    # PostgreSQL environment settings
|-- scripts/
|   |-- db/
|   |   |-- connection.py            # Shared PostgreSQL connection helper
|   |   |-- create_db.py             # Database and table initialization
|   |   |-- insert_price.py          # Single-candle insert
|   |   |-- insert_price_batch.py    # Batch candle insert
|   |   `-- read_db.py               # Displays the newest stored rows
|   |-- fetch/
|   |   |-- get_ohclv.py             # Latest-candle polling helper
|   |   |-- get_ohclv_range.py       # Historical daily candle downloader
|   |   `-- get_price.py             # Live ticker-price polling helper
|   `-- util/
|       `-- date_util.py              # Inclusive date generator
|-- setup/
|   `-- setup_venv.sh                # pyenv/macOS/Linux environment setup
`-- .env.example                     # Example PostgreSQL settings
```

## Adjusting the collection

Edit these constants in `_main.py`:

```python
SYMBOL = "PAXGUSDT"
START_DATE = datetime.strptime("2024-03-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2024-06-30", "%Y-%m-%d")
```

Historical downloads use Binance's `1m` interval. The fetcher pauses between requests to reduce the likelihood of hitting API rate limits.

## Notes

- Binance timestamps are converted with `datetime.fromtimestamp`, so stored values use the machine's local timezone and are written to PostgreSQL as timezone-naive `TIMESTAMP` values.
- `open_time` is the sole primary key. A candle for another trading pair with the same opening time will therefore be treated as a duplicate.
- Network errors from the historical range fetcher are not retried automatically.
