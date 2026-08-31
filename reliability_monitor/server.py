"""Dependency-free JSON API and dashboard server for the reliability monitor."""

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .core import (
    ValidationError,
    compare_treatments,
    get_alerts,
    get_overview,
    insert_run,
)


MAX_REQUEST_BYTES = 1_000_000
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}


def make_handler(database_path, static_directory):
    database_path = Path(database_path)
    static_directory = Path(static_directory)

    class ReliabilityHandler(BaseHTTPRequestHandler):
        server_version = "VisionReliabilityMonitor/0.1"

        def log_message(self, message, *args):
            print(f"{self.address_string()} - {message % args}")

        def _send_json(self, payload, status=HTTPStatus.OK):
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_static(self, filename):
            path = static_directory / filename
            if not path.is_file():
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                return
            body = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", CONTENT_TYPES[path.suffix])
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            try:
                if parsed.path == "/health":
                    self._send_json({"status": "ok"})
                elif parsed.path == "/api/overview":
                    self._send_json(get_overview(database_path))
                elif parsed.path == "/api/alerts":
                    minimum = float(query.get("minimum_mean", ["0.70"])[0])
                    maximum_drop = float(
                        query.get("maximum_severity_drop", ["0.12"])[0]
                    )
                    self._send_json(get_alerts(database_path, minimum, maximum_drop))
                elif parsed.path == "/api/compare":
                    baseline = query.get("baseline", [""])[0]
                    candidate = query.get("candidate", [""])[0]
                    segmentor = query.get("segmentor", ["mseg"])[0]
                    self._send_json(
                        compare_treatments(
                            database_path, baseline, candidate, segmentor
                        )
                    )
                elif parsed.path in {"/", "/index.html"}:
                    self._send_static("index.html")
                elif parsed.path == "/app.js":
                    self._send_static("app.js")
                elif parsed.path == "/styles.css":
                    self._send_static("styles.css")
                else:
                    self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            except (ValidationError, ValueError) as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

        def do_POST(self):
            if urlparse(self.path).path != "/api/runs":
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
                if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
                    raise ValidationError("request body must be between 1 byte and 1 MB")
                payload = json.loads(self.rfile.read(content_length))
                records = payload if isinstance(payload, list) else [payload]
                if not records or len(records) > 1000:
                    raise ValidationError("submit between 1 and 1000 runs per request")
                inserted = [insert_run(database_path, record) for record in records]
                self._send_json(
                    {"accepted": len(inserted), "runs": inserted},
                    HTTPStatus.CREATED,
                )
            except (ValidationError, ValueError, json.JSONDecodeError) as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    return ReliabilityHandler


def build_server(database_path, host="127.0.0.1", port=8081):
    static_directory = Path(__file__).with_name("static")
    return ThreadingHTTPServer(
        (host, port), make_handler(database_path, static_directory)
    )


def serve(database_path, host="127.0.0.1", port=8081):
    server = build_server(database_path, host=host, port=port)
    print(f"Vision Reliability Monitor: http://{host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
