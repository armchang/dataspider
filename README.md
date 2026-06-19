# Dataspider

Dataspider is a Python data collector that downloads one-minute OHLCV (open, high, low, close, and volume) candles from the Binance public API and stores them through a dynamically loaded database adapter.

PostgreSQL and SQLite are currently supported. The active backend is selected entirely through environment variables, without changing the application code.

## How it works

When `_main.py` runs, it:

1. Loads the adapter selected by `DATABASE_TYPE`.
2. Initializes the database and creates the `ohclv` table when needed.
3. Builds an inclusive date list from `START_DATE` through `END_DATE`.
4. Requests one-minute Binance klines for each day in batches of up to 1,000 candles.
5. Inserts each day's candles using the selected database adapter.
6. Ignores a candle when its `open_time` already exists.

The current entry point collects `PAXGUSDT` candles from 1 March 2024 through 30 June 2024. These constants can be changed in `_main.py`. Binance's public endpoints are used, so no Binance API key is required.

## Requirements

- Python 3.11 or newer
- Python packages:
  - `pandas`
  - `requests`
  - `tqdm`
  - `psycopg[binary]` when using PostgreSQL
- PostgreSQL server and a role with database-creation permission when using PostgreSQL
- No separate database installation when using SQLite; Python includes its driver

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pandas requests tqdm "psycopg[binary]"
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pandas requests tqdm "psycopg[binary]"
```

The `psycopg` package may be omitted when the project will only use SQLite. macOS/Linux users with `pyenv` can alternatively run `setup/setup_venv.sh`.

## Database configuration

The connection layer uses only two backend-neutral variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_TYPE` | `postgresql` | Adapter module name, such as `postgresql` or `sqlite` |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/dataspider` | Backend connection URL |

The project reads environment variables directly. It does not automatically load `.env`, so export the values in your shell or use your preferred environment/process manager. Examples are also provided in `.env.example`.

### PostgreSQL

PowerShell:

```powershell
$env:DATABASE_TYPE = "postgresql"
$env:DATABASE_URL = "postgresql://postgres:your-password@localhost:5432/dataspider"
python _main.py
```

Bash:

```bash
export DATABASE_TYPE=postgresql
export DATABASE_URL=postgresql://postgres:your-password@localhost:5432/dataspider
python _main.py
```

The PostgreSQL adapter connects to the server's `postgres` maintenance database to create the target database from the URL when it does not exist.

### SQLite

PowerShell:

```powershell
$env:DATABASE_TYPE = "sqlite"
$env:DATABASE_URL = "sqlite:///datas/dataspider.db"
python _main.py
```

Bash:

```bash
export DATABASE_TYPE=sqlite
export DATABASE_URL=sqlite:///datas/dataspider.db
python _main.py
```

The SQLite adapter creates the parent folder, database file, and table when needed. For an in-memory database, use `sqlite:///:memory:`; note that its contents last only for the lifetime of a single SQLite connection.

## Switching databases

No Python changes are required to switch between the included backends. Set the matching type and URL before starting the application:

```text
PostgreSQL: DATABASE_TYPE=postgresql
            DATABASE_URL=postgresql://user:password@host:5432/database

SQLite:     DATABASE_TYPE=sqlite
            DATABASE_URL=sqlite:///path/to/database.db
```

Do not combine a PostgreSQL type with a SQLite URL, or vice versa.

## Running the project

Run the historical collector:

```bash
python _main.py
```

Create only the configured database/table:

```bash
python -c "from scripts.db.create_db import run; run()"
```

Print the five newest stored candles:

```bash
python -c "from scripts.db.read_db import run; run()"
```

## Database adapter architecture

`scripts/db/connection.py` passes `DATABASE_TYPE` and `DATABASE_URL` to `load_database()` in `scripts/db/database.py`. The loader imports the adapter dynamically from:

```text
scripts.db.backends.<DATABASE_TYPE>
```

For example:

- `DATABASE_TYPE=postgresql` loads `scripts/db/backends/postgresql.py`.
- `DATABASE_TYPE=sqlite` loads `scripts/db/backends/sqlite.py`.

Application-facing database modules call the adapter interface and contain no backend-specific drivers, placeholders, schema types, or upsert syntax.

To add another database backend:

1. Create `scripts/db/backends/<type>.py`.
2. Export a `Database` class derived from `DatabaseAdapter`.
3. Implement `connect`, `initialize`, `insert_ohlcv`, `insert_ohlcv_batch`, and `fetch_recent_ohlcv`.
4. Parse the generic `self.settings["url"]` value inside the adapter.
5. Install the backend's Python driver.
6. Set `DATABASE_TYPE=<type>` and provide its matching `DATABASE_URL`.

Unsupported database types fail immediately with an error naming the adapter module that must be added.

## Database schema

Each adapter creates the equivalent of this logical schema using its database-specific types:

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

The table is named `ohclv` in the current codebase rather than the more common spelling `ohlcv`.

## Project structure

```text
dataspider/
|-- _main.py                              # Historical collection entry point
|-- .env.example                          # PostgreSQL and SQLite examples
|-- .gitignore
|-- README.md
|-- config/
|   `-- config.py                         # Backend-neutral type and URL settings
|-- datas/                                # Local data files, including SQLite databases
|-- scripts/
|   |-- db/
|   |   |-- connection.py                 # Selects and exposes the active adapter
|   |   |-- database.py                   # Adapter contract and dynamic loader
|   |   |-- backends/
|   |   |   |-- __init__.py
|   |   |   |-- postgresql.py             # PostgreSQL connection and SQL behavior
|   |   |   `-- sqlite.py                 # SQLite connection and SQL behavior
|   |   |-- create_db.py                  # Initializes the active backend
|   |   |-- insert_price.py               # Inserts one candle through the adapter
|   |   |-- insert_price_batch.py         # Inserts candle batches through the adapter
|   |   `-- read_db.py                    # Displays the newest stored candles
|   |-- fetch/
|   |   |-- get_ohclv.py                  # Latest-candle polling helper
|   |   |-- get_ohclv_range.py            # Historical daily candle downloader
|   |   `-- get_price.py                  # Live ticker-price polling helper
|   `-- util/
|       `-- date_util.py                   # Inclusive date generator
`-- setup/
    `-- setup_venv.sh                     # pyenv/macOS/Linux environment setup
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

- Binance timestamps are converted with `datetime.fromtimestamp`, so values use the machine's local timezone and remain timezone-naive.
- `open_time` is the sole primary key. A candle for another trading pair with the same opening time is treated as a duplicate.
- Network errors from the historical range fetcher are not retried automatically.
- SQLite and PostgreSQL use different physical column types and SQL syntax, which remain isolated inside their respective adapters.
