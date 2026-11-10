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
.sr { position: absolute; opacity: 0; width: 1px; height: 1px; }
.switch { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 8px 0 14px; }
.switch label {
  border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px;
  cursor: pointer; color: var(--dim);
}
#view-status:checked ~ .switch label[for="view-status"],
#view-project:checked ~ .switch label[for="view-project"],
#view-agent:checked ~ .switch label[for="view-agent"],
#view-kanban:checked ~ .switch label[for="view-kanban"],
#show-done:checked ~ .switch label[for="show-done"] {
  color: var(--text); border-color: var(--accent);
}
.board-switch .view { display: none; }
#view-status:checked ~ .view-status { display: block; }
#view-project:checked ~ .view-project { display: block; }
#view-agent:checked ~ .view-agent { display: block; }
#view-kanban:checked ~ .view-kanban { display: block; }
.board-switch:not(:has(#show-done:checked)) .is-done,
.board-switch:not(:has(#show-done:checked)) .group-only-done { display: none; }
.group { margin: 0 0 18px; }
.group h3 {
  font-size: 13px; text-transform: uppercase; letter-spacing: 1px;
  color: var(--dim); margin: 0 0 8px;
}
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


def board_views(cards, projects, agents, ref_cell, esc, today):
    agent_ids = [a.get("id") for a in agents if a.get("id")]
    names = {a.get("id"): (a.get("name") or a.get("id")) for a in agents if a.get("id")}
    open_n = sum(1 for c in cards if c.get("column") != "done")
    done_n = len(cards) - open_n
    intro = ("%d open · %d done. Show done reveals the archive. "
             "Save writes that card's frontmatter and appends one event."
             % (open_n, done_n))
    by_status = _groups_by_status(cards)
    by_project = _groups_by_project(cards, projects)
    by_agent = _groups_by_agent(cards, agent_ids, names)
    views = [
        _switch(),
        "<div class='view view-status'>%s</div>" % _tables(
            by_status, agent_ids, ref_cell, esc, today, by_column=False),
        "<div class='view view-project'>%s</div>" % _tables(
            by_project, agent_ids, ref_cell, esc, today, by_column=True),
        "<div class='view view-agent'>%s</div>" % _tables(
            by_agent, agent_ids, ref_cell, esc, today, by_column=True),
        "<div class='view view-kanban'><div class='board'>%s</div></div>" % _kanban(
            cards, agent_ids, ref_cell, esc, today),
    ]
    return intro, "\n".join(views) + "</div>"


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


def _switch():
    return (
        "<div class='board-switch'>"
        "<input class='sr' type='radio' name='board-view' id='view-status' checked>"
        "<input class='sr' type='radio' name='board-view' id='view-project'>"
        "<input class='sr' type='radio' name='board-view' id='view-agent'>"
        "<input class='sr' type='radio' name='board-view' id='view-kanban'>"
        "<input class='sr' type='checkbox' id='show-done'>"
        "<div class='switch'>"
        "<label for='view-status'>By status</label>"
        "<label for='view-project'>By project</label>"
        "<label for='view-agent'>By agent</label>"
        "<label for='view-kanban'>Kanban</label>"
        "<label for='show-done'>Show done</label>"
        "</div>"
    )


def _groups_by_status(cards):
    columns = list(COLUMNS)
    for card in cards:
        column = card.get("column") or "backlog"
        if column not in columns:
            columns.append(column)
    groups = []
    for column in columns:
        items = [c for c in cards if (c.get("column") or "backlog") == column]
        groups.append((column, "", items))
    return groups


def _groups_by_project(cards, projects):
    order = sorted(projects, key=lambda p: (
        (p.get("status") or "") != "active", p.get("title") or p.get("id") or ""))
    groups = []
    seen = set()
    for project in order:
        pid = project.get("id")
        if not pid:
            continue
        seen.add(pid)
        items = [c for c in cards if c.get("project") == pid]
        if not items:
            continue
        label = "%s · %s" % (project.get("title") or pid, project.get("status") or "?")
        groups.append((label, pid, items))
    unknown = [c for c in cards if (c.get("project") or "") not in seen]
    if unknown:
        groups.append(("Unscoped", "", unknown))
    return groups


def _groups_by_agent(cards, agent_ids, names):
    groups = []
    seen = set()
    for agent_id in agent_ids:
        items = [c for c in cards if (c.get("assignee") or "unassigned") == agent_id]
        if not items:
            continue
        seen.add(agent_id)
        groups.append((names.get(agent_id) or agent_id, agent_id, items))
    rest = {}
    for card in cards:
        assignee = card.get("assignee") or "unassigned"
        if assignee in seen:
            continue
        rest.setdefault(assignee, []).append(card)
    for assignee in sorted(rest, key=lambda name: (name == "unassigned", name)):
        groups.append((assignee, "", rest[assignee]))
    return groups


def _tables(groups, agent_ids, ref_cell, esc, today, by_column):
    blocks = []
    for title, _key, items in groups:
        if not items:
            continue
        blocks.append(_table_group(title, items, agent_ids, ref_cell, esc, today, by_column))
    return "\n".join(blocks) or "<div class='empty'>no cards</div>"


def _table_group(title, items, agent_ids, ref_cell, esc, today, by_column):
    items = _sort_cards(items, by_column)
    done_n = sum(1 for c in items if c.get("column") == "done")
    only_done = bool(items) and done_n == len(items)
    cls = "group group-only-done" if only_done else "group"
    rows = []
    for card in items:
        rows.append(_row(card, agent_ids, ref_cell, esc, today))
    meta = "%d open / %d done" % (len(items) - done_n, done_n)
    return (
        "<section class='%s'><h3>%s <span class='kcount'>%s</span></h3>"
        "<table><tr><th>Card</th><th>Project</th><th>Owner</th><th>Priority</th>"
        "<th>Due</th><th>Updated</th><th>Status</th></tr>%s</table></section>"
        % (cls, esc(title), esc(meta), "".join(rows) or
           "<tr><td colspan='7'><span class='empty'>nothing here</span></td></tr>")
    )


def _row(card, agent_ids, ref_cell, esc, today):
    done = " is-done" if card.get("column") == "done" else ""
    cid = card.get("id") or ""
    return (
        "<tr class='clickable%s' data-kind='card' data-id='%s'>"
        "<td><div class='card-title'>%s</div><div class='cid'>%s</div></td>"
        "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
        % (done, esc(cid), esc(card.get("title") or "(no title)"),
           ref_cell(cid) if cid else "",
           _project_cell(card, esc),
           _owner_cell(card, agent_ids, esc),
           _prio_html(card.get("priority"), esc),
           _due_html(card, esc, today),
           esc(card.get("updated_at") or ""),
           _card_form(card, agent_ids, esc))
    )


def _kanban(cards, agent_ids, ref_cell, esc, today):
    columns = list(COLUMNS)
    for card in cards:
        column = card.get("column") or "backlog"
        if column not in columns:
            columns.append(column)
    chunks = []
    for column in columns:
        items = [c for c in cards if (c.get("column") or "backlog") == column]
        items = _sort_cards(items, by_column=False)
        only_done = column == "done" or (bool(items) and all(
            c.get("column") == "done" for c in items))
        cls = "kcol group-only-done" if only_done else "kcol"
        cards_html = []
        for card in items:
            cid = card.get("id") or ""
            done = " is-done" if card.get("column") == "done" else ""
            cards_html.append(
                "<div class='card clickable col-%s%s' data-kind='card' data-id='%s'>"
                "<div class='card-head'><span class='assignee'>%s</span></div>"
                "<div class='cid'>%s</div>"
                "<div class='card-title'>%s</div>"
                "<div class='card-meta'>%s · %s · due %s · updated %s</div>"
                "%s%s</div>"
                % (esc(column), done, esc(cid),
                   esc(card.get("assignee") or "unassigned"),
                   ref_cell(cid) if cid else "",
                   esc(card.get("title") or "(no title)"),
                   _project_cell(card, esc),
                   _prio_html(card.get("priority"), esc),
                   _due_html(card, esc, today),
                   esc(card.get("updated_at") or "?"),
                   _deps(card, ref_cell),
                   _card_form(card, agent_ids, esc))
            )
        chunks.append(
            "<div class='%s'><div class='kcol-head'>%s <span class='kcount'>%d</span></div>"
            "<div class='kcards'>%s</div></div>"
            % (cls, esc(column), len(items),
               "\n".join(cards_html) or "<div class='empty'>\u2014</div>")
        )
    return "\n".join(chunks)


def _card_form(card, agent_ids, esc):
    cid = card.get("id") or ""
    if not cid:
        return ""
    column = card.get("column") or "backlog"
    columns = list(COLUMNS)
    if column not in columns:
        columns = [column] + columns
    status = "".join(
        "<option value='%s'%s>%s</option>" % (esc(name), " selected" if name == column else "", esc(name))
        for name in columns)
    people = ["unassigned"] + [a for a in agent_ids if a != "unassigned"]
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
    return (
        "<form method='post' action='/api/card' class='card-form'>"
        "<input type='hidden' name='id' value='%s'>"
        "<input type='hidden' name='actor' value='brad'>"
        "<input type='hidden' name='back' value='board'>"
        "<label>Status <select name='column'>%s</select></label>"
        "<button type='submit'>Save</button>"
        "<details><summary>Owner, priority, due</summary><div class='fields'>"
        "<label>Owner <select name='assignee'>%s</select></label>"
        "<label>Priority <select name='priority'>%s</select></label>"
        "<label>Due <input name='due' type='text' placeholder='YYYY-MM-DD' value='%s' autocomplete='off'></label>"
        "<label>Note <input name='note' type='text' placeholder='required if you block it' autocomplete='off'></label>"
        "</div></details></form>"
        % (esc(cid), status, owners, priority, esc(due))
    )


def _project_cell(card, esc):
    pid = card.get("project") or ""
    if not pid:
        return "<span class='dim'>unscoped</span>"
    return "<a href='#proj/%s'>%s</a>" % (esc(pid), esc(pid))


def _owner_cell(card, agent_ids, esc):
    assignee = card.get("assignee") or "unassigned"
    if assignee == "unassigned":
        return "<span class='dim'>unassigned</span>"
    if assignee in agent_ids:
        return "<a href='#thread/agent/%s'>%s</a>" % (esc(assignee), esc(assignee))
    return esc(assignee)


def _prio_html(priority, esc):
    priority = (priority or "").strip().lower()
    if not priority:
        return "<span class='dim'>\u2014</span>"
    return "<span class='prio p-%s'>%s</span>" % (esc(priority), esc(priority))


def _due_html(card, esc, today):
    due = (card.get("due") or "").strip()
    if not due:
        return "<span class='dim'>\u2014</span>"
    overdue = ""
    if card.get("column") != "done" and _iso_date(due) and due < today.isoformat():
        overdue = " overdue"
    return "<span class='%s'>%s</span>" % (overdue.strip(), esc(due))


def _iso_date(value):
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _deps(card, ref_cell):
    raw = card.get("depends_on") or ""
    deps = []
    for piece in raw.replace("[", "").replace("]", "").split(","):
        piece = piece.strip().strip('"').strip("'")
        if piece:
            deps.append(piece)
    if not deps:
        return ""
    return "<div class='deps'>deps: %s</div>" % " &middot; ".join(ref_cell(d) for d in deps)


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
