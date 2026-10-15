import json
import re
from datetime import datetime
from pathlib import Path

LAB = Path(r"F:\Lab")
ORG = LAB / "org"
STATE = LAB / "state"
TRANSPORT = LAB / "transport"
DASHBOARD = LAB / "dashboard"

COLUMNS = ["backlog", "in-progress", "review", "done", "blocked"]
KNOWN_COLUMNS = set(COLUMNS)


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip().strip('"')
    return fields


def load_msg(path):
    """Frontmatter fields + body for a message/card file."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None, text.strip()
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip().strip('"')
    return fields, text[m.end():].strip()


def load_dir_md(folder):
    out = []
    if not folder.exists():
        return out
    for p in sorted(folder.glob("*.md")):
        f = parse_frontmatter(p)
        if f:
            out.append(f)
    return out


def load_events(limit=20):
    ev_dir = ORG / "events"
    events = []
    if ev_dir.exists():
        for p in sorted(ev_dir.glob("*.jsonl")):
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    events.sort(key=lambda e: e.get("ts", ""), reverse=True)
    return events[:limit]


def inbox_counts():
    counts = {}
    inbox = ORG / "inbox"
    if inbox.exists():
        for d in sorted(inbox.iterdir()):
            if d.is_dir():
                n = sum(1 for f in d.iterdir() if f.is_file() and f.name != ".keep")
                counts[d.name] = n
    return counts


def load_pings():
    """Unread inbox messages flagged activate: true (activation requests)."""
    pings = []
    inbox = ORG / "inbox"
    if inbox.exists():
        for d in sorted(inbox.iterdir()):
            if not d.is_dir():
                continue
            for f in sorted(d.iterdir()):
                if not f.is_file() or f.name == ".keep":
                    continue
                res = load_msg(f)
                if not res:
                    continue
                fm, body = res
                if str(fm.get("activate", "")).lower() == "true":
                    fm["to"] = d.name
                    fm["body"] = body
                    fm["rel"] = f.relative_to(LAB).as_posix()
                    pings.append(fm)
    return pings


def build_page():
    cards = load_dir_md(ORG / "cards")
    for c in cards:
        c["column"] = c.get("column", "backlog")
        if c["column"] not in KNOWN_COLUMNS:
            c["column"] = "backlog"
    agents = {}
    for a in load_dir_md(ORG / "agents"):
        agents[a.get("id", "?")] = a
    builds = load_dir_md(ORG / "builds")
    builds.sort(key=lambda b: (b.get("ts", ""), b.get("id", "")), reverse=True)
    events = load_events()
    inboxes = inbox_counts()
    pings = load_pings()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def esc(s):
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    # ---- Kanban ----
    col_html = []
    for col in COLUMNS:
        items = [c for c in cards if c.get("column") == col]
        cards_html = []
        for c in items:
            deps = []
            for d in c.get("depends_on", "").replace("]", "").replace("[", "").split(","):
                d = d.strip().strip('"').strip()
                if d:
                    deps.append(d)
            dep_html = ""
            if deps:
                dep_html = '<div class="deps">deps: ' + ", ".join(esc(d) for d in deps) + "</div>"
            cards_html.append(
                '<div class="card col-%s">'
                '<div class="card-head"><span class="cid">%s</span><span class="assignee">%s</span></div>'
                '<div class="card-title">%s</div>'
                '<div class="card-meta">updated %s</div>'
                "%s"
                "</div>"
                % (col.replace("-", ""), esc(c.get("id", "?")), esc(c.get("assignee", "unassigned")),
                   esc(c.get("title", "(no title)")), esc(c.get("updated_at", "?")), dep_html)
            )
        col_html.append(
            '<div class="kcol">'
            '<div class="kcol-head">%s <span class="kcount">%d</span></div>'
            '<div class="kcards">%s</div>'
            "</div>" % (col, len(items), "\n".join(cards_html) or '<div class="empty">—</div>')
        )

    names = {aid: (a.get("name") or aid) for aid, a in agents.items()}

    def disp(aid):
        return names.get(aid, aid)

    # ---- Agents ----
    def heartbeat_age(hb):
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
            try:
                return datetime.now() - datetime.strptime(hb, fmt)
            except (ValueError, TypeError):
                continue
        return None

    agent_rows = []
    for aid in sorted(agents):
        a = agents[aid]

        def clean(v):
            v = a.get(v) or ""
            return "\u2014" if v in ("", "null") else v

        status = a.get("status", "")
        hb_raw = clean("last_heartbeat")
        age = heartbeat_age(hb_raw) if hb_raw != "\u2014" else None
        if age is None:
            hb_disp = "\u2014"
            stale = ""
        else:
            hours = max(0.0, age.total_seconds()) / 3600.0
            if hours < 1:
                hb_disp = "%dm ago" % max(0, int(hours * 60))
            elif hours < 48:
                hb_disp = "%dh ago" % int(hours)
            else:
                hb_disp = "%dd ago" % int(hours / 24)
            stale = " STALE" if (status == "on-duty" and hours > 24) else ""

        status_cell = "<td class='st-%s'>%s%s</td>" % (
            esc(status), esc(status), " <span class='stale'>%s</span>" % stale if stale else "")
        agent_rows.append(
            "<tr><td>%s</td><td>%s</td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(names.get(aid, aid)), esc(a.get("role", "")), status_cell,
               esc(clean("scope")), esc(clean("schedule")), esc(clean("focus")), esc(hb_disp))
        )

    # ---- Inboxes ----
    inbox_rows = []
    for name, n in inboxes.items():
        cls = "st-blocked" if n > 0 else ""
        inbox_rows.append("<tr><td>%s</td><td class='%s'>%d</td></tr>" % (disp(name), cls, n))

    # ---- Builds ----
    build_rows = []
    for b in builds:
        st = b.get("status", "pending").lower()
        chip = {"pass": "st-pass", "fail": "st-fail", "pending": "st-review"}.get(st, "st-review")
        build_rows.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td class='%s'>%s</td><td>%s</td></tr>"
            % (esc(b.get("id", "?")), esc(b.get("target", "?")), esc(b.get("agent", "?")),
               chip, esc(st), esc(b.get("ts", "?")))
        )

    # ---- Events ----
    event_rows = []
    for e in events:
        event_rows.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(e.get("ts", "?")), esc(e.get("agent", "?")), esc(e.get("type", "?")), esc(e.get("card_id", "")))
        )

    pings_html = []
    for p in pings:
        cls = " to-brad" if p.get("to") == "brad" else ""
        card = p.get("card", "")
        card_note = (
            ' · <a href="../org/cards/%s.md">%s</a>' % (esc(card), esc(card))
            if card else ""
        )
        work = p.get("work", "")
        work_note = ""
        if work:
            if work.lower().startswith("http"):
                work_note = ' · work: <a href="%s">%s</a>' % (esc(work), esc(work))
            else:
                work_note = " · work: %s" % esc(work)
        rel = p.get("rel", "")
        src = (
            '<span class="dim"> · <a href="../%s">source</a></span>' % rel
            if rel else ""
        )
        pings_html.append(
            '<details class="ping%s">'
            '<summary><b>%s → %s</b> — %s <span class="dim">· needs: %s</span>%s%s</summary>'
            '<pre class="msgbody">%s</pre>'
            '<div class="card-meta">%s</div>'
            "</details>"
            % (cls, esc(disp(p.get("from", "?"))), esc(disp(p.get("to", "?"))),
               esc(p.get("subject", "")), esc(p.get("needs", "-")),
               card_note, work_note, esc(p.get("body", "")), src)
        )

    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="30">
<title>Templeton Systems — Org Dashboard</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --border: #30363d; --text: #e6edf3;
    --dim: #8b949e; --accent: #58a6ff; --green: #3fb950; --red: #f85149;
    --yellow: #d29922; --purple: #bc8cff;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text);
         font: 14px/1.5 "Segoe UI", system-ui, sans-serif; padding: 20px 28px 60px; }
  h1 { font-size: 20px; margin: 0 0 4px; }
  h2 { font-size: 15px; text-transform: uppercase; letter-spacing: 1px; color: var(--dim); margin: 28px 0 12px; }
  .sub { color: var(--dim); font-size: 12px; margin-bottom: 8px; }
  .board { display: flex; gap: 12px; align-items: flex-start; overflow-x: auto; padding-bottom: 8px; }
  .kcol { background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
          min-width: 240px; flex: 1; padding: 10px; }
  .kcol-head { font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;
               color: var(--dim); display: flex; justify-content: space-between; padding: 2px 4px 8px; }
  .kcount { background: var(--border); border-radius: 10px; padding: 0 8px; }
  .card { background: #1c2129; border: 1px solid var(--border); border-left: 3px solid var(--dim);
          border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; }
  .card.col-in-progress { border-left-color: var(--accent); }
  .card.col-review { border-left-color: var(--yellow); }
  .card.col-done { border-left-color: var(--green); }
  .card.col-blocked { border-left-color: var(--red); }
  .card-head { display: flex; justify-content: space-between; align-items: center; }
  .cid { color: var(--dim); font-size: 11px; font-family: Consolas, monospace; }
  .assignee { background: #21262d; border: 1px solid var(--border); border-radius: 10px;
              font-size: 11px; padding: 1px 8px; color: var(--accent); }
  .card-title { font-weight: 600; margin: 6px 0 4px; }
  .card-meta, .deps { color: var(--dim); font-size: 11px; }
  .empty { color: var(--dim); opacity: .5; padding: 4px; }
  table { width: 100%%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; }
  th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--border); font-size: 13px; }
  th { color: var(--dim); text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }
  tr:last-child td { border-bottom: none; }
  .st-pass { color: var(--green); font-weight: 600; }
  .st-fail { color: var(--red); font-weight: 600; }
  .st-review { color: var(--yellow); font-weight: 600; }
  .st-on-duty { color: var(--green); }
  .st-cloud { color: var(--purple); }
  .st-blocked { color: var(--red); font-weight: 700; }
  .stale { color: var(--red); font-weight: 700; font-size: 11px; }
  .pings .ping { background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
                padding: 10px 12px; margin-bottom: 8px; }
  .pings .ping.to-brad { border-left: 3px solid var(--red); }
  .pings summary { cursor: pointer; font-weight: 600; }
  .msgbody { white-space: pre-wrap; font-size: 12px; color: var(--dim);
             font-family: Consolas, monospace; margin: 10px 0 6px; }
  .dim { color: var(--dim); font-weight: 400; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  a { color: var(--accent); text-decoration: none; }
  .refresh-note { position: fixed; bottom: 14px; right: 20px; color: var(--dim); font-size: 11px; }
</style>
</head>
<body>
<h1>Templeton Systems <span style="color:var(--dim);font-weight:400">— Org Dashboard</span></h1>
<div class="sub">generated %s &nbsp;·&nbsp; F:\\Lab &nbsp;·&nbsp; auto-refresh 30s &nbsp;·&nbsp; <a href="BOARD.md">plain-text board</a></div>

<h2>Pings</h2>
<div class="pings">
%s
</div>

<h2>Kanban</h2>
<div class="board">
%s
</div>

<div class="grid">
<div>
<h2>Agents</h2>
<table>
<tr><th>ID</th><th>Role</th><th>Status</th><th>Scope</th><th>Schedule</th><th>Focus</th><th>Heartbeat</th></tr>
%s
</table>

<h2>Inboxes</h2>
<table>
<tr><th>Agent</th><th>Messages</th></tr>
%s
</table>
</div>
<div>
<h2>Builds</h2>
<table>
<tr><th>ID</th><th>Target</th><th>Agent</th><th>Status</th><th>TS</th></tr>
%s
</table>

<h2>Recent Events</h2>
<table>
<tr><th>TS</th><th>Agent</th><th>Type</th><th>Card</th></tr>
%s
</table>
</div>
</div>

<div class="refresh-note">Templeton Systems · F:\\Lab</div>
</body>
</html>""" % (now, "\n".join(pings_html) or '<div class="empty">no open pings</div>',
             "\n".join(col_html), "\n".join(agent_rows) or "<tr><td colspan='7'>no agent files yet</td></tr>",
             "\n".join(inbox_rows) or "<tr><td colspan='2'>none</td></tr>",
             "\n".join(build_rows) or "<tr><td colspan='5'>no builds recorded yet</td></tr>",
             "\n".join(event_rows) or "<tr><td colspan='4'>no events yet</td></tr>")

    DASHBOARD.mkdir(parents=True, exist_ok=True)
    (DASHBOARD / "index.html").write_text(html, encoding="utf-8")
    return len(cards)


def generate_board():
    """Plain-text board for agents (kept for tooling that reads markdown)."""
    cards = load_dir_md(ORG / "cards")
    for c in cards:
        c["column"] = c.get("column", "backlog")
        if c["column"] not in KNOWN_COLUMNS:
            c["column"] = "backlog"
    lines = ["# Templeton Board\n"]
    for col in COLUMNS:
        items = [c for c in cards if c.get("column") == col]
        lines.append("## %s" % col)
        for c in items:
            lines.append("- **%s**: %s (assignee: %s)" % (c.get("id", "?"), c.get("title", ""), c.get("assignee", "-")))
        lines.append("")
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "BOARD.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    n = build_page()
    generate_board()
    print("dashboard generated: %d card(s) -> F:\\Lab\\dashboard\\index.html" % n)
