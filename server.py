#!/usr/bin/env python3
import html
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


def env_page() -> bytes:
    rows = "\n".join(
        f"<tr><td>{html.escape(k)}</td><td>{html.escape(v)}</td></tr>"
        for k, v in sorted(os.environ.items())
    )
    body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Container environment</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 64rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.35rem 0.6rem; text-align: left; vertical-align: top; }}
    th {{ background: #f4f4f4; }}
    td:first-child {{ font-weight: 600; white-space: nowrap; }}
    td:last-child {{ word-break: break-all; }}
  </style>
</head>
<body>
  <h1>Environment variables</h1>
  <table>
    <thead><tr><th>Name</th><th>Value</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>"""
    return body.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        payload = env_page()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:
        pass


def main() -> None:
    host, port = "0.0.0.0", 443
    server = HTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
