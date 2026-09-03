"""Minimal HTTP server for free cron services (cron-job.org, Render, etc.)."""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import subprocess
import sys

PORT = int(os.environ.get("PORT", "8080"))
CRON_SECRET = os.environ.get("CRON_SECRET", "")


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        print(format % args)

    def _respond(self, code: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path in ("/", "/health"):
            self._respond(200, {"ok": True, "service": "news-ai"})
            return

        if not CRON_SECRET or self.path != f"/{CRON_SECRET}":
            self._respond(403, {"ok": False, "error": "forbidden"})
            return

        def _job() -> None:
            try:
                subprocess.run(
                    [sys.executable, "scripts/fetch_articles.py"],
                    check=True,
                )
            except Exception as exc:
                print(f"Fetch failed: {type(exc).__name__}: {exc}")

        threading.Thread(target=_job, daemon=True).start()
        self._respond(202, {"ok": True, "status": "started"})


def main() -> None:
    if not CRON_SECRET:
        raise SystemExit("CRON_SECRET environment variable is required")

    server = HTTPServer(("0.0.0.0", PORT), _Handler)
    print(f"Trigger server listening on :{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
