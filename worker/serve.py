import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

LAB = Path(r"F:\Lab")
sys.path.insert(0, str(LAB / "worker"))

import dashboard  # noqa: E402  (same folder)

PORT = 8901


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            try:
                dashboard.build_page()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(("dashboard error: %s" % e).encode())
                return
            body = (LAB / "dashboard" / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/BOARD.md":
            p = LAB / "state" / "BOARD.md"
            body = p.read_bytes() if p.exists() else b"# Templeton Board\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/raw/"):
            rel = self.path[5:].lstrip("/")
            fp = (LAB / rel).resolve()
            lab = LAB.resolve()
            if str(fp).startswith(str(lab)) and fp.is_file():
                body = fp.read_bytes()
                ext = fp.suffix.lower()
                ctype = {
                    ".md": "text/markdown; charset=utf-8",
                    ".json": "application/json; charset=utf-8",
                    ".jsonl": "text/plain; charset=utf-8",
                    ".html": "text/html; charset=utf-8",
                    ".py": "text/plain; charset=utf-8",
                    ".yaml": "text/plain; charset=utf-8",
                    ".yml": "text/plain; charset=utf-8",
                }.get(ext, "text/plain; charset=utf-8")
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass  # keep console quiet


if __name__ == "__main__":
    print("Templeton dashboard live: http://localhost:%d  (Ctrl+C to stop)" % PORT)
    try:
        HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
