"""Writes stay append-only, and the dashboard renders this checkout."""
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from worker.labroot import lab_root  # noqa: E402
from worker.mutate import RecordError, post_thread, update_card  # noqa: E402
import worker.dashboard as dashboard  # noqa: E402


def org_hashes(root):
    found = {}
    folder = root / "org"
    if not folder.is_dir():
        return found
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            found[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


BEFORE = org_hashes(REPO)


def setUpModule():
    global BEFORE
    BEFORE = org_hashes(REPO)


def tearDownModule():
    after = org_hashes(REPO)
    if after != BEFORE:
        changed = sorted(set(BEFORE) ^ set(after) | {
            key for key in BEFORE if key in after and BEFORE[key] != after[key]})
        raise AssertionError("a test wrote the real org record: %s" % ", ".join(changed[:12]))


def build_fixture(root):
    agents = root / "org" / "agents"
    agents.mkdir(parents=True)
    (agents / "brad.md").write_text("---\nid: brad\nname: Brad\n---\n\nCEO\n", encoding="utf-8")
    (agents / "qwen.md").write_text("---\nid: qwen\n---\n\nexecutor\n", encoding="utf-8")
    card = root / "org" / "cards"
    card.mkdir()
    (card / "card-016.md").write_text(
        "---\n"
        "id: card-016\n"
        "title: Fix the contract\n"
        "column: backlog\n"
        "assignee: unassigned\n"
        "project: swarm-playpen\n"
        "depends_on: []\n"
        "created_at: 2026-10-29T04:40\n"
        "updated_at: 2026-10-30T00:05\n"
        "---\n"
        "\n"
        "Parked. See decision-008 — do not delete this sentence.\n",
        encoding="utf-8",
    )
    projects = root / "org" / "projects"
    projects.mkdir()
    (projects / "swarm-playpen.md").write_text(
        "---\nid: swarm-playpen\ntitle: Swarm\nstatus: active\n---\n\nPlaypen.\n",
        encoding="utf-8",
    )
    for name in ("brad", "qwen"):
        inbox = root / "org" / "inbox" / name
        inbox.mkdir(parents=True)
        (inbox / ".keep").write_text("", encoding="utf-8")
    events = root / "org" / "events"
    events.mkdir()
    (events / "2026-10-30.jsonl").write_bytes(
        b'{"ts": "2026-10-30T00:05", "agent": "qwen", "type": "note", "note": "existing"}\n')
    decisions = root / "org" / "decisions"
    decisions.mkdir()
    (decisions / "2026-10-30-swarm-rebuild.md").write_text(
        "---\nid: decision-008\n---\n\n# Do not edit\n", encoding="utf-8")


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        build_fixture(self.root)
        self.old_event = (self.root / "org" / "events" / "2026-10-30.jsonl").read_bytes()
        self.decision = (self.root / "org" / "decisions" / "2026-10-30-swarm-rebuild.md").read_bytes()
        self.card = self.root / "org" / "cards" / "card-016.md"

    def tearDown(self):
        self.tmp.cleanup()

    def assert_history_intact(self):
        self.assertEqual(
            (self.root / "org" / "events" / "2026-10-30.jsonl").read_bytes(),
            self.old_event)
        self.assertEqual(
            (self.root / "org" / "decisions" / "2026-10-30-swarm-rebuild.md").read_bytes(),
            self.decision)
        self.assertTrue(self.card.is_file())

    def today_log(self):
        return self.root / "org" / "events" / ("%s.jsonl" % datetime.now().date().isoformat())


class MutateTests(Fixture):
    def test_claim_appends_and_keeps_the_body(self):
        original = self.card.read_text(encoding="utf-8")
        result = update_card(self.root, "card-016", "brad", column="in-progress")
        self.assertTrue(result["changed"])
        text = self.card.read_text(encoding="utf-8")
        self.assertIn("column: in-progress", text)
        self.assertNotIn("column: backlog", text)
        self.assertIn("depends_on: []", text)
        self.assertIn("Parked. See decision-008 — do not delete this sentence.", text)
        old_body = original.split("---", 2)[2]
        new_body = text.split("---", 2)[2]
        self.assertTrue(new_body.startswith(old_body.rstrip("\n")))
        self.assertLess(text.index("Parked. See decision-008"), text.index("_Dashboard"))
        lines = self.today_log().read_text(encoding="utf-8").splitlines()
        entry = json.loads(lines[0])
        self.assertEqual(entry["type"], "card_claim")
        self.assertEqual(entry["agent"], "brad")
        self.assertEqual(entry["card"], "card-016")
        self.assertEqual(entry["project"], "swarm-playpen")
        self.assertIn("backlog -> in-progress", entry["note"])
        self.assert_history_intact()

    def test_later_edit_does_not_rewrite_the_first_event(self):
        update_card(self.root, "card-016", "brad", column="in-progress")
        first = self.today_log().read_bytes()
        update_card(self.root, "card-016", "brad", priority="high", due="2026-12-01")
        log = self.today_log().read_bytes()
        self.assertTrue(log.startswith(first))
        lines = log.decode("utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["type"], "card_claim")
        second = json.loads(lines[1])
        self.assertEqual(second["type"], "card_update")
        self.assertIn("priority none -> high", second["note"])
        self.assertIn("due none -> 2026-12-01", second["note"])
        text = self.card.read_text(encoding="utf-8")
        self.assertIn("priority: high", text)
        self.assertIn("due: 2026-12-01", text)
        self.assertEqual(text.count("_Dashboard"), 2)
        self.assert_history_intact()

    def test_unchanged_save_writes_nothing(self):
        update_card(self.root, "card-016", "brad", column="in-progress", priority="high")
        log = self.today_log().read_bytes()
        card = self.card.read_bytes()
        result = update_card(
            self.root, "card-016", "brad",
            column="in-progress", priority="high", assignee="unassigned", due="")
        self.assertFalse(result["changed"])
        self.assertEqual(self.today_log().read_bytes(), log)
        self.assertEqual(self.card.read_bytes(), card)

    def test_done_card_is_not_deleted(self):
        update_card(self.root, "card-016", "brad", column="done")
        self.assertTrue(self.card.is_file())
        entry = json.loads(self.today_log().read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(entry["type"], "card_done")
        self.assertIn("do not delete this sentence", self.card.read_text(encoding="utf-8"))

    def test_blocked_needs_a_note_and_then_files_an_inbox_message(self):
        before = self.card.read_bytes()
        with self.assertRaises(RecordError):
            update_card(self.root, "card-016", "brad", column="blocked")
        self.assertEqual(self.card.read_bytes(), before)
        self.assertFalse(self.today_log().exists())
        update_card(
            self.root, "card-016", "brad", column="blocked",
            note="Need a ruling on the rebuild")
        text = self.card.read_text(encoding="utf-8")
        self.assertIn("column: blocked", text)
        messages = list((self.root / "org" / "inbox" / "brad").glob("*.md"))
        self.assertEqual(len(messages), 1)
        body = messages[0].read_text(encoding="utf-8")
        self.assertIn("from: brad", body)
        self.assertIn("to: brad", body)
        self.assertIn("card: card-016", body)
        self.assertIn("Need a ruling on the rebuild", body)
        kinds = [json.loads(line)["type"] for line in self.today_log().read_text(encoding="utf-8").splitlines()]
        self.assertEqual(kinds, ["card_update", "message"])
        self.assert_history_intact()

    def test_rejects_a_path_and_an_unknown_actor(self):
        before = org_hashes(self.root)
        with self.assertRaises(RecordError):
            update_card(self.root, "../card-016", "brad", column="done")
        with self.assertRaises(RecordError):
            update_card(self.root, "card-016", "newagent", column="done")
        with self.assertRaises(RecordError):
            update_card(self.root, "card-016", "brad", column="shipped")
        with self.assertRaises(RecordError):
            update_card(self.root, "card-016", "brad", due="tomorrow")
        self.assertEqual(org_hashes(self.root), before)

    def test_message_is_a_new_file_and_note_is_only_an_event(self):
        post_thread(
            self.root, "brad", "note", "Hold the rebuild.",
            project="swarm-playpen", card="card-016")
        inbox_before = sorted(p.name for p in (self.root / "org" / "inbox").rglob("*.md"))
        post_thread(
            self.root, "brad", "message", "Hold the rebuild.",
            to="qwen", subject="Ladder status", project="swarm-playpen", card="card-016")
        created = [
            p for p in (self.root / "org" / "inbox").rglob("*.md")
            if p.name not in inbox_before]
        self.assertEqual(len(created), 1)
        text = created[0].read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nfrom: brad\nto: qwen\nsubject: Ladder status\n"))
        self.assertIn("project: swarm-playpen", text)
        self.assertIn("card: card-016", text)
        self.assertIn("Hold the rebuild.", text)
        self.assertNotIn("done", created[0].relative_to(self.root / "org" / "inbox").parts)
        lines = [json.loads(line) for line in self.today_log().read_text(encoding="utf-8").splitlines()]
        self.assertEqual([line["type"] for line in lines], ["note", "message"])
        self.assertEqual(lines[0]["note"], "Hold the rebuild.")
        self.assertEqual(lines[0]["project"], "swarm-playpen")
        self.assertEqual(lines[1]["file"], created[0].relative_to(self.root).as_posix())
        self.assertEqual(self.card.read_text(encoding="utf-8").split("---", 2)[1].count("column: backlog"), 1)
        self.assert_history_intact()

    def test_message_requires_a_recipient(self):
        with self.assertRaises(RecordError):
            post_thread(self.root, "brad", "message", "Hello", subject="Hi")
        self.assertFalse(self.today_log().exists())
        self.assertEqual(list((self.root / "org" / "inbox").rglob("*.md")), [])


class RenderTests(unittest.TestCase):
    def test_page_shows_the_repo_and_does_not_invent_a_lab_folder(self):
        stray = REPO / "F:\\Lab"
        self.assertFalse(stray.exists())
        count = dashboard.build_page()
        self.assertGreaterEqual(count, 20)
        self.assertFalse(stray.exists())
        html = (REPO / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertIn("card-021", html)
        self.assertIn("col-in-progress", html)
        self.assertIn("draggable='true'", html)
        self.assertIn("data-default='emergent-harness'", html)
        self.assertIn("data-project='templeton-lab'", html)
        self.assertIn("data-project='swarm-playpen'", html)
        self.assertIn("data-column='backlog'", html)
        self.assertIn("data-column='in-progress'", html)
        self.assertIn("data-column='blocked'", html)
        self.assertIn("data-column='done'", html)
        self.assertIn("id='block-modal'", html)
        self.assertNotIn("By status", html)
        self.assertNotIn("view-kanban", html)
        self.assertIn("thread/project/emergent-harness", html)
        self.assertIn("thread/agent/qwen", html)
        self.assertIn("v2 smoke-test ping", html)
        self.assertIn("action='/api/card'", html)
        self.assertIn("action='/api/post'", html)
        self.assertNotIn("action='/api/decision'", html)
        self.assertNotIn("col-inprogress", html)
        self.assertEqual(org_hashes(REPO), BEFORE)

    def test_lab_root_is_this_checkout_unless_overridden(self):
        root = lab_root()
        self.assertTrue((root / "org" / "cards" / "card-021.md").is_file())
        old = os.environ.get("TEMPLETON_LAB")
        with tempfile.TemporaryDirectory() as tmp:
            org = Path(tmp) / "org"
            org.mkdir()
            os.environ["TEMPLETON_LAB"] = tmp
            try:
                self.assertEqual(lab_root(), Path(tmp).resolve())
            finally:
                if old is None:
                    os.environ.pop("TEMPLETON_LAB", None)
                else:
                    os.environ["TEMPLETON_LAB"] = old


class ServeTests(unittest.TestCase):
    def test_http_round_trip_on_a_copy(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        shutil.copytree(REPO / "org", root / "org")
        decisions = org_hashes(root)
        old_event = (root / "org" / "events" / "2026-11-09.jsonl").read_bytes()
        card = (root / "org" / "cards" / "card-016.md").read_bytes()
        port = "8911"
        env = dict(os.environ)
        env["TEMPLETON_LAB"] = str(root)
        env["TEMPLETON_PORT"] = port
        env["PYTHONUNBUFFERED"] = "1"
        env.pop("TEMPLETON_LAB_UNUSED", None)
        kwargs = {}
        if os.name != "nt":
            kwargs["start_new_session"] = True
        proc = subprocess.Popen(
            [sys.executable, str(REPO / "worker" / "serve.py")],
            cwd=str(REPO),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **kwargs,
        )
        output = []

        def drain():
            for line in proc.stdout:
                output.append(line)

        threading.Thread(target=drain, daemon=True).start()
        self.addCleanup(lambda: _stop(proc))
        base = "http://127.0.0.1:%s" % port
        page = _wait_ok(base + "/", proc, output)
        self.assertIn("card-021", page)
        self.assertIn("Threads", page)
        note = "HQ thread note from the dashboard test."
        _post(base + "/api/post", {
            "actor": "brad",
            "kind": "note",
            "body": note,
            "project": "emergent-harness",
            "back": "thread/project/emergent-harness",
        })
        again = _get(base + "/")
        self.assertIn(note, again)
        log = root / "org" / "events" / ("%s.jsonl" % datetime.now().date().isoformat())
        saved = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(saved[-1]["type"], "note")
        self.assertEqual(saved[-1]["agent"], "brad")
        self.assertEqual(saved[-1]["project"], "emergent-harness")
        self.assertEqual(saved[-1]["note"], note)
        _post(base + "/api/card", {
            "id": "card-016",
            "actor": "brad",
            "back": "board",
            "column": "review",
            "assignee": "qwen",
            "priority": "high",
            "due": "2026-12-15",
            "note": "",
        })
        moved = (root / "org" / "cards" / "card-016.md").read_text(encoding="utf-8")
        self.assertIn("column: review", moved)
        self.assertIn("assignee: qwen", moved)
        self.assertIn("priority: high", moved)
        self.assertIn("due: 2026-12-15", moved)
        self.assertIn("Parked by Brad", moved)
        self.assertTrue(moved.index("Parked by Brad") < moved.index("_Dashboard"))
        with self.assertRaises(urllib.error.HTTPError) as caught:
            _post(base + "/api/card", {
                "id": "card-013",
                "actor": "brad",
                "back": "board",
                "column": "blocked",
                "note": "",
            })
        self.assertEqual(caught.exception.code, 400)
        with urllib.request.urlopen(base + "/raw/org/cards/card-016.md", timeout=5) as raw:
            self.assertEqual(raw.status, 200)
            self.assertIn(b"column: review", raw.read())
        with self.assertRaises(urllib.error.HTTPError) as missing:
            urllib.request.urlopen(base + "/raw/../etc/passwd", timeout=5)
        self.assertEqual(missing.exception.code, 404)
        missing.exception.close()
        self.assertEqual((root / "org" / "events" / "2026-11-09.jsonl").read_bytes(), old_event)
        # decisions were not part of the write, so their bytes match the copy
        for path, digest in decisions.items():
            if path.startswith("org/decisions/"):
                current = hashlib.sha256((root / path).read_bytes()).hexdigest()
                self.assertEqual(current, digest, path)
        self.assertNotEqual((root / "org" / "cards" / "card-016.md").read_bytes(), card)
        self.assertFalse((REPO / "F:\\Lab").exists())

    def test_drag_to_status_appends_one_event_and_blocked_needs_a_note(self):
        """The board drag posts /api/card with only the new column.

        Dropping on blocked is the same write, plus the note the prompt collects.
        """
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        shutil.copytree(REPO / "org", root / "org")
        decisions = (root / "org" / "decisions" / "2026-10-30-swarm-rebuild.md").read_bytes()
        old_event = (root / "org" / "events" / "2026-11-09.jsonl").read_bytes()
        port = "8912"
        proc, output = _start_server(root, port)
        self.addCleanup(lambda: _stop(proc))
        base = "http://127.0.0.1:%s" % port
        page = _wait_ok(base + "/", proc, output)
        self.assertIn("draggable='true'", page)
        self.assertIn("id='block-modal'", page)
        code, location = _post_status(base + "/api/card", {
            "id": "card-016",
            "actor": "brad",
            "column": "in-progress",
            "back": "board/swarm-playpen",
        })
        self.assertEqual(code, 303)
        self.assertIn("#board/swarm-playpen", location)
        card = (root / "org" / "cards" / "card-016.md").read_text(encoding="utf-8")
        self.assertIn("column: in-progress", card)
        self.assertIn("assignee: unassigned", card)
        log = root / "org" / "events" / ("%s.jsonl" % datetime.now().date().isoformat())
        lines = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(lines[0]["type"], "card_claim")
        self.assertEqual(lines[0]["card"], "card-016")
        self.assertEqual(lines[0]["agent"], "brad")
        self.assertIn("backlog -> in-progress", lines[0]["note"])
        code, _location = _post_status(base + "/api/card", {
            "id": "card-016",
            "actor": "brad",
            "column": "blocked",
            "back": "board/swarm-playpen",
        })
        self.assertEqual(code, 400)
        self.assertIn(
            "column: in-progress",
            (root / "org" / "cards" / "card-016.md").read_text(encoding="utf-8"))
        code, location = _post_status(base + "/api/card", {
            "id": "card-016",
            "actor": "brad",
            "column": "blocked",
            "note": "Need a ruling before anyone touches the yacht tests",
            "back": "board/swarm-playpen",
        })
        self.assertEqual(code, 303)
        self.assertIn("#board/swarm-playpen", location)
        moved = (root / "org" / "cards" / "card-016.md").read_text(encoding="utf-8")
        self.assertIn("column: blocked", moved)
        self.assertLess(moved.index("Parked by Brad"), moved.index("_Dashboard"))
        messages = list((root / "org" / "inbox" / "brad").glob("*.md"))
        self.assertEqual(len(messages), 1)
        filed = messages[0].read_text(encoding="utf-8")
        self.assertIn("to: brad", filed)
        self.assertIn("card: card-016", filed)
        self.assertIn("Need a ruling before anyone touches the yacht tests", filed)
        kinds = [json.loads(line)["type"] for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(kinds, ["card_claim", "card_update", "message"])
        self.assertEqual(
            (root / "org" / "events" / "2026-11-09.jsonl").read_bytes(), old_event)
        self.assertEqual(
            (root / "org" / "decisions" / "2026-10-30-swarm-rebuild.md").read_bytes(),
            decisions)


def _start_server(root, port):
    env = dict(os.environ)
    env["TEMPLETON_LAB"] = str(root)
    env["TEMPLETON_PORT"] = str(port)
    env["PYTHONUNBUFFERED"] = "1"
    kwargs = {}
    if os.name != "nt":
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(
        [sys.executable, str(REPO / "worker" / "serve.py")],
        cwd=str(REPO),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs,
    )
    output = []

    def drain():
        for line in proc.stdout:
            output.append(line)

    threading.Thread(target=drain, daemon=True).start()
    return proc, output


def _post_status(url, fields):
    """POST without following the redirect, the way a drag records the move."""
    class _Stop(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    data = urllib.parse.urlencode(fields).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    opener = urllib.request.build_opener(_Stop)
    try:
        response = opener.open(request, timeout=10)
    except urllib.error.HTTPError as exc:
        location = exc.headers.get("Location")
        exc.close()
        return exc.code, location
    location = response.headers.get("Location")
    response.close()
    return response.status, location


def _stop(proc):
    if proc.poll() is not None:
        return
    if os.name == "nt":
        proc.terminate()
    else:
        os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def _get(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


def _wait_ok(url, proc, output):
    last = None
    for _ in range(50):
        if proc.poll() is not None:
            text = b"".join(output).decode("utf-8", "replace")
            raise AssertionError("server exited\n" + text)
        try:
            return _get(url)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise AssertionError("server %s\n%s" % (exc.code, detail))
        except Exception as exc:
            last = exc
            time.sleep(0.2)
    text = b"".join(output).decode("utf-8", "replace")
    raise AssertionError("server did not answer (%s)\n%s" % (last, text))


def _post(url, fields):
    data = urllib.parse.urlencode(fields).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8")


if __name__ == "__main__":
    unittest.main()
