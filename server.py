#!/usr/bin/env python3
import html
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Iterable
from urllib.parse import splitport

PROXY_HEADER_NAMES = (
    "Forwarded",
    "X-Forwarded-For",
    "X-Forwarded-Host",
    "X-Forwarded-Proto",
    "X-Forwarded-Port",
    "X-Real-IP",
    "True-Client-IP",
    "CF-Connecting-IP",
)


def _is_ip(hostname: str) -> bool:
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(family, hostname)
            return True
        except OSError:
            continue
    return False


def _hostname_from_host_header(host_header: str | None) -> str | None:
    if not host_header:
        return None
    host, _port = splitport(host_header.strip())
    return host or None


def _lookup_a_records(hostname: str) -> str:
    try:
        infos = socket.getaddrinfo(
            hostname, None, family=socket.AF_INET, type=socket.SOCK_STREAM
        )
        addrs = sorted({item[4][0] for item in infos})
        return ", ".join(addrs) if addrs else "(no A records)"
    except socket.gaierror as exc:
        return f"(lookup failed: {exc})"


def _server_variables(handler: BaseHTTPRequestHandler) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []

    client = handler.client_address
    rows.append(("TCP client (remote)", f"{client[0]}:{client[1]}"))

    try:
        local = handler.connection.getsockname()
        rows.append(("TCP local (this connection)", f"{local[0]}:{local[1]}"))
    except OSError:
        rows.append(("TCP local (this connection)", "(unavailable)"))

    host_header = handler.headers.get("Host")
    rows.append(("Host header", host_header or "(not sent)"))

    hostname = _hostname_from_host_header(host_header)
    if hostname and _is_ip(hostname):
        rows.append(("DNS A lookup for Host", "(skipped — Host is an IP address)"))
    elif hostname:
        rows.append((f"DNS A lookup for {hostname}", _lookup_a_records(hostname)))
    else:
        rows.append(("DNS A lookup for Host", "(no hostname in Host header)"))

    for name in PROXY_HEADER_NAMES:
        value = handler.headers.get(name)
        rows.append((name, value if value is not None else "(not sent)"))

    return rows


def _table_rows(pairs: Iterable[tuple[str, str]]) -> str:
    return "\n".join(
        f"<tr><td>{html.escape(k)}</td><td>{html.escape(v)}</td></tr>"
        for k, v in pairs
    )


def build_page(handler: BaseHTTPRequestHandler) -> bytes:
    env_rows = _table_rows(sorted(os.environ.items()))
    server_rows = _table_rows(_server_variables(handler))
    body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Container environment</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 64rem; margin-bottom: 1.5rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.35rem 0.6rem; text-align: left; vertical-align: top; }}
    th {{ background: #f4f4f4; }}
    td:first-child {{ font-weight: 600; white-space: nowrap; }}
    td:last-child {{ word-break: break-all; }}
  </style>
</head>
<body>
  <h1>Server variables</h1>
  <p>Per-request connection and HTTP metadata. Proxy headers are only present when a reverse proxy sets them.</p>
  <table>
    <thead><tr><th>Name</th><th>Value</th></tr></thead>
    <tbody>
{server_rows}
    </tbody>
  </table>
  <h1>Environment variables</h1>
  <table>
    <thead><tr><th>Name</th><th>Value</th></tr></thead>
    <tbody>
{env_rows}
    </tbody>
  </table>
</body>
</html>"""
    return body.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        payload = build_page(self)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:
        pass


def main() -> None:
    host, port = "0.0.0.0", 8080
    server = HTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
