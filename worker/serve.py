"""Serve the HQ dashboard and accept board and thread writes.

    python worker/serve.py

Then open http://localhost:8901 . Binds to 127.0.0.1 only. The org root is
the checkout that contains this file (F:\\Lab on the HQ box). TEMPLETON_PORT
overrides the port; it is not part of the normal run.
"""
import importlib
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

WORKER = Path(__file__).resolve().parent
if str(WORKER) not in sys.path:
    sys.path.insert(0, str(WORKER))

import dashboard  # noqa: E402
import mutate  # noqa: E402
from labroot import lab_root  # noqa: E402

PORT = int(os.environ.get("TEMPLETON_PORT", "8901"))
SKIP_PARTS = {".git", "__pycache__", "swarm", "node_modules", ".venv"}
BACK_RE = re.compile(
    r"board/[a-z0-9-]+|thread/(?:general|project/[a-z0-9-]+|agent/[a-z0-9-]+)|proj/[a-z0-9-]+")
PLAIN_BACK = {"board", "threads", "projects", "pings", "roster",
              "decisions", "memory", "builds", "events"}


def fresh():
    """Reload generators so a long-running process does not keep a stale page."""
    importlib.reload(mutate)
    hq = sys.modules.get("hq_render")
    if hq is not None:
        importlib.reload(hq)
    importlib.reload(dashboard)
    return dashboard


def safe_repo_file(rel):
    root = lab_root().resolve()
    rel = (rel or "").replace("\\", "/").split("?", 1)[0].split("#", 1)[0].lstrip("/")
    if not rel:
        return None
    parts = Path(rel).parts
    if ".." in parts or any(part in SKIP_PARTS for part in parts):
        return None
    fp = (root / rel).resolve()
    try:
        fp.relative_to(root)
    except ValueError:
        return None
    if not fp.is_file():
        return None
    return fp


def field(fields, name):
    if name not in fields:
        return None
    return fields[name][0]


def safe_back(value):
    value = (value or "board").strip()
    if value in PLAIN_BACK or BACK_RE.fullmatch(value):
        return value
    return "board"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in ("/", "/index.html"):
            self._page()
            return
        if path == "/BOARD.md":
            dash = fresh()
            try:
                dash.generate_board()
            except Exception as exc:
                self._text(500, "board error: %s" % exc)
                return
            board = lab_root() / "state" / "BOARD.md"
            body = board.read_bytes() if board.is_file() else b"# Templeton Board\n"
            self._bytes(200, "text/markdown; charset=utf-8", body)
            return
        if path.startswith("/raw/"):
            fp = safe_repo_file(path[5:])
            if fp is None:
                self._text(404, "not found")
                return
            ctype = {
                ".md": "text/plain; charset=utf-8",
                ".json": "application/json; charset=utf-8",
                ".jsonl": "text/plain; charset=utf-8",
                ".html": "text/html; charset=utf-8",
                ".py": "text/plain; charset=utf-8",
                ".yaml": "text/plain; charset=utf-8",
                ".yml": "text/plain; charset=utf-8",
            }.get(fp.suffix.lower(), "text/plain; charset=utf-8")
            self._bytes(200, ctype, fp.read_bytes())
            return
        self._text(404, "not found")

    def do_POST(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path not in ("/api/card", "/api/post", "/api/project"):
            self._text(404, "not found")
            return
        if "application/x-www-form-urlencoded" not in self.headers.get("Content-Type", ""):
            self._text(415, "send a form")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._text(400, "bad length")
            return
        if length < 0 or length > 65536:
            self._text(413, "too large")
            return
        raw = self.rfile.read(length).decode("utf-8", "replace")
        fields = urllib.parse.parse_qs(raw, keep_blank_values=True)
        back = safe_back(field(fields, "back"))
        fresh()
        try:
            if path == "/api/card":
                result = mutate.update_card(
                    lab_root(),
                    field(fields, "id") or "",
                    field(fields, "actor") or "",
                    column=field(fields, "column"),
                    assignee=field(fields, "assignee"),
                    priority=field(fields, "priority"),
                    due=field(fields, "due"),
                    note=field(fields, "note") or "",
                )
                print("hq card %s changed=%s" % (
                    field(fields, "id") or "?", result.get("changed")), flush=True)
            elif path == "/api/project":
                action = (field(fields, "action") or "").strip()
                if action not in ("archive", "unarchive"):
                    raise mutate.RecordError("archive or unarchive")
                result = mutate.set_project_archived(
                    lab_root(),
                    field(fields, "project") or "",
                    field(fields, "actor") or "",
                    action == "archive",
                )
                print("hq project %s %s changed=%s" % (
                    action, field(fields, "project") or "?", result.get("changed")),
                    flush=True)
            else:
                mutate.post_thread(
                    lab_root(),
                    field(fields, "actor") or "",
                    field(fields, "kind") or "",
                    field(fields, "body") or "",
                    to=field(fields, "to") or "",
                    subject=field(fields, "subject") or "",
                    project=field(fields, "project") or "",
                    card=field(fields, "card") or "",
                )
                print("hq post %s" % (field(fields, "kind") or "?"), flush=True)
        except mutate.RecordError as exc:
            self._text(400, str(exc), back)
            return
        except Exception as exc:
            self._text(500, "not saved: %s" % exc, back)
            return
        self.send_response(303)
        self.send_header("Location", "/#" + back)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _page(self):
        dash = fresh()
        try:
            dash.build_page()
            dash.generate_board()
            dash.generate_projects()
        except Exception as exc:
            self._text(500, "dashboard error: %s" % exc)
            return
        page = lab_root() / "dashboard" / "index.html"
        self._bytes(200, "text/html; charset=utf-8", page.read_bytes())

    def _bytes(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _text(self, code, message, back="board"):
        body = (
            "<!DOCTYPE html><meta charset='utf-8'><title>HQ</title>"
            "<p>%s</p><p><a href='/#%s'>Back</a></p>"
            % (dashboard.esc(str(message)), dashboard.esc(back))
        ).encode("utf-8")
        self._bytes(code, "text/html; charset=utf-8", body)

    def log_message(self, fmt, *args):
        return


def main():
    print("Templeton dashboard live: http://localhost:%d" % PORT, flush=True)
    print("org root: %s" % lab_root(), flush=True)
    print("Ctrl+C to stop", flush=True)
    try:
        HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("stopped.", flush=True)


if __name__ == "__main__":
    main()
