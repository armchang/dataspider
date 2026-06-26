import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from config.config import API_HOST, API_PORT, BASE_URL, SCAN_INTERVAL_SECONDS, SYMBOL
from scripts.scanner import scanner


class DataspiderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path_only == "/health":
            self._write_json({"ok": True})
            return
        if self.path_only == "/scanner/status":
            payload = self._query_params()
            self._write_json(scanner.status(symbol=payload.get("symbol")))
            return
        self._write_json({"error": "not found"}, status=404)

    def do_POST(self):
        if self.path_only == "/scanner/start":
            try:
                payload = self._read_json()
            except json.JSONDecodeError as error:
                self._write_json({"error": f"invalid JSON: {error}"}, status=400)
                return
            try:
                status = scanner.start(
                    symbol=payload.get("symbol", SYMBOL),
                    base_url=payload.get("base_url", BASE_URL),
                    interval=payload.get("interval", "1m"),
                    scan_interval_seconds=int(
                        payload.get("scan_interval_seconds", SCAN_INTERVAL_SECONDS)
                    ),
                )
            except (TypeError, ValueError) as error:
                self._write_json({"error": str(error)}, status=400)
                return

            self._write_json(status)
            return

        if self.path_only == "/scanner/stop":
            try:
                payload = self._read_json()
            except json.JSONDecodeError as error:
                self._write_json({"error": f"invalid JSON: {error}"}, status=400)
                return
            self._write_json(scanner.stop(symbol=payload.get("symbol")))
            return

        self._write_json({"error": "not found"}, status=404)

    @property
    def path_only(self):
        return urlparse(self.path).path

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return self._query_params()

        raw_body = self.rfile.read(length).decode("utf-8")
        if not raw_body:
            return {}
        return json.loads(raw_body)

    def _query_params(self):
        query = parse_qs(urlparse(self.path).query)
        return {key: values[-1] for key, values in query.items()}

    def _write_json(self, payload, status=200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def build_parser():
    parser = argparse.ArgumentParser(description="Run the Dataspider control API.")
    parser.add_argument("--host", default=API_HOST)
    parser.add_argument("--port", type=int, default=API_PORT)
    return parser


def run(host=API_HOST, port=API_PORT):
    server = ThreadingHTTPServer((host, port), DataspiderHandler)
    print(f"Dataspider API listening on http://{host}:{port}")
    print("POST /scanner/start, POST /scanner/stop, GET /scanner/status")
    server.serve_forever()


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    run(host=arguments.host, port=arguments.port)
