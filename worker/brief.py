r"""Temporal-grounding brief for cloud agent handoffs.

Cloud sessions are stateless — never hand one raw context. Run:

    python worker\brief.py [agent_id]        (default: copilot)

Writes F:\Lab\state\BRIEF.md and prints it. Paste the brief into the
cloud session, then the task. The brief carries the date anchor, board,
open pings, recent events, and roster so the agent knows what is current.
"""
import datetime
import json
import re
import sys
from pathlib import Path

LAB = Path(r"F:\Lab")
ORG = LAB / "org"
STATE = LAB / "state"
COLUMNS = ["backlog", "in-progress", "review", "done", "blocked"]


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


def load_dir_md(folder):
    out = []
    if folder.exists():
        for p in sorted(folder.glob("*.md")):
            f = parse_frontmatter(p)
            if f:
                out.append(f)
    return out


def load_events(limit=15):
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


def load_pings():
    pings = []
    inbox = ORG / "inbox"
    if inbox.exists():
        for d in sorted(inbox.iterdir()):
            if not d.is_dir():
                continue
            for f in sorted(d.iterdir()):
                if not f.is_file() or f.name == ".keep":
                    continue
                fm = parse_frontmatter(f)
                if not fm:
                    continue
                if str(fm.get("activate", "")).lower() == "true":
                    fm["to"] = d.name
                    pings.append(fm)
    return pings


def main():
    agent = sys.argv[1] if len(sys.argv) > 1 else "copilot"
    now = datetime.datetime.now()

    cards = load_dir_md(ORG / "cards")
    board = {}
    for col in COLUMNS:
        items = [c for c in cards if c.get("column", "backlog") == col]
        board[col] = items

    events = load_events()
    pings = load_pings()
    agents = {}
    for a in load_dir_md(ORG / "agents"):
        agents[a.get("id", "?")] = a

    lines = []
    lines.append("# ORG BRIEF — %s (local time, Europe/London)" % now.strftime("%Y-%m-%d %H:%M"))
    lines.append("For: **%s** — Templeton Systems org, HQ at F:\\Lab" % agent)
    lines.append("")
    lines.append("This brief is your temporal anchor: the date above is NOW,")
    lines.append("the board below is current state. Everything older than")
    lines.append("these events is history.")
    lines.append("")
    lines.append("## Board (now)")
    for col in COLUMNS:
        items = board[col]
        if not items:
            lines.append("- %s: (empty)" % col)
            continue
        lines.append("- %s:" % col)
        for c in items:
            lines.append("  - %s — %s [%s]" % (c.get("id", "?"), c.get("title", ""), c.get("assignee", "unassigned")))
    lines.append("")
    names = {aid: (a.get("name") or aid) for aid, a in agents.items()}

    def disp(aid):
        return names.get(aid, aid)

    lines.append("## Open pings")
    if not pings:
        lines.append("- (none)")
    for p in pings:
        lines.append("- %s -> %s: %s (needs: %s%s)" % (
            disp(p.get("from", "?")), disp(p.get("to", "?")), p.get("subject", ""),
            p.get("needs", "-"), ", card: " + p["card"] if p.get("card") else ""))
    lines.append("")
    lines.append("## Recent events (newest first)")
    for e in events:
        lines.append("- %s | %s | %s%s" % (e.get("ts", "?"), e.get("agent", "?"), e.get("type", "?"),
                                          " | " + str(e.get("card_id", "")) if e.get("card_id") else ""))
    lines.append("")
    lines.append("## Roster")
    for aid in sorted(agents):
        a = agents[aid]
        lines.append("- %s — %s, %s | schedule: %s | focus: %s" % (
            aid, a.get("role", "?"), a.get("side", a.get("status", "?")),
            a.get("schedule", "-"), a.get("focus", "-")))
    lines.append("")
    lines.append("## Reply format (org-update block)")
    lines.append("End your session with this block so qwen can land it:")
    lines.append("")
    lines.append("```")
    lines.append("agent: %s" % agent)
    lines.append("status: <on-duty|off-duty|cloud>")
    lines.append("focus: <what you are working on>")
    lines.append("cards:")
    lines.append("  - <id>: <column> [claim|move|done]")
    lines.append("messages:")
    lines.append("  - to: <who> | subject: <...> | body: <...>")
    lines.append("events:")
    lines.append("  - <type> | <card_id or note>")
    lines.append("```")
    lines.append("")
    lines.append("If you need anything that costs time/money (activating a")
    lines.append("paid agent, a decision, a deletion), ping the CEO instead")
    lines.append("of assuming. Agents don't spend, agents ask.")

    brief = "\n".join(lines)
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "BRIEF.md").write_text(brief, encoding="utf-8")
    print(brief)


if __name__ == "__main__":
    main()
