"""Templeton Systems dashboard generator (v2 — tabs + detail drawers).

Generates F:\\Lab\\dashboard\\index.html — self-contained (no external deps,
works from file:// or via worker/serve.py). Also writes the plain-text
board to F:\\Lab\\state\\BOARD.md for tools that read markdown.

Tabs (hash-routed): board | projects | pings | roster | builds | events
Projects: `#proj/<id>` opens a per-project page — cards, builds, decisions
(by mention), the project's memory cell, and events scoped by ctx refs.
Drawers: click any card / ping / build / agent / inbox / decision / project to
open the full artifact. Artifact bodies are embedded as JSON in the page.
"""
import datetime
import json
import re
from pathlib import Path

LAB = Path(r"F:\Lab")
ORG = LAB / "org"
STATE = LAB / "state"
TRANSPORT = LAB / "transport"
DASHBOARD = LAB / "dashboard"

COLUMNS = ["backlog", "in-progress", "review", "done", "blocked"]
KNOWN_COLUMNS = set(COLUMNS)
COLUMN_RANK = {name: i for i, name in enumerate(COLUMNS)}


# ---------- loading ----------

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


def load_md_with_body(folder):
    """All markdown files in a folder as frontmatter dicts (+_body, _rel)."""
    out = []
    if not folder.exists():
        return out
    for p in sorted(folder.glob("*.md")):
        fm, body = load_msg(p)
        if fm is None:
            continue
        fm["_body"] = body
        fm["_rel"] = p.relative_to(LAB).as_posix()
        out.append(fm)
    return out


def pub_meta(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


def load_events(limit=20):
    """Whole log, newest first; limit=None means no cap (project scoping
    needs every event, the Events tab stays capped)."""
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
    return events[:limit] if limit else events


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


def load_inboxes():
    """Unread messages per agent (for Roster tab + inbox drawers)."""
    result = {}
    inbox = ORG / "inbox"
    if inbox.exists():
        for d in sorted(inbox.iterdir()):
            if not d.is_dir():
                continue
            msgs = []
            for f in sorted(d.iterdir()):
                if not f.is_file() or f.name == ".keep":
                    continue
                if "done" in f.relative_to(ORG).parts:
                    continue
                fm, body = load_msg(f)
                if fm is None:
                    fm = {}
                msgs.append({
                    "file": f.name,
                    "rel": f.relative_to(LAB).as_posix(),
                    "from": fm.get("from", "?"),
                    "subject": fm.get("subject", f.name),
                    "activate": str(fm.get("activate", "")).lower() == "true",
                    "body": body,
                })
            result[d.name] = msgs
    return result


def load_decisions():
    out = []
    ddir = ORG / "decisions"
    if ddir.exists():
        for f in sorted(ddir.glob("*.md")):
            fm, body = load_msg(f)
            if fm is None:
                fm = {}
            title = ""
            for line in body.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            out.append({
                "id": fm.get("id", f.stem),
                "date": fm.get("date", ""),
                "status": fm.get("status", ""),
                "title": title or f.stem,
                "body": body,
                "path": f.relative_to(LAB).as_posix(),
            })
    return out


def load_memory():
    """Qwen's Lattice: core.md (hot tier) + cells/ (warm tier)."""
    mem = {"core": None, "cells": []}
    core = LAB / "memory" / "core.md"
    if core.exists():
        mem["core"] = {
            "body": core.read_text(encoding="utf-8").strip(),
            "path": "memory/core.md",
        }
    cdir = LAB / "memory" / "cells"
    if cdir.exists():
        for p in sorted(cdir.glob("*.md")):
            fm, body = load_msg(p)
            if fm is None:
                continue
            fm["_body"] = body
            fm["_rel"] = p.relative_to(LAB).as_posix()
            mem["cells"].append(fm)
    return mem


def load_projects():
    """org/projects/<id>.md — the org's project artifacts."""
    return load_md_with_body(ORG / "projects")


def project_scopes(projects, cards, builds):
    """Returns project_of(event). Scope by explicit ctx field first, then by
    the card/build/memory-cell/repo the event names; None = not scoped."""
    ids = set()
    by_cell = {}
    by_repo = {}
    for p in projects:
        pid = p.get("id")
        ids.add(pid)
        cell = (p.get("memory_cell") or "").strip().replace("\\", "/")
        if cell:
            stem = cell.split("/")[-1].replace(".md", "")
            by_cell[stem] = pid
            by_cell[cell] = pid
        repo = (p.get("repo") or "").strip()
        if repo:
            by_repo[repo.rstrip("/").split("/")[-1]] = pid
    by_card = {c.get("id"): c.get("project") for c in cards if c.get("project")}
    by_build = {b.get("id"): b.get("project") for b in builds if b.get("project")}

    def project_of(e):
        explicit = e.get("project")
        if explicit and explicit in ids:
            return explicit
        # older events used `card_id`, newer ones `card` — both are card refs
        for key, index in (("card", by_card), ("card_id", by_card),
                           ("build_id", by_build), ("build", by_build)):
            ref = e.get(key)
            if ref and index.get(ref):
                return index[ref]
        cell = e.get("cell")
        if cell and by_cell.get(cell.replace(".md", "")):
            return by_cell[cell.replace(".md", "")]
        repo = e.get("repo")
        if repo and by_repo.get(repo.rstrip("/").split("/")[-1]):
            return by_repo[repo.rstrip("/").split("/")[-1]]
        # a `file` ref naming an artifact inside a project's own tree
        file = e.get("file")
        if file:
            file = str(file).replace("\\", "/")
            base = file.split("/")[-1].replace(".md", "")
            if file.startswith("org/cards/") and by_card.get(base):
                return by_card[base]
            if file.startswith("org/builds/") and by_build.get(base):
                return by_build[base]
            if file.startswith("org/projects/") and base in ids:
                return base
            if file.startswith("memory/cells/") and by_cell.get(base):
                return by_cell[base]
        return None

    return project_of


def mentions_project(doc, pid):
    """Decisions carry no project field, so this is by token mention only —
    the dashboard labels it as 'by mention' instead of pretending precision."""
    tokens = [t for t in pid.split("-") if len(t) >= 4]
    hay = ("%s %s" % (doc.get("id", ""),
                      doc.get("body", "") or doc.get("_body", ""))).lower()
    return any(t in hay for t in tokens)


def build_streak(builds):
    """Newest-first builds -> (kind, count) of the current pass/fail streak."""
    kind = None
    n = 0
    for b in builds:
        st = (b.get("status") or "").lower()
        if st not in ("pass", "fail"):
            continue
        if kind is None:
            kind = st
        if st != kind:
            break
        n += 1
    return kind, n


def heartbeat_age(hb):
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.datetime.now() - datetime.datetime.strptime(hb, fmt)
        except (ValueError, TypeError):
            continue
    return None


# ---------- rendering ----------

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def event_ref(e):
    """Whatever an event points at — card, build, note, decision, cell, repo."""
    for key in ("card", "card_id", "build_id", "build", "note", "decision",
                "cell", "repo", "message"):
        if e.get(key):
            return str(e[key])
    return ""


def md_lite(text):
    """Minimal markdown for our prose artifacts: paragraphs, **bold**, `code`."""
    parts = []
    for para in re.split(r"\n\s*\n", (text or "").strip()):
        p = esc(para.strip()).replace("\n", " ")
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"`([^`]+)`", r"<code>\1</code>", p)
        if p:
            parts.append("<p>%s</p>" % p)
    return "".join(parts)


def build_page():
    now = datetime.datetime.now()
    cards = load_md_with_body(ORG / "cards")
    for c in cards:
        c["column"] = c.get("column", "backlog")
        if c["column"] not in KNOWN_COLUMNS:
            c["column"] = "backlog"
    agents = load_md_with_body(ORG / "agents")
    builds = load_md_with_body(ORG / "builds")
    builds.sort(key=lambda b: (b.get("ts", ""), b.get("id", "")), reverse=True)
    events = load_events()
    pings = load_pings()
    inboxes = load_inboxes()
    decisions = load_decisions()
    memory = load_memory()
    projects = load_projects()
    all_events = load_events(limit=None)
    project_of = project_scopes(projects, cards, builds)

    names = {a.get("id", "?"): (a.get("name") or a.get("id")) for a in agents}

    def disp(aid):
        return names.get(aid, aid)

    # ---- artifacts JSON (drawer content) ----
    artifacts = {
        "cards": {c["id"]: {"meta": pub_meta(c), "body": c["_body"], "path": c["_rel"]}
                 for c in cards if "id" in c},
        "agents": {a.get("id", "?"): {"meta": pub_meta(a), "body": a["_body"], "path": a["_rel"]}
                  for a in agents},
        "builds": {b.get("id", "?"): {"meta": pub_meta(b), "body": b["_body"], "path": b["_rel"]}
                  for b in builds if "id" in b},
        "pings": {p["rel"]: {"meta": pub_meta(p), "body": p.get("body", "")}
                 for p in pings},
        "inbox": {name: msgs for name, msgs in inboxes.items()},
        "decisions": {d["id"]: d for d in decisions},
    }
    mem_art = {}
    if memory.get("core"):
        mem_art["core"] = {
            "meta": {"id": "core", "tier": "hot — always loaded"},
            "body": memory["core"]["body"],
            "path": "memory/core.md",
        }
    for c in memory.get("cells", []):
        mem_art[c.get("id", "?")] = {
            "meta": pub_meta(c), "body": c["_body"], "path": c["_rel"]}
    artifacts["memory"] = mem_art
    artifacts["projects"] = {p.get("id", "?"): {"meta": pub_meta(p), "body": p["_body"],
                                                "path": p["_rel"]}
                             for p in projects if "id" in p}
    artifacts_json = json.dumps(artifacts).replace("</", "<\\/")

    # ---- Board tab ----
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
                '<div class="card clickable col-%s" data-kind="card" data-id="%s">'
                '<div class="card-head"><span class="cid">%s</span><span class="assignee">%s</span></div>'
                '<div class="card-title">%s</div>'
                '<div class="card-meta">updated %s</div>'
                "%s"
                "</div>"
                % (col.replace("-", ""), esc(c.get("id", "?")), esc(c.get("id", "?")),
                   esc(c.get("assignee", "unassigned")), esc(c.get("title", "(no title)")),
                   esc(c.get("updated_at", "?")), dep_html)
            )
        col_html.append(
            '<div class="kcol">'
            '<div class="kcol-head">%s <span class="kcount">%d</span></div>'
            '<div class="kcards">%s</div>'
            "</div>" % (col, len(items), "\n".join(cards_html) or '<div class="empty">—</div>')
        )

    # ---- Pings tab ----
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
        pings_html.append(
            '<div class="pingrow clickable%s" data-kind="ping" data-id="%s">'
            "<b>%s → %s</b> — %s <span class='dim'>· needs: %s</span>%s%s"
            "</div>"
            % (cls, esc(p["rel"]), esc(disp(p.get("from", "?"))),
               esc(disp(p.get("to", "?"))), esc(p.get("subject", "")),
               esc(p.get("needs", "-")), card_note, work_note)
        )

    # ---- Roster tab ----
    agent_rows = []
    for a in agents:
        aid = a.get("id", "?")
        status = a.get("status", "")

        def clean(v):
            v = a.get(v) or ""
            return "\u2014" if v in ("", "null") else v

        hb_raw = clean("last_heartbeat")
        dispatch_only = str(a.get("dispatch_only", "")).lower() in ("true", "yes", "1")
        age = heartbeat_age(hb_raw) if hb_raw != "\u2014" else None
        if dispatch_only:
            hb_disp = "dispatch-only"
            stale = ""
        elif age is None:
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
            esc(status), esc(status),
            " <span class='stale'>%s</span>" % stale if stale else "")
        agent_rows.append(
            "<tr class='clickable' data-kind='agent' data-id='%s'><td>%s</td><td>%s</td>%s"
            "<td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(aid), esc(names.get(aid, aid)), esc(a.get("role", "")), status_cell,
               esc(clean("scope")), esc(clean("schedule")), esc(hb_disp))
        )

    inbox_rows = []
    for name in sorted(inboxes):
        n = len(inboxes[name])
        cls = "st-blocked" if n > 0 else ""
        inbox_rows.append(
            "<tr class='clickable' data-kind='inbox' data-id='%s'><td>%s</td><td class='%s'>%d</td></tr>"
            % (esc(name), esc(disp(name)), cls, n))

    decision_rows = []
    for d in decisions:
        decision_rows.append(
            "<tr class='clickable' data-kind='decision' data-id='%s'><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(d["id"]), esc(d["id"]), esc(d["date"]), esc(d["status"]), esc(d["title"])))

    # ---- Builds tab ----
    build_rows = []
    for b in builds:
        st = (b.get("status", "pending")).lower()
        chip = {"pass": "st-pass", "fail": "st-fail"}.get(st, "st-review")
        build_rows.append(
            "<tr class='clickable' data-kind='build' data-id='%s'><td>%s</td><td>%s</td><td>%s</td>"
            "<td class='%s'>%s</td><td>%s</td></tr>"
            % (esc(b.get("id", "?")), esc(b.get("id", "?")), esc(b.get("target", "?")),
               esc(b.get("agent", "?")), chip, esc(st), esc(b.get("ts", "?")))
        )

    # ---- Events tab ----
    event_rows = []
    for e in events:
        event_rows.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(e.get("ts", "?")), esc(e.get("agent", "?")), esc(e.get("type", "?")),
               esc(event_ref(e) or "\u2014"), esc(project_of(e) or "\u2014"))
        )

    mem_rows = []
    if memory.get("core"):
        mem_rows.append(
            "<tr class='clickable' data-kind='memory' data-id='core'>"
            "<td>core.md</td><td>core</td><td>\u2014</td><td>always</td>"
            "<td>hot tier \u2014 identity, Brad, standing preferences</td></tr>")
    for c in memory.get("cells", []):
        firstline = (c.get("_body", "").splitlines() or [""])[0].strip()[:60]
        mem_rows.append(
            "<tr class='clickable' data-kind='memory' data-id='%s'><td>%s</td>"
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(c.get("id", "?")), esc(c.get("id", "?")),
               esc(c.get("kind", "?")), esc(c.get("key", "?")),
               esc(c.get("updated", "?")), esc(firstline)))

    # ---- Projects tab: overview + one page per project ----
    proj_rows = []
    proj_panes = []
    for pr in sorted(projects, key=lambda p: ((p.get("status") or "") != "active",
                                              p.get("id", ""))):
        pid = pr.get("id", "?")
        pcards = [c for c in cards if c.get("project") == pid]
        pbuilds = [b for b in builds if b.get("project") == pid]
        pevents = [e for e in all_events if project_of(e) == pid]
        pdocs = [d for d in decisions if mentions_project(d, pid)]
        cell_id = (pr.get("memory_cell") or "").strip()
        cell = next((c for c in memory.get("cells", []) if c.get("id") == cell_id), None)
        st = (pr.get("status") or "?").lower()
        chip = "st-pass" if st == "active" else "dim"
        repo = (pr.get("repo") or "").strip()
        repo_html = ("<a href='%s' target='_blank' rel='noopener'>%s</a>"
                     % (esc(repo), esc(repo)) if repo.startswith("http")
                     else "<span class='dim'>local only</span>")
        done = sum(1 for c in pcards if c.get("column") == "done")
        passed = sum(1 for b in pbuilds if (b.get("status") or "").lower() == "pass")
        failed = sum(1 for b in pbuilds if (b.get("status") or "").lower() == "fail")
        streak_kind, streak_n = build_streak(pbuilds)

        proj_rows.append(
            "<tr class='clickable' data-kind='project' data-id='%s'>"
            "<td><a href='#proj/%s'>%s</a></td><td class='%s'>%s</td><td>%s</td>"
            "<td>%d open / %d done</td><td>%d pass / %d fail</td><td>%d</td></tr>"
            % (esc(pid), esc(pid), esc(pr.get("title") or pid), chip, esc(st), repo_html,
               len(pcards) - done, done, passed, failed, len(pevents)))

        pan = ["<section class='pane' data-pane='proj/%s'>" % esc(pid)]
        pan.append("<div class='crumb'><a href='#projects'>&larr; Projects</a>"
                   " &middot; %s</div>" % esc(pid))
        pan.append("<h2>%s <span class='%s'>[%s]</span></h2>"
                   % (esc(pr.get("title") or pid), chip, esc(st)))
        pan.append("<div class='sub'>owner %s &middot; %s &middot; path %s"
                   " &middot; memory cell %s &middot; updated %s</div>"
                   % (esc(pr.get("owner") or "?"), repo_html,
                      esc(pr.get("path") or "?"), esc(cell_id or "\u2014"),
                      esc(pr.get("updated_at") or "?")))
        pan.append("<div class='prose'>%s</div>" % md_lite(pr.get("_body", "")))

        pan.append("<h2>Cards here</h2>")
        crows = []
        for c in sorted(pcards, key=lambda c: (COLUMN_RANK.get(c["column"], 9),
                                               c.get("id", ""))):
            crows.append(
                "<tr class='clickable' data-kind='card' data-id='%s'>"
                "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (esc(c.get("id", "?")), esc(c.get("id", "?")),
                   esc(c.get("title", "(no title)")), esc(c.get("column", "?")),
                   esc(c.get("assignee", "unassigned")), esc(c.get("updated_at", "?"))))
        pan.append("<table><tr><th>ID</th><th>Title</th><th>Column</th><th>Assignee</th>"
                   "<th>Updated</th></tr>%s</table>"
                   % ("".join(crows) or "<tr><td colspan='5'>no cards tagged %s</td></tr>"
                      % esc(pid)))

        pan.append("<h2>Builds here</h2>")
        pan.append("<p class='sub'>latest streak: %d %s in a row</p>" % (streak_n, streak_kind)
                   if streak_kind else "<p class='sub'>no pass/fail builds recorded</p>")
        brows = []
        for b in pbuilds:
            bst = (b.get("status", "pending")).lower()
            bchip = {"pass": "st-pass", "fail": "st-fail"}.get(bst, "st-review")
            brows.append(
                "<tr class='clickable' data-kind='build' data-id='%s'>"
                "<td>%s</td><td>%s</td><td>%s</td><td class='%s'>%s</td><td>%s</td></tr>"
                % (esc(b.get("id", "?")), esc(b.get("id", "?")), esc(b.get("target", "?")),
                   esc(b.get("agent", "?")), bchip, esc(bst), esc(b.get("ts", "?"))))
        pan.append("<table><tr><th>ID</th><th>Target</th><th>Agent</th><th>Status</th>"
                   "<th>TS</th></tr>%s</table>"
                   % ("".join(brows) or "<tr><td colspan='5'>nothing has been built here"
                      " through the org pipeline yet</td></tr>"))

        pan.append("<h2>Decisions touching this project</h2>")
        pan.append("<p class='sub'>decisions have no project field \u2014 matched by"
                   " name mention only</p>")
        drows = []
        for d in pdocs:
            drows.append("<tr class='clickable' data-kind='decision' data-id='%s'>"
                         "<td>%s</td><td>%s</td><td>%s</td></tr>"
                         % (esc(d["id"]), esc(d["id"]), esc(d["date"]), esc(d["title"])))
        pan.append("<table><tr><th>ID</th><th>Date</th><th>Title</th></tr>%s</table>"
                   % ("".join(drows) or "<tr><td colspan='3'>no decision text mentions"
                      " this project</td></tr>"))

        pan.append("<h2>Memory cell</h2>")
        if cell:
            pan.append("<pre class='cell'>%s</pre>" % esc(cell.get("_body", "").strip()))
            pan.append("<div class='drawer-src'>source: <a href='../%s' target='_blank'>%s</a></div>"
                       % (esc(cell["_rel"]), esc(cell["_rel"])))
        else:
            pan.append("<div class='empty'>memory cell '%s' does not exist"
                       " \u2014 memory/cells/%s.md</div>" % (esc(cell_id or "?"), esc(cell_id or "?")))

        pan.append("<h2>Events scoped to this project</h2>")
        pan.append("<p class='sub'>%d of %d logged events &middot; scoped by ctx"
                   " fields (project / card / build / cell / repo)</p>"
                   % (len(pevents), len(all_events)))
        erows = []
        for e in pevents[:25]:
            erows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                         % (esc(e.get("ts", "?")), esc(e.get("agent", "?")),
                            esc(e.get("type", "?")), esc(event_ref(e) or "\u2014")))
        pan.append("<table><tr><th>TS</th><th>Agent</th><th>Type</th><th>Ref</th></tr>%s</table>"
                   % ("".join(erows) or "<tr><td colspan='4'>no events scope to this"
                      " project yet</td></tr>"))
        pan.append("</section>")
        proj_panes.append("\n".join(pan))

    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    html = HTML_TEMPLATE % {
        "ts": ts,
        "artifacts": artifacts_json,
        "board": "\n".join(col_html),
        "projects": "\n".join(proj_rows) or "<tr><td colspan='6'>no org/projects/*.md files yet</td></tr>",
        "project_panes": "\n\n".join(proj_panes),
        "pings": "\n".join(pings_html) or '<div class="empty">no open pings</div>',
        "agents": "\n".join(agent_rows) or "<tr><td colspan='7'>no agent files yet</td></tr>",
        "inboxes": "\n".join(inbox_rows) or "<tr><td colspan='2'>none</td></tr>",
        "decisions": "\n".join(decision_rows) or "<tr><td colspan='4'>no decisions yet</td></tr>",
        "memory": "\n".join(mem_rows) or "<tr><td colspan='5'>no memory yet</td></tr>",
        "builds": "\n".join(build_rows) or "<tr><td colspan='5'>no builds recorded yet</td></tr>",
        "events": "\n".join(event_rows) or "<tr><td colspan='5'>no events yet</td></tr>",
    }

    DASHBOARD.mkdir(parents=True, exist_ok=True)
    (DASHBOARD / "index.html").write_text(html, encoding="utf-8")
    return len(cards)


def generate_board():
    """Plain-text board for agents (kept for tools that read markdown)."""
    cards = load_md_with_body(ORG / "cards")
    for c in cards:
        c["column"] = c.get("column", "backlog")
        if c["column"] not in KNOWN_COLUMNS:
            c["column"] = "backlog"
    lines = ["# Templeton Board\n"]
    for col in COLUMNS:
        items = [c for c in cards if c.get("column") == col]
        lines.append("## %s" % col)
        for c in items:
            lines.append("- **%s**: %s (assignee: %s)"
                         % (c.get("id", "?"), c.get("title", ""), c.get("assignee", "-")))
        lines.append("")
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "BOARD.md").write_text("\n".join(lines), encoding="utf-8")


def generate_projects():
    """Plain-text project ledger for agents — same scope rules as the pages."""
    projects = load_projects()
    cards = load_md_with_body(ORG / "cards")
    for c in cards:
        c["column"] = c.get("column", "backlog")
        if c["column"] not in KNOWN_COLUMNS:
            c["column"] = "backlog"
    builds = load_md_with_body(ORG / "builds")
    events = load_events(limit=None)
    project_of = project_scopes(projects, cards, builds)

    lines = ["# Templeton Projects\n",
             "generated by worker/dashboard.py — a view of org/projects/*.md, not a source\n"]
    for p in sorted(projects, key=lambda p: p.get("id", "")):
        pid = p.get("id", "?")
        pcards = [c for c in cards if c.get("project") == pid]
        pbuilds = sorted((b for b in builds if b.get("project") == pid),
                         key=lambda b: b.get("ts") or b.get("id") or "",
                         reverse=True)
        open_cards = [c for c in pcards if c.get("column") != "done"]
        streak = build_streak(pbuilds)
        nev = sum(1 for e in events if project_of(e) == pid)
        lines.append("## %s (%s)" % (pid, p.get("title", "")))
        lines.append("- status: %s | repo: %s | memory cell: %s"
                     % (p.get("status", "?"), p.get("repo") or "local only",
                        p.get("memory_cell", "-")))
        lines.append("- cards: %d open / %d done%s"
                     % (len(open_cards), len(pcards) - len(open_cards),
                        "" if open_cards else " (nothing open)"))
        for c in sorted(open_cards, key=lambda c: c.get("id", "")):
            lines.append("  - %s [%s]: %s" % (c.get("id", "?"),
                                              c.get("column", "?"),
                                              c.get("title", "")))
        lines.append("- builds: %d pass / %d fail | current streak: %s"
                     % (sum(1 for b in pbuilds if b.get("status") == "pass"),
                        sum(1 for b in pbuilds if b.get("status") == "fail"),
                        "%s of %d" % streak if streak[0] else "none"))
        lines.append("- events scoped here: %d" % nev)
        body = (p.get("_body") or "").strip()
        first = next((ln.strip() for ln in body.splitlines()
                      if ln.strip() and not ln.startswith("#")), "")
        if first:
            lines.append("- from the project artifact: %s" % first)
        lines.append("")
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "PROJECTS.md").write_text("\n".join(lines), encoding="utf-8")


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
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
  .tabs { display: flex; gap: 4px; margin: 14px 0 6px; border-bottom: 1px solid var(--border); }
  .tabs a { padding: 8px 16px; color: var(--dim); text-decoration: none; font-weight: 600;
            font-size: 13px; border: 1px solid transparent; border-bottom: none;
            border-radius: 6px 6px 0 0; }
  .tabs a:hover { color: var(--text); background: var(--panel); }
  .tabs a.active { color: var(--text); background: var(--panel); border-color: var(--border); }
  .pane { display: none; }
  .pane.active { display: block; }
  .board { display: flex; gap: 12px; align-items: flex-start; overflow-x: auto; padding-bottom: 8px; }
  .kcol { background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
          min-width: 240px; flex: 1; padding: 10px; }
  .kcol-head { font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;
               color: var(--dim); display: flex; justify-content: space-between; padding: 2px 4px 8px; }
  .kcount { background: var(--border); border-radius: 10px; padding: 0 8px; }
  .card { background: #1c2129; border: 1px solid var(--border); border-left: 3px solid var(--dim);
          border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; }
  .clickable { cursor: pointer; }
  .card.clickable:hover, tr.clickable:hover, .pingrow:hover { outline: 1px solid var(--accent); }
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
  .pingrow { background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
             padding: 10px 12px; margin-bottom: 8px; }
  .pingrow.to-brad { border-left: 3px solid var(--red); }
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
  .dim { color: var(--dim); font-weight: 400; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  a { color: var(--accent); text-decoration: none; }
  /* drawer */
  .drawer-backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 40; }
  .drawer { position: fixed; top: 0; right: -560px; width: 540px; max-width: 92vw; height: 100vh;
            background: var(--panel); border-left: 1px solid var(--border); z-index: 50;
            transition: right .18s ease; overflow-y: auto; padding: 20px 24px 40px; }
  .drawer.open { right: 0; }
  .drawer-backdrop.open { display: block; }
  .drawer-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .drawer-title { font-size: 16px; font-weight: 700; }
  .drawer-close { background: none; border: 1px solid var(--border); color: var(--dim);
                  border-radius: 6px; font-size: 16px; cursor: pointer; padding: 2px 10px; }
  .drawer-close:hover { color: var(--text); }
  .drawer-meta { width: 100%%; margin: 10px 0; border-collapse: collapse; }
  .drawer-meta td { padding: 3px 10px 3px 0; font-size: 12px; border: none; }
  .drawer-meta td:first-child { color: var(--dim); font-family: Consolas, monospace; width: 110px; }
  .drawer-body { white-space: pre-wrap; font-size: 13px; background: #10151c;
                 border: 1px solid var(--border); border-radius: 8px; padding: 14px; }
  .drawer-src { margin-top: 10px; font-size: 12px; }
  .msglist { list-style: none; padding: 0; margin: 10px 0; }
  .msglist li { background: #1c2129; border: 1px solid var(--border); border-radius: 6px;
               padding: 8px 12px; margin-bottom: 8px; cursor: pointer; font-size: 13px; }
  .msglist li:hover { outline: 1px solid var(--accent); }
  .msglist .dim { display: block; font-size: 11px; }
  /* project pages */
  .crumb { font-size: 12px; color: var(--dim); margin-bottom: 6px; }
  .prose { background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
           padding: 12px 16px; margin: 12px 0 20px; max-width: 900px; }
  .prose p { margin: 0 0 10px; }
  .prose p:last-child { margin-bottom: 0; }
  pre.cell, .prose code { font-family: Consolas, monospace; font-size: 12px; }
  .prose code { background: #21262d; border-radius: 4px; padding: 1px 5px; }
  pre.cell { background: #10151c; border: 1px solid var(--border); border-radius: 8px;
             padding: 14px; white-space: pre-wrap; margin: 0 0 6px; max-width: 900px; }
  .refresh-note { position: fixed; bottom: 14px; right: 20px; color: var(--dim); font-size: 11px; }
</style>
</head>
<body>
<h1>Templeton Systems <span style="color:var(--dim);font-weight:400">— Org Dashboard</span></h1>
<div class="sub">generated %(ts)s &nbsp;·&nbsp; F:\\Lab &nbsp;·&nbsp; <a href="#board">Board</a> · <a href="#projects">Projects</a> · <a href="#pings">Pings</a> · <a href="#roster">Roster</a> · <a href="#memory">Memory</a> · <a href="#builds">Builds</a> · <a href="#events">Events</a></div>

<nav class="tabs">
  <a href="#board" class="tab" data-tab="board">Board</a>
  <a href="#projects" class="tab" data-tab="projects">Projects</a>
  <a href="#pings" class="tab" data-tab="pings">Pings</a>
  <a href="#roster" class="tab" data-tab="roster">Roster</a>
  <a href="#memory" class="tab" data-tab="memory">Memory</a>
  <a href="#builds" class="tab" data-tab="builds">Builds</a>
  <a href="#events" class="tab" data-tab="events">Events</a>
</nav>

<section class="pane" data-pane="board">
<h2>Kanban</h2>
<div class="board">
%(board)s
</div>
</section>

<section class="pane" data-pane="projects">
<h2>Projects</h2>
<p class="sub">every project the org works in — click a row for its page: what it is, where it's at, and everything done in it</p>
<table>
<tr><th>Project</th><th>Status</th><th>Repo</th><th>Cards</th><th>Builds</th><th>Events</th></tr>
%(projects)s
</table>
</section>

%(project_panes)s

<section class="pane" data-pane="pings">
<h2>Pings</h2>
<p class="sub">click a ping to open the full message</p>
%(pings)s
</section>

<section class="pane" data-pane="roster">
<h2>Agents</h2>
<table>
<tr><th>Name</th><th>Role</th><th>Status</th><th>Scope</th><th>Schedule</th><th>Heartbeat</th></tr>
%(agents)s
</table>

<h2>Inboxes</h2>
<table>
<tr><th>Agent</th><th>Unread</th></tr>
%(inboxes)s
</table>

<h2>Decisions</h2>
<table>
<tr><th>ID</th><th>Date</th><th>Status</th><th>Title</th></tr>
%(decisions)s
</table>
</section>

<section class="pane" data-pane="memory">
<h2>Qwen's Memory — the Lattice</h2>
<p class="sub">hot tier + warm cells — click to open · recall: python worker\\recall.py · write: python worker\\remember.py</p>
<table>
<tr><th>Cell</th><th>Kind</th><th>Key</th><th>Updated</th><th>First line</th></tr>
%(memory)s
</table>
</section>

<section class="pane" data-pane="builds">
<h2>Builds</h2>
<table>
<tr><th>ID</th><th>Target</th><th>Agent</th><th>Status</th><th>TS</th></tr>
%(builds)s
</table>
</section>

<section class="pane" data-pane="events">
<h2>Recent Events</h2>
<p class="sub">newest first, last 20 of the log — project column resolved from ctx refs</p>
<table>
<tr><th>TS</th><th>Agent</th><th>Type</th><th>Ref</th><th>Project</th></tr>
%(events)s
</table>
</section>

<div class="drawer-backdrop" id="dbk"></div>
<aside class="drawer" id="drawer">
  <div class="drawer-head"><span class="drawer-title" id="dtitle"></span><button class="drawer-close" id="dclose">✕</button></div>
  <div id="dcontent"></div>
</aside>

<script type="application/json" id="artifacts">
%(artifacts)s
</script>
<script>
(function () {
  var ARTS = {};
  try { ARTS = JSON.parse(document.getElementById('artifacts').textContent); } catch (e) {}
  var esc = function (s) { return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };

  // ---- tabs ----
  var tabs = document.querySelectorAll('.tab');
  function activate(name) {
    document.querySelectorAll('.pane').forEach(function (p) {
      p.classList.toggle('active', p.getAttribute('data-pane') === name);
    });
    var tab = name.indexOf('proj/') === 0 ? 'projects' : name;
    tabs.forEach(function (t) {
      t.classList.toggle('active', t.getAttribute('data-tab') === tab);
    });
  }
  function fromHash() {
    var h = location.hash.replace('#', '') || 'board';
    activate(document.querySelector('.pane[data-pane="' + h + '"]') ? h : 'board');
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();

  // ---- drawer ----
  var drawer = document.getElementById('drawer');
  var dbk = document.getElementById('dbk');
  var dtitle = document.getElementById('dtitle');
  var dcontent = document.getElementById('dcontent');

  function metaTable(meta) {
    var rows = '';
    Object.keys(meta).forEach(function (k) {
      rows += '<tr><td>' + esc(k) + '</td><td>' + esc(meta[k]) + '</td></tr>';
    });
    return '<table class="drawer-meta">' + rows + '</table>';
  }
  function openArt(kind, id, title) {
    var a = ARTS[kind] || {};
    var item = a[id];
    if (!item) { closeDrawer(); return; }
    dtitle.textContent = title || id;
    var html = metaTable(item.meta || {});
    if (item.body) html += '<div class="drawer-body">' + esc(item.body) + '</div>';
    if (item.path) html += '<div class="drawer-src">source: <a href="../' + esc(item.path) + '" target="_blank">' + esc(item.path) + '</a></div>';
    dcontent.innerHTML = html;
    drawer.classList.add('open');
    dbk.classList.add('open');
  }
  function openInbox(id) {
    var msgs = (ARTS.inbox || {})[id] || [];
    dtitle.textContent = 'Inbox — ' + id;
    var html = '<p class="sub">' + msgs.length + ' unread message(s)</p>';
    if (msgs.length) {
      html += '<ul class="msglist">';
      msgs.forEach(function (m) {
        html += '<li data-rel="' + esc(m.rel) + '">' + esc(m.subject)
              + '<span class="dim">from ' + esc(m.from) + ' · ' + esc(m.file) + '</span></li>';
      });
      html += '</ul>';
    }
    dcontent.innerHTML = html;
    drawer.classList.add('open');
    dbk.classList.add('open');
  }
  function openMsg(rel) {
    var a = ARTS.pings || {};
    var item = a[rel] || { meta: {}, body: '' };
    // fall back to inbox bodies if not an open ping
    var found = item.body;
    if (!found) {
      Object.keys(ARTS.inbox || {}).forEach(function (k) {
        (ARTS.inbox[k] || []).forEach(function (m) {
          if (m.rel === rel) found = m.body;
        });
      });
    }
    dtitle.textContent = rel.split('/').pop();
    var html = metaTable(item.meta || { source: rel });
    if (found) html += '<div class="drawer-body">' + esc(found) + '</div>';
    html += '<div class="drawer-src">source: <a href="../' + esc(rel) + '" target="_blank">' + esc(rel) + '</a></div>';
    dcontent.innerHTML = html;
    drawer.classList.add('open');
    dbk.classList.add('open');
  }
  function closeDrawer() {
    drawer.classList.remove('open');
    dbk.classList.remove('open');
  }
  document.getElementById('dclose').addEventListener('click', closeDrawer);
  dbk.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeDrawer(); });

  // ---- click routing ----
  document.addEventListener('click', function (e) {
    var li = e.target.closest && e.target.closest('.msglist li[data-rel]');
    if (li) { openMsg(li.getAttribute('data-rel')); return; }
    // an explicit link wins — let it navigate (project pages, source files)
    if (e.target.closest && e.target.closest('a')) return;
    var el = e.target.closest && e.target.closest('[data-kind]');
    if (!el) return;
    var kind = el.getAttribute('data-kind');
    var id = el.getAttribute('data-id');
    if (kind === 'card') openArt('cards', id, id);
    else if (kind === 'agent') openArt('agents', id, id);
    else if (kind === 'build') openArt('builds', id, id);
    else if (kind === 'decision') openArt('decisions', id, id);
    else if (kind === 'ping') openMsg(id);
    else if (kind === 'inbox') openInbox(id);
    else if (kind === 'memory') openArt('memory', id, id);
    else if (kind === 'project') openArt('projects', id, id);
  });
})();
</script>

<div class="refresh-note">Templeton Systems · F:\\Lab</div>
</body>
</html>
"""


if __name__ == "__main__":
    n = build_page()
    generate_board()
    generate_projects()
    print("dashboard v2 generated: %d card(s) -> F:\\Lab\\dashboard\\index.html" % n)
