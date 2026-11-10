"""Board and thread HTML for the HQ dashboard.

Rendering only. Writes happen in mutate.py, through worker/serve.py.
"""
import datetime

COLUMNS = ("backlog", "in-progress", "review", "done", "blocked")
PRIO_RANK = {"urgent": 0, "high": 1, "med": 2, "low": 3}

EXTRA_CSS = """
.acting { margin-left: 12px; }
.acting select, .card-form select, .card-form input, .composer select,
.composer input, .composer textarea {
  background: #0d1117; color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; padding: 4px 8px; font: inherit;
}
.card-form button, .composer button {
  background: #21262d; color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; padding: 4px 10px; cursor: pointer; font: inherit;
}
.card-form button:hover, .composer button:hover { border-color: var(--accent); }
.proj-picker { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 14px; }
.proj-picker a {
  border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px;
  color: var(--dim); background: transparent;
}
.proj-picker a.is-current { color: var(--text); border-color: var(--accent); background: #21262d; }
.kanban { display: none; gap: 12px; align-items: stretch; overflow-x: auto; padding-bottom: 16px; }
.kanban.is-current { display: flex; }
.lane {
  flex: 1 0 240px; min-width: 240px; max-width: 340px; background: #12171e;
  border: 1px solid var(--border); border-radius: 10px; min-height: 320px;
  display: flex; flex-direction: column;
}
.lane.drop-hover { outline: 2px solid var(--accent); outline-offset: -2px; }
.lane-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px 8px; font-size: 12px; font-weight: 700;
  letter-spacing: 0.04em; text-transform: uppercase;
}
.lane-backlog .lane-head { color: var(--dim); }
.lane-in-progress .lane-head { color: var(--accent); }
.lane-review .lane-head { color: var(--yellow); }
.lane-blocked .lane-head { color: var(--red); }
.lane-done .lane-head { color: var(--green); }
.collapse-done {
  background: none; border: none; color: inherit; font: inherit;
  letter-spacing: inherit; text-transform: inherit; cursor: pointer; padding: 0;
}
.lane-cards { display: flex; flex-direction: column; gap: 8px; padding: 0 8px 10px; min-height: 96px; }
.lane.is-collapsed .lane-cards { display: none; }
.tile {
  background: #1c2129; border: 1px solid var(--border); border-left: 4px solid var(--dim);
  border-radius: 8px; padding: 10px 12px; cursor: grab;
}
.tile:active { cursor: grabbing; }
.tile.dragging { opacity: 0.45; }
.tile.col-in-progress { border-left-color: var(--accent); }
.tile.col-review { border-left-color: var(--yellow); }
.tile.col-blocked { border-left-color: var(--red); }
.tile.col-done { border-left-color: var(--green); }
.tile-title { font-weight: 650; margin: 4px 0 2px; }
.tile-id { font-family: Consolas, monospace; font-size: 12px; }
.tile-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; align-items: center; }
.pill {
  font-size: 11px; font-weight: 700; border-radius: 999px; padding: 1px 8px;
  border: 1px solid var(--border); text-transform: uppercase; letter-spacing: 0.03em;
}
.pill.owner { color: var(--accent); font-weight: 600; text-transform: none; letter-spacing: 0; }
.pill.owner.dim { color: var(--dim); }
.pill.status-backlog { color: var(--dim); }
.pill.status-in-progress { color: var(--accent); border-color: var(--accent); }
.pill.status-review { color: var(--yellow); border-color: var(--yellow); }
.pill.status-blocked { color: var(--red); border-color: var(--red); }
.pill.status-done { color: var(--green); border-color: var(--green); }
.pill.p-urgent, .pill.p-high { color: var(--red); border-color: var(--red); }
.pill.p-med { color: var(--yellow); border-color: var(--yellow); }
.pill.p-low { color: var(--dim); }
.pill.due { text-transform: none; letter-spacing: 0; font-weight: 600; color: var(--text); }
.pill.due.overdue { color: var(--red); border-color: var(--red); }
.edit-panel[hidden] { display: none; }
.modal[hidden] { display: none; }
.modal {
  position: fixed; inset: 0; background: rgba(0,0,0,.55); z-index: 80;
  display: flex; align-items: center; justify-content: center;
}
.modal form {
  background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
  padding: 16px 18px; width: 440px; max-width: 92vw;
}
.modal-title { font-size: 16px; font-weight: 700; margin: 0 0 8px; }
.modal textarea {
  width: 100%; min-height: 88px; display: block; margin: 8px 0;
  background: #0d1117; color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; padding: 8px; font: inherit;
}
.modal button {
  background: #21262d; color: var(--text); border: 1px solid var(--border);
  border-radius: 6px; padding: 4px 10px; cursor: pointer; font: inherit;
}
.modal button[type="submit"] { border-color: var(--red); color: var(--red); }
.modal .row { display: flex; gap: 8px; }
.block-error { color: var(--red); font-size: 13px; }
.card-form { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.card-form label, .composer label {
  display: flex; gap: 4px; align-items: center; color: var(--dim); font-size: 11px;
}
.card-form details { flex-basis: 100%; }
.fields { display: flex; flex-wrap: wrap; gap: 8px; padding: 8px 0; }
.prio { font-size: 11px; font-weight: 700; text-transform: uppercase; }
.p-urgent, .p-high { color: var(--red); }
.p-med { color: var(--yellow); }
.p-low { color: var(--dim); }
.overdue { color: var(--red); font-weight: 700; }
.slack {
  display: flex; min-height: 640px; border: 1px solid var(--border);
  border-radius: 8px; background: var(--panel);
}
.ch-list {
  width: 240px; flex: 0 0 240px; border-right: 1px solid var(--border);
  padding: 8px; overflow: auto; max-height: 80vh;
}
.ch-list a { display: block; padding: 4px 8px; border-radius: 6px; color: var(--text); }
.ch-list a.active { background: #21262d; color: var(--accent); }
.ch-h {
  font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
  color: var(--dim); margin: 12px 8px 4px;
}
.thread { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.timeline { flex: 1; overflow: auto; padding: 12px 16px; max-height: 68vh; }
.msg { padding: 8px 0; border-bottom: 1px solid var(--border); }
.msg-subject { font-weight: 600; margin-top: 2px; }
.msg-text { white-space: pre-wrap; margin-top: 4px; }
.chip {
  font-size: 10px; border: 1px solid var(--border); border-radius: 999px;
  padding: 0 6px; color: var(--dim); margin-left: 4px;
}
.chip.ping { color: var(--red); border-color: var(--red); }
.composer { border-top: 1px solid var(--border); padding: 10px 12px; }
.composer textarea { width: 100%; min-height: 72px; display: block; margin: 6px 0; }
.composer .row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
"""


# Always-visible lanes. Any other status a card actually uses is inserted
# after in-progress (review lands there, which is where check-in puts it).
LANES = ("backlog", "in-progress", "blocked", "done")


def board_views(cards, projects, agents, ref_cell, esc, today):
    agent_ids = [a.get("id") for a in agents if a.get("id")]
    catalog = _catalog(cards, projects)
    default = _default_project(catalog, cards)
    open_n = sum(1 for c in cards if (c.get("column") or "") != "done")
    intro = ("%d open. Drag a card to another column to change its status. "
             "That writes the card and appends one event. Done can collapse, and it stays a column."
             % open_n)
    order = sorted(catalog, key=lambda pid: (-_open_count(pid, cards), pid))
    tabs = []
    boards = []
    for pid in order:
        project = catalog[pid]
        owned = _cards_for(pid, cards)
        current = " is-current" if pid == default else ""
        title = project.get("title") or pid
        tabs.append(
            "<a href='#board/%s' data-project='%s' class='%s'>%s <span class='kcount'>%d</span></a>"
            % (esc(pid), esc(pid), current.strip(), esc(title), _open_count(pid, cards)))
        boards.append(
            "<div class='kanban%s' data-project='%s'>%s</div>"
            % (current, esc(pid), _lanes(owned, agent_ids, esc, today, pid)))
    modal = (
        "<div class='modal' id='block-modal' hidden>"
        "<form id='block-form'>"
        "<p class='modal-title'>Move to blocked</p>"
        "<p class='sub'>What decision is needed? The note is filed in Brad's inbox "
        "and appended to the event log.</p>"
        "<textarea name='note' required "
        "placeholder='The decision this card is waiting on'></textarea>"
        "<p class='block-error' id='block-error' hidden></p>"
        "<div class='row'><button type='submit'>Move to blocked</button>"
        "<button type='button' id='block-cancel'>Cancel</button></div>"
        "</form></div>"
    )
    html = (
        "<div id='hq-board' data-default='%s'>"
        "<nav class='proj-picker' aria-label='Project'>%s</nav>%s%s</div>"
        % (esc(default), "".join(tabs), "".join(boards), modal)
    )
    return intro, html


def thread_panes(cards, projects, agents, events, messages,
                 ref_cell, esc, linkify, pointer, names, project_of):
    agent_ids = [a.get("id") for a in agents if a.get("id")]
    channels, buckets = _assemble(
        cards, projects, agents, events, messages, pointer, names, project_of, ref_cell)
    chunks = [_pane_shell(
        "threads", channels, "", esc,
        "<div class='thread'><div class='timeline'>"
        "<h2>Threads</h2>"
        "<p class='sub'>One channel per project and per agent. The timeline is "
        "org/events plus org/inbox, including messages already filed under done/. "
        "A note appends one event. A message writes a new inbox file and a message "
        "event. Decisions are not edited from here.</p>"
        "</div></div>")]
    for channel in channels:
        items = buckets.get(channel["pane"], [])
        items = sorted(items, key=lambda item: (item["ts"] or "", item["n"]))
        body = "".join(_item_html(item, esc, linkify) for item in items)
        if not body:
            body = "<div class='empty'>nothing on this thread yet</div>"
        composer = _composer(channel, agent_ids, projects, esc)
        head = "<div class='crumb'><a href='#threads'>All threads</a>"
        if channel["project"]:
            head += " · <a href='#proj/%s'>Project page</a>" % esc(channel["project"])
        head += "</div><h2>%s</h2><p class='sub'>%s</p>" % (
            esc(channel["heading"]), esc(channel["blurb"]))
        stage = ("<div class='thread'><div class='timeline'>%s%s</div>%s</div>"
                 % (head, body, composer))
        chunks.append(_pane_shell(channel["pane"], channels, channel["pane"], esc, stage))
    return "\n".join(chunks)


def _catalog(cards, projects):
    """Projects on disk, plus any project id a card names that has no file."""
    found = {}
    for project in projects:
        pid = (project.get("id") or "").strip()
        if pid:
            found[pid] = project
    for card in cards:
        pid = (card.get("project") or "").strip()
        if pid and pid not in found:
            found[pid] = {"id": pid, "title": pid, "status": ""}
    if any(not (card.get("project") or "").strip() for card in cards):
        found["unscoped"] = {"id": "unscoped", "title": "Unscoped", "status": ""}
    return found


def _cards_for(pid, cards):
    if pid == "unscoped":
        return [card for card in cards if not (card.get("project") or "").strip()]
    return [card for card in cards if (card.get("project") or "").strip() == pid]


def _open_count(pid, cards):
    return sum(1 for card in _cards_for(pid, cards) if (card.get("column") or "") != "done")


def _default_project(catalog, cards):
    """The project with the most open cards. Ties break on id, so the choice is stable."""
    if not catalog:
        return ""
    return max(sorted(catalog), key=lambda pid: _open_count(pid, cards))


def _lane_names(cards):
    extras = []
    for card in cards:
        column = (card.get("column") or "backlog").strip() or "backlog"
        if column not in LANES and column not in extras:
            extras.append(column)
    extras.sort(key=lambda name: (name != "review", name))
    return ("backlog", "in-progress") + tuple(extras) + ("blocked", "done")


def _lanes(cards, agent_ids, esc, today, project):
    chunks = []
    for column in _lane_names(cards):
        items = [card for card in cards if ((card.get("column") or "backlog").strip() or "backlog") == column]
        items = _sort_cards(items, by_column=False)
        tiles = "".join(_tile(card, agent_ids, esc, today, project) for card in items)
        if not tiles:
            tiles = "<div class='empty'>drop a card here</div>"
        if column == "done":
            label = ("<button type='button' class='collapse-done' aria-expanded='true'>done</button>")
        else:
            label = "<span class='lane-name'>%s</span>" % esc(column)
        chunks.append(
            "<section class='lane lane-%s' data-column='%s'>"
            "<header class='lane-head'>%s<span class='kcount'>%d</span></header>"
            "<div class='lane-cards'>%s</div></section>"
            % (esc(column), esc(column), label, len(items), tiles)
        )
    return "".join(chunks)


def _tile(card, agent_ids, esc, today, project):
    cid = card.get("id") or ""
    column = (card.get("column") or "backlog").strip() or "backlog"
    owner = card.get("assignee") or "unassigned"
    bits = ["<span class='pill status-%s'>%s</span>" % (esc(column), esc(column))]
    if owner == "unassigned":
        bits.append("<span class='pill owner dim'>unassigned</span>")
    else:
        bits.append("<span class='pill owner'>%s</span>" % esc(owner))
    priority = (card.get("priority") or "").strip().lower()
    if priority:
        bits.append("<span class='pill p-%s'>%s</span>" % (esc(priority), esc(priority)))
    due = (card.get("due") or "").strip()
    if due:
        overdue = ""
        if column != "done" and _iso_date(due) and due < today.isoformat():
            overdue = " overdue"
        bits.append("<span class='pill due%s'>%s</span>" % (overdue, esc(due)))
    ident = cid or "(no id)"
    link = "<a class='fp' href='raw/org/cards/%s.md'>%s</a>" % (esc(cid), esc(ident)) if cid else esc(ident)
    return (
        "<article class='tile clickable col-%s' draggable='true' data-kind='card' "
        "data-id='%s' data-column='%s'>"
        "<div class='tile-id'>%s</div>"
        "<div class='tile-title'>%s</div>"
        "<div class='tile-meta'>%s</div>"
        "<div class='edit-panel' hidden>%s</div>"
        "</article>"
        % (esc(column), esc(cid), esc(column), link,
           esc(card.get("title") or "(no title)"),
           "".join(bits),
           _edit_panel(card, agent_ids, esc, project))
    )


def _edit_panel(card, agent_ids, esc, project):
    """Owner, priority, and due. Status changes by dragging the card."""
    cid = card.get("id") or ""
    if not cid:
        return ""
    people = ["unassigned"] + [agent for agent in agent_ids if agent != "unassigned"]
    assignee = card.get("assignee") or "unassigned"
    if assignee not in people:
        people.append(assignee)
    owners = "".join(
        "<option value='%s'%s>%s</option>" % (esc(name), " selected" if name == assignee else "", esc(name))
        for name in people)
    current_p = (card.get("priority") or "").lower()
    prios = [("", "\u2014"), ("urgent", "urgent"), ("high", "high"), ("med", "med"), ("low", "low")]
    if current_p and current_p not in ("urgent", "high", "med", "low"):
        prios.append((current_p, current_p))
    priority = "".join(
        "<option value='%s'%s>%s</option>" % (
            esc(value), " selected" if value == current_p else "", esc(label))
        for value, label in prios)
    due = card.get("due") or ""
    back = "board/%s" % project if project else "board"
    return (
        "<form method='post' action='/api/card' class='card-form'>"
        "<input type='hidden' name='id' value='%s'>"
        "<input type='hidden' name='actor' value='brad'>"
        "<input type='hidden' name='back' value='%s'>"
        "<label>Owner <select name='assignee'>%s</select></label>"
        "<label>Priority <select name='priority'>%s</select></label>"
        "<label>Due <input name='due' type='text' placeholder='YYYY-MM-DD' value='%s' autocomplete='off'></label>"
        "<button type='submit'>Save</button>"
        "</form>"
        % (esc(cid), esc(back), owners, priority, esc(due))
    )


def _iso_date(value):
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _sort_cards(cards, by_column):
    def key(card):
        column = COLUMN_RANK(card.get("column"))
        priority = PRIO_RANK.get((card.get("priority") or "").lower(), 9)
        due = card.get("due") or "9999-99-99"
        head = (column,) if by_column else ()
        return head + (priority, due, card.get("id") or "")
    return sorted(cards, key=key)


def COLUMN_RANK(column):
    try:
        return COLUMNS.index(column)
    except ValueError:
        return 50


def _assemble(cards, projects, agents, events, messages, pointer, names,
              project_of, ref_cell):
    by_card = {c.get("id"): c for c in cards if c.get("id")}
    agent_ids = [a.get("id") for a in agents if a.get("id")]
    agent_set = set(agent_ids)
    unread = {}
    for message in messages:
        if message.get("done"):
            continue
        owner = message.get("to") or message.get("owner")
        if owner:
            unread[owner] = unread.get(owner, 0) + 1
    channels = []
    for project in sorted(projects, key=lambda p: (
            (p.get("status") or "") != "active", p.get("id") or "")):
        pid = project.get("id")
        if not pid:
            continue
        pcards = [c for c in cards if c.get("project") == pid]
        open_n = sum(1 for c in pcards if c.get("column") != "done")
        channels.append({
            "pane": "thread/project/%s" % pid,
            "group": "Projects",
            "label": "# %s" % pid,
            "hint": "%d open" % open_n,
            "heading": "# %s" % (project.get("title") or pid),
            "blurb": "%s · owner %s · %d open / %d done"
                     % (project.get("status") or "?", project.get("owner") or "?",
                        open_n, len(pcards) - open_n),
            "project": pid,
            "agent": "",
        })
    for agent in agents:
        aid = agent.get("id")
        if not aid:
            continue
        channels.append({
            "pane": "thread/agent/%s" % aid,
            "group": "Agents",
            "label": "@ %s" % (names.get(aid) or aid),
            "hint": "%d unread" % unread[aid] if unread.get(aid) else "",
            "heading": "@ %s" % (names.get(aid) or aid),
            "blurb": "events from %s, plus inbox files to or from %s" % (aid, aid),
            "project": "",
            "agent": aid,
        })
    channels.append({
        "pane": "thread/general",
        "group": "Org",
        "label": "# general",
        "hint": "",
        "heading": "# general",
        "blurb": "events and messages that are not scoped to a project",
        "project": "",
        "agent": "",
    })
    buckets = {channel["pane"]: [] for channel in channels}
    number = 0

    def add(pane, item):
        bucket = buckets.get(pane)
        if bucket is None or item in bucket:
            return
        bucket.append(item)

    for event in events:
        number += 1
        project = project_of(event) or ""
        item = {
            "n": number,
            "ts": str(event.get("ts") or ""),
            "who": names.get(event.get("agent"), event.get("agent") or "?"),
            "kind": str(event.get("type") or "event"),
            "subject": "",
            "text": str(event.get("note") or event.get("message") or "").strip(),
            "ref_html": pointer(event),
            "done": False,
            "activate": False,
        }
        if project:
            add("thread/project/%s" % project, item)
        else:
            add("thread/general", item)
        agent = event.get("agent")
        if agent in agent_set:
            add("thread/agent/%s" % agent, item)

    for message in messages:
        number += 1
        project = (message.get("project") or "").strip()
        card = by_card.get((message.get("card") or "").strip())
        if not project and card:
            project = card.get("project") or ""
        sender = message.get("from") or "?"
        recipient = message.get("to") or message.get("owner") or "?"
        item = {
            "n": number,
            "ts": message.get("ts") or "",
            "who": "%s \u2192 %s" % (names.get(sender, sender), names.get(recipient, recipient)),
            "kind": "message",
            "subject": message.get("subject") or "",
            "text": message.get("body") or "",
            "ref_html": ref_cell(message["rel"]) if message.get("rel") else "",
            "done": bool(message.get("done")),
            "activate": bool(message.get("activate")),
            "_rel": message.get("rel") or "",
        }
        if project:
            add("thread/project/%s" % project, item)
        else:
            add("thread/general", item)
        for who in (sender, recipient, message.get("owner")):
            if who in agent_set:
                add("thread/agent/%s" % who, item)
    return channels, buckets


def _item_html(item, esc, linkify):
    chips = []
    if item.get("done"):
        chips.append("<span class='chip'>filed</span>")
    if item.get("activate"):
        chips.append("<span class='chip ping'>ping</span>")
    subject = item.get("subject") or ""
    subject_html = "<div class='msg-subject'>%s</div>" % esc(subject) if subject else ""
    text = item.get("text") or ""
    if subject and text.strip() == subject.strip():
        text = ""
    text_html = ""
    if text:
        text_html = "<div class='msg-text'>%s</div>" % linkify(esc(text))
    ref = item.get("ref_html") or ""
    if item.get("_rel") and not ref:
        ref = item["_rel"]
    ref_html = "<div class='fp-src'>%s</div>" % ref if ref else ""
    return (
        "<article class='msg'><header><b>%s</b> <span class='dim'>%s · %s</span>%s</header>"
        "%s%s%s</article>"
        % (esc(item.get("who") or "?"), esc(item.get("kind") or ""),
           esc(item.get("ts") or "undated"), "".join(chips),
           subject_html, text_html, ref_html)
    )


def _pane_shell(pane, channels, active, esc, stage):
    return (
        "<section class='pane' data-pane='%s'><div class='slack'>%s%s</div></section>"
        % (esc(pane), _sidebar(channels, active, esc), stage)
    )


def _sidebar(channels, active, esc):
    parts = ["<nav class='ch-list'>"]
    group = None
    for channel in channels:
        if channel["group"] != group:
            group = channel["group"]
            parts.append("<div class='ch-h'>%s</div>" % esc(group))
        cls = " class='active'" if channel["pane"] == active else ""
        hint = " <span class='dim'>%s</span>" % esc(channel["hint"]) if channel["hint"] else ""
        parts.append("<a href='#%s'%s>%s%s</a>" % (
            esc(channel["pane"]), cls, esc(channel["label"]), hint))
    parts.append("</nav>")
    return "".join(parts)


def _composer(channel, agent_ids, projects, esc):
    recipients = "".join(
        "<option value='%s'>%s</option>" % (esc(agent_id), esc(agent_id))
        for agent_id in agent_ids)
    project_field = ""
    if channel["project"]:
        project_field = "<input type='hidden' name='project' value='%s'>" % esc(channel["project"])
    else:
        options = ["<option value=''>no project</option>"]
        for project in projects:
            pid = project.get("id")
            if pid:
                options.append("<option value='%s'>%s</option>" % (esc(pid), esc(pid)))
        project_field = "<label>Project <select name='project'>%s</select></label>" % "".join(options)
    return (
        "<form method='post' action='/api/post' class='composer'>"
        "<input type='hidden' name='actor' value='brad'>"
        "<input type='hidden' name='back' value='%s'>"
        "%s"
        "<div class='row'>"
        "<label>Kind <select name='kind'>"
        "<option value='note'>Note on the record</option>"
        "<option value='message'>Message to an inbox</option>"
        "</select></label>"
        "<label>To <select name='to'><option value=''>\u2014</option>%s</select></label>"
        "<label>Card <input name='card' type='text' placeholder='card-021' autocomplete='off'></label>"
        "</div>"
        "<input name='subject' type='text' placeholder='Subject, required for a message' autocomplete='off'>"
        "<textarea name='body' required placeholder='Write a note, or a message the recipient will find in their inbox'></textarea>"
        "<button type='submit'>Post</button>"
        "<p class='sub'>A note is one new line in org/events. A message is a new file in org/inbox plus a message event.</p>"
        "</form>"
        % (esc(channel["pane"]), project_field, recipients)
    )
