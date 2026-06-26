import datetime
import threading
import traceback

from config.config import BASE_URL, SCAN_INTERVAL_SECONDS, SYMBOL
from scripts.fetch.get_ohclv import get_ohlcv


class CandleScanner:
    def __init__(self):
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._settings = {}
        self._last_run_at = None
        self._last_open_time = None
        self._last_error = None
        self._saved_rows = 0

    def start(
        self,
        symbol=SYMBOL,
        base_url=BASE_URL,
        interval="1m",
        scan_interval_seconds=SCAN_INTERVAL_SECONDS,
    ):
        symbol = symbol.strip().upper()
        if not symbol:
            raise ValueError("symbol cannot be empty")
        if scan_interval_seconds <= 0:
            raise ValueError("scan_interval_seconds must be greater than zero")

        with self._lock:
            if self._thread and self._thread.is_alive():
                return dict(self._status_unlocked(running=True))

            self._stop_event.clear()
            self._settings = {
                "symbol": symbol,
                "base_url": base_url,
                "interval": interval,
                "scan_interval_seconds": scan_interval_seconds,
            }
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            return dict(self._status_unlocked(running=True))

    def stop(self):
        with self._lock:
            thread = self._thread
            if not thread or not thread.is_alive():
                return self.status()
            self._stop_event.set()

        thread.join(timeout=5)
        return self.status()

    def status(self):
        with self._lock:
            running = bool(self._thread and self._thread.is_alive())
            return dict(self._status_unlocked(running=running))

    def _status_unlocked(self, running):
        return {
            "running": running,
            "settings": dict(self._settings),
            "last_run_at": self._format_datetime(self._last_run_at),
            "last_open_time": self._format_datetime(self._last_open_time),
            "last_error": self._last_error,
            "saved_rows": self._saved_rows,
        }

    def _run_loop(self):
        try:
            import scripts.db.create_db as create_db

            create_db.run()
            while not self._stop_event.is_set():
                self._scan_once()
                wait_seconds = self._settings["scan_interval_seconds"]
                self._stop_event.wait(wait_seconds)
        except Exception:
            with self._lock:
                self._last_error = traceback.format_exc()

    def _scan_once(self):
        settings = dict(self._settings)
        now = datetime.datetime.now()
        try:
            result = get_ohlcv(
                base_url=settings["base_url"],
                symbol=settings["symbol"],
                interval=settings["interval"],
                limit=1,
            )
        except Exception as error:
            with self._lock:
                self._last_run_at = now
                self._last_error = str(error)
            return

        import scripts.db.insert_price_batch as insert_price_batch

        insert_price_batch.run(result)
        with self._lock:
            self._last_run_at = now
            self._last_open_time = result["open_time"]
            self._last_error = None
            self._saved_rows += 1

    @staticmethod
    def _format_datetime(value):
        if value is None:
            return None
        return value.isoformat()


class ScannerManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._scanners = {}

    def start(
        self,
        symbol=SYMBOL,
        base_url=BASE_URL,
        interval="1m",
        scan_interval_seconds=SCAN_INTERVAL_SECONDS,
    ):
        symbol = symbol.strip().upper()
        with self._lock:
            pair_scanner = self._scanners.get(symbol)
            if pair_scanner is None:
                pair_scanner = CandleScanner()
                self._scanners[symbol] = pair_scanner

        return pair_scanner.start(
            symbol=symbol,
            base_url=base_url,
            interval=interval,
            scan_interval_seconds=scan_interval_seconds,
        )

    def stop(self, symbol=None):
        if symbol:
            symbol = symbol.strip().upper()
            with self._lock:
                pair_scanner = self._scanners.get(symbol)
            if pair_scanner is None:
                return {"running": False, "settings": {"symbol": symbol}}
            return pair_scanner.stop()

        with self._lock:
            scanners = list(self._scanners.items())
        return {pair: pair_scanner.stop() for pair, pair_scanner in scanners}

    def status(self, symbol=None):
        if symbol:
            symbol = symbol.strip().upper()
            with self._lock:
                pair_scanner = self._scanners.get(symbol)
            if pair_scanner is None:
                return {"running": False, "settings": {"symbol": symbol}}
            return pair_scanner.status()

        with self._lock:
            scanners = list(self._scanners.items())
        return {pair: pair_scanner.status() for pair, pair_scanner in scanners}


scanner = ScannerManager()
