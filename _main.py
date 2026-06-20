import argparse
from datetime import datetime

from tqdm import tqdm

from config.config import BASE_URL, END_DATE, START_DATE, SYMBOL
import scripts.db.create_db as create_db
import scripts.db.insert_price_batch as insert_price_batch
import scripts.fetch.get_ohclv_range as get_ohlcv_range
from scripts.util import date_util


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected YYYY-MM-DD."
        ) from error


def run(symbol=SYMBOL, start_date=START_DATE, end_date=END_DATE, base_url=BASE_URL):
    """Download and store Binance candles using explicit or configured values."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("symbol cannot be empty")
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")

    create_db.run()
    dates = list(date_util.date_range(start_date, end_date))
    fetched_rows = 0

    for day in tqdm(dates, desc=f"Saving {symbol} data"):
        data = get_ohlcv_range.get_ohlcv_range(
            symbol=symbol,
            start_date=day,
            end_date=day,
            base_url=base_url,
        )
        insert_price_batch.run(data)
        fetched_rows += len(data)

    return fetched_rows


def build_parser():
    parser = argparse.ArgumentParser(
        description="Download Binance OHLCV candles into the configured database."
    )
    parser.add_argument("--symbol", default=SYMBOL, help=f"Trading pair (default: {SYMBOL})")
    parser.add_argument(
        "--start-date",
        type=parse_date,
        default=START_DATE,
        metavar="YYYY-MM-DD",
        help=f"First date to download (default: {START_DATE:%Y-%m-%d})",
    )
    parser.add_argument(
        "--end-date",
        type=parse_date,
        default=END_DATE,
        metavar="YYYY-MM-DD",
        help=f"Last date to download (default: {END_DATE:%Y-%m-%d})",
    )
    parser.add_argument("--base-url", default=BASE_URL, help="Binance klines endpoint")
    return parser


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    total = run(
        symbol=arguments.symbol,
        start_date=arguments.start_date,
        end_date=arguments.end_date,
        base_url=arguments.base_url,
    )
    print(f"Fetched {total} candle rows for {arguments.symbol.upper()}.")
