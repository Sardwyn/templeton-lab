"""Append-only writes for the HQ dashboard.

Card frontmatter is the current state (check-in: cards move by editing their
own file). History is a new line in org/events, or a new inbox file. This
module never deletes a file, never rewrites an event line, and never opens
org/decisions.
"""
import datetime
import json
import os
import re
from pathlib import Path

# Same columns as check-in.md and dashboard.COLUMNS.
COLUMNS = ("backlog", "in-progress", "review", "done", "blocked")
PRIORITIES = ("", "low", "med", "high", "urgent")
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
CARD_RE = re.compile(r"^card-\d{3}$")


class RecordError(ValueError):
    """A write the dashboard should refuse, before anything is changed."""


def read_text(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    if "\r\n" in text:
        return text.replace("\r\n", "\n"), "\r\n"
    return text, "\n"


def write_bytes(path, text, nl):
    if text and not text.endswith("\n"):
        text += "\n"
    data = text.replace("\n", nl).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def atomic_write(path, text, nl):
    tmp = path.with_name(path.name + ".tmp")
    try:
        write_bytes(tmp, text, nl)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def split_frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        return None, text
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields, text[match.end():]


def patch_frontmatter(text, updates):
    """Replace or drop named keys. Every other line, including the body, stays."""
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        raise RecordError("card has no frontmatter")
    lines = match.group(1).splitlines()
    seen = set()
    out = []
    for line in lines:
        if ":" in line and not line[:1].isspace():
            key = line.split(":", 1)[0].strip()
            if key in updates:
                seen.add(key)
                value = updates[key]
                if value in (None, ""):
                    continue
                out.append("%s: %s" % (key, value))
                continue
        out.append(line)
    for key, value in updates.items():
        if key not in seen and value not in (None, ""):
            out.append("%s: %s" % (key, value))
    return "---\n" + "\n".join(out) + "\n---" + text[match.end():]


def append_paragraph(text, line):
    if text and not text.endswith("\n"):
        text += "\n"
    if text and not text.endswith("\n\n"):
        text += "\n"
    return text + line + "\n"


def agent_ids(root):
    folder = root / "org" / "agents"
    found = []
    if not folder.is_dir():
        return found
    for path in sorted(folder.glob("*.md")):
        text, _nl = read_text(path)
        fields, _body = split_frontmatter(text)
        agent_id = ((fields or {}).get("id") or path.stem).strip()
        if ID_RE.fullmatch(agent_id):
            found.append(agent_id)
    return found


def inbox_ids(root):
    folder = root / "org" / "inbox"
    if not folder.is_dir():
        return []
    return sorted(
        path.name for path in folder.iterdir()
        if path.is_dir() and ID_RE.fullmatch(path.name)
    )


def append_event(root, agent, type_, **ctx):
    """One new JSON line. Existing lines in the file are not opened for write
    except by append mode."""
    events = root / "org" / "events"
    events.mkdir(parents=True, exist_ok=True)
    path = events / (datetime.date.today().isoformat() + ".jsonl")
    entry = {
        "ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "agent": agent,
        "type": type_,
    }
    for key, value in ctx.items():
        if value not in (None, ""):
            entry[key] = value
    line = json.dumps(entry, ensure_ascii=True) + "\n"
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
    return entry


def _require_actor(root, actor):
    actor = (actor or "").strip()
    if actor not in agent_ids(root):
        raise RecordError("actor must be an agent already on the roster")
    return actor


def _card_path(root, card_id):
    card_id = (card_id or "").strip()
    if not CARD_RE.fullmatch(card_id):
        raise RecordError("card id must look like card-021")
    path = root / "org" / "cards" / ("%s.md" % card_id)
    if not path.is_file():
        raise RecordError("no card file %s" % card_id)
    return card_id, path


def _project_of_card(fields):
    project = (fields.get("project") or "").strip()
    if project and not ID_RE.fullmatch(project):
        return ""
    return project


def _normalize_note(note, limit, label):
    text = " ".join((note or "").replace("\r", " ").split())
    if len(text) > limit:
        raise RecordError("%s is too long" % label)
    return text


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    slug = slug[:40].strip("-")
    return slug or "note"


def _message_path(folder, subject, now):
    stamp = now.strftime("%Y%m%d-%H%M")
    base = "%s-%s" % (stamp, slugify(subject))
    candidate = folder / ("%s.md" % base)
    number = 2
    while candidate.exists():
        candidate = folder / ("%s-%d.md" % (base, number))
        number += 1
        if number > 50:
            raise RecordError("too many messages with that subject this minute")
    return candidate


def write_message(root, actor, to, subject, body, project="", card="", now=None):
    """New inbox file plus one message event. Does not touch older messages."""
    actor = _require_actor(root, actor)
    to = (to or "").strip()
    if to not in inbox_ids(root):
        raise RecordError("no inbox for that recipient")
    subject = _normalize_note(subject, 160, "subject")
    if not subject:
        raise RecordError("a message needs a subject")
    body = (body or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not body:
        raise RecordError("write something first")
    if len(body) > 4000:
        raise RecordError("keep a message under 4000 characters")
    project = (project or "").strip()
    card = (card or "").strip()
    if project and not _project_file(root, project):
        raise RecordError("unknown project")
    if card:
        card, _path = _card_path(root, card)
    now = now or datetime.datetime.now()
    folder = root / "org" / "inbox" / to
    path = _message_path(folder, subject, now)
    lines = ["---", "from: %s" % actor, "to: %s" % to, "subject: %s" % subject]
    if project:
        lines.append("project: %s" % project)
    if card:
        lines.append("card: %s" % card)
    lines.extend(["---", "", body, ""])
    write_bytes(path, "\n".join(lines), "\n")
    rel = path.relative_to(root).as_posix()
    entry = append_event(
        root, actor, "message",
        file=rel, to=to, subject=subject, project=project, card=card, note=subject,
    )
    return {"path": rel, "event": entry}


def _project_file(root, project):
    if not ID_RE.fullmatch(project or ""):
        return None
    path = root / "org" / "projects" / ("%s.md" % project)
    return path if path.is_file() else None


def post_thread(root, actor, kind, body, to="", subject="", project="", card=""):
    """A thread post. note -> one event. message -> inbox file + event."""
    kind = (kind or "").strip()
    if kind not in ("note", "message"):
        raise RecordError("post a note or a message")
    actor = _require_actor(root, actor)
    project = (project or "").strip()
    card = (card or "").strip()
    if card:
        card, card_path = _card_path(root, card)
        text, _nl = read_text(card_path)
        fields, _body = split_frontmatter(text)
        card_project = _project_of_card(fields or {})
        if project and card_project and project != card_project:
            raise RecordError("that card is not in the selected project")
        if not project:
            project = card_project
    if project and not _project_file(root, project):
        raise RecordError("unknown project")
    if kind == "message":
        return write_message(
            root, actor, to, subject, body, project=project, card=card)
    text = (body or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        raise RecordError("write something first")
    if len(text) > 4000:
        raise RecordError("keep a note under 4000 characters")
    entry = append_event(
        root, actor, "note", project=project, card=card, note=text)
    return {"path": "", "event": entry}


def update_card(root, card_id, actor, column=None, assignee=None,
                priority=None, due=None, note=""):
    """Change current card fields and append one event describing the diff.

    A field left as None is not part of this save. An empty priority or due
    clears that key. Returns changed=False when the save matches the file.
    """
    actor = _require_actor(root, actor)
    card_id, path = _card_path(root, card_id)
    original, nl = read_text(path)
    fields, body = split_frontmatter(original)
    if fields is None:
        raise RecordError("card has no frontmatter")
    current_column = (fields.get("column") or "backlog").strip() or "backlog"
    current_assignee = (fields.get("assignee") or "unassigned").strip() or "unassigned"
    current_priority = (fields.get("priority") or "").strip().lower()
    current_due = (fields.get("due") or "").strip()
    note = _normalize_note(note, 500, "note")

    changes = {}
    if column is not None:
        column = column.strip()
        if column != current_column and column not in COLUMNS:
            raise RecordError(
                "column must be backlog, in-progress, review, done, or blocked")
        if column != current_column:
            changes["column"] = column
    if assignee is not None:
        assignee = assignee.strip() or "unassigned"
        known = set(agent_ids(root)) | {"unassigned", current_assignee}
        if assignee not in known:
            raise RecordError("assignee must be unassigned or an agent on the roster")
        if assignee != current_assignee:
            changes["assignee"] = assignee
    if priority is not None:
        priority = priority.strip().lower()
        allowed = set(PRIORITIES)
        if current_priority:
            allowed.add(current_priority)
        if priority not in allowed:
            raise RecordError("priority must be urgent, high, med, low, or empty")
        if priority != current_priority:
            changes["priority"] = priority
    if due is not None:
        due = due.strip()
        if due and not _real_date(due):
            raise RecordError("due date must be YYYY-MM-DD")
        if due != current_due:
            changes["due"] = due
    if not changes and not note:
        return {"changed": False, "event": None, "summary": ""}

    new_column = changes.get("column", current_column)
    blocking = new_column == "blocked" and current_column != "blocked"
    if blocking and not note:
        raise RecordError(
            "moving to blocked needs a note saying what decision is needed")
    if blocking and "brad" not in inbox_ids(root):
        raise RecordError("no inbox for brad, so the blocked card cannot ask for a decision")

    summary = _summary(fields, changes, note)
    stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    updates = dict(changes)
    updates["updated_at"] = stamp
    rewritten = patch_frontmatter(original, updates)
    line = "_Dashboard %s (%s): %s._" % (stamp, actor, summary)
    rewritten = append_paragraph(rewritten, line)
    atomic_write(path, rewritten, nl)

    if "column" in changes and changes["column"] == "in-progress":
        event_type = "card_claim"
    elif "column" in changes and changes["column"] == "done":
        event_type = "card_done"
    else:
        event_type = "card_update"
    try:
        entry = append_event(
            root, actor, event_type,
            card=card_id, project=_project_of_card(fields), note=summary,
        )
    except Exception:
        # The event line was not written. Put the card file back so the
        # record does not claim a move that the log does not have.
        atomic_write(path, original, nl)
        raise
    if blocking:
        title = " ".join((fields.get("title") or card_id).split())
        write_message(
            root, actor, "brad",
            "blocked: %s" % title[:140],
            note,
            project=_project_of_card(fields),
            card=card_id,
        )
    return {"changed": True, "event": entry, "summary": summary}


def _real_date(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def set_project_archived(root, project_id, actor, archived):
    """Hide or restore a project's board.

    status: archived is current state on org/projects/<id>.md. The previous
    status comes back on unarchive. A project that exists only as a card
    reference gets a minimal project file on archive. Nothing is deleted.
    """
    actor = _require_actor(root, actor)
    project_id = (project_id or "").strip()
    if project_id == "unscoped" or not ID_RE.fullmatch(project_id or ""):
        raise RecordError("that is not a project")
    path = root / "org" / "projects" / ("%s.md" % project_id)
    if archived:
        return _archive_project(root, path, project_id, actor)
    return _unarchive_project(root, path, project_id, actor)


def _archive_project(root, path, project_id, actor):
    stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    if path.is_file():
        original, nl = read_text(path)
        fields, _body = split_frontmatter(original)
        if fields is None:
            raise RecordError("project has no frontmatter")
        prior = (fields.get("status") or "").strip() or "active"
        if prior.lower() == "archived":
            return {"changed": False, "event": None, "summary": ""}
        rewritten = patch_frontmatter(original, {
            "status": "archived",
            "updated_at": stamp,
        })
        atomic_write(path, rewritten, nl)
        note = "status %s -> archived" % prior
        created = False
    else:
        if not _cards_name_project(root, project_id):
            raise RecordError("no such project")
        prior = "active"
        original = None
        nl = "\n"
        created = True
        path.parent.mkdir(parents=True, exist_ok=True)
        write_bytes(path, (
            "---\n"
            "id: %s\n"
            "title: %s\n"
            "status: archived\n"
            "updated_at: %s\n"
            "---\n\n"
        ) % (project_id, project_id, stamp), "\n")
        note = "created org/projects/%s.md; status -> archived" % project_id
    try:
        entry = append_event(
            root, actor, "project_archive",
            project=project_id, prior_status=prior, note=note,
        )
    except Exception:
        if created:
            if path.is_file():
                path.unlink()
        else:
            atomic_write(path, original, nl)
        raise
    return {"changed": True, "event": entry, "summary": note}


def _unarchive_project(root, path, project_id, actor):
    if not path.is_file():
        raise RecordError("no such project")
    original, nl = read_text(path)
    fields, _body = split_frontmatter(original)
    if fields is None:
        raise RecordError("project has no frontmatter")
    current = (fields.get("status") or "").strip()
    if current.lower() != "archived":
        return {"changed": False, "event": None, "summary": ""}
    restored = _archived_from(root, project_id)
    stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    rewritten = patch_frontmatter(original, {
        "status": restored,
        "updated_at": stamp,
    })
    atomic_write(path, rewritten, nl)
    note = "status archived -> %s" % restored
    try:
        entry = append_event(
            root, actor, "project_unarchive",
            project=project_id, note=note,
        )
    except Exception:
        atomic_write(path, original, nl)
        raise
    return {"changed": True, "event": entry, "summary": note}


def _cards_name_project(root, project_id):
    folder = root / "org" / "cards"
    if not folder.is_dir():
        return False
    for path in folder.glob("*.md"):
        text, _nl = read_text(path)
        fields, _body = split_frontmatter(text)
        if fields and (fields.get("project") or "").strip() == project_id:
            return True
    return False


def _archived_from(root, project_id):
    """Previous status recorded on the latest project_archive line."""
    folder = root / "org" / "events"
    prior = ""
    if folder.is_dir():
        for path in sorted(folder.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if (entry.get("type") == "project_archive"
                        and entry.get("project") == project_id
                        and entry.get("prior_status")):
                    prior = entry["prior_status"]
    if not prior or prior.lower() == "archived":
        return "active"
    return prior


def _summary(fields, changes, note):
    parts = []
    labels = (
        ("column", "column"),
        ("assignee", "assignee"),
        ("priority", "priority"),
        ("due", "due"),
    )
    current = {
        "column": (fields.get("column") or "backlog").strip(),
        "assignee": (fields.get("assignee") or "unassigned").strip(),
        "priority": (fields.get("priority") or "").strip(),
        "due": (fields.get("due") or "").strip(),
    }
    for key, label in labels:
        if key not in changes:
            continue
        before = current[key] or "none"
        after = changes[key] or "none"
        parts.append("%s %s -> %s" % (label, before, after))
    if note:
        parts.append(note)
    return "; ".join(parts)
