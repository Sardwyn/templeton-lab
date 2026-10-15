"""Qwen recall — session-start hydration: memory + org state in one pass.

Usage:
    python worker/recall.py [topic]

Loads and prints (also writes state/RECALL.md under the F:/Lab HQ):
  1. Core memory  — memory/core.md (the hot tier, always loaded)
  2. Memory cells — always-relevant kinds (preference, person) + the 5 most
                    recent other cells + any cell matching [topic]
  3. Org state    — date anchor, board, open pings, recent events, roster
                    (reuses worker/brief.py loaders)

This is the Lattice read head: bounded, keyed, current. Superseded cells are
excluded (the overwrite semantics).
"""
import datetime
import sys
from pathlib import Path

LAB = Path(r"F:\Lab")
MEMORY = LAB / "memory"
STATE = LAB / "state"
sys.path.insert(0, str(LAB / "worker"))

from brief import COLUMNS, load_dir_md, load_events, load_pings  # noqa: E402


def load_cell(path):
    text = path.read_text(encoding="utf-8")
    import re
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip().strip('"')
    fields["_body"] = text[m.end():].strip()
    return fields


def load_cells():
    cells = []
    cdir = MEMORY / "cells"
    if cdir.exists():
        for p in sorted(cdir.glob("*.md")):
            c = load_cell(p)
            if c:
                cells.append(c)
    return cells


def cell_summary(c):
    body = c.get("_body", "").splitlines()
    first = body[0].strip() if body else ""
    return "%s [%s] %s — %s" % (c.get("id", "?"), c.get("kind", "?"),
                               c.get("updated", "?"), first[:80])


def main():
    topic = sys.argv[1].lower() if len(sys.argv) > 1 else None
    now = datetime.datetime.now()

    # ---- supersession: any cell listed in another's supersedes is retired
    retired = set()
    for c in load_cells():
        raw = c.get("supersedes", "")
        for s in raw.replace("]", "").replace("[", "").split(","):
            s = s.strip().strip('"').strip()
            if s:
                retired.add(s)

    # ---- memory
    lines = []
    lines.append("# QWEN RECALL — %s" % now.strftime("%Y-%m-%d %H:%M"))
    lines.append("")

    core = MEMORY / "core.md"
    lines.append("## 1. CORE MEMORY (hot tier)")
    if core.exists():
        lines.append(core.read_text(encoding="utf-8").strip())
    else:
        lines.append("(no core memory yet)")
    lines.append("")

    cells = [c for c in load_cells() if c.get("id") not in retired]
    always = [c for c in cells if c.get("kind") in ("preference", "person")]
    rest = [c for c in cells
            if c.get("kind") not in ("preference", "person")]
    rest.sort(key=lambda c: c.get("updated", ""), reverse=True)
    recent = rest[:5]
    topical = []
    if topic:
        topical = [c for c in cells
                   if topic in (c.get("id", "") + c.get("key", "")
                                + c.get("_body", "")).lower()]

    lines.append("## 2. MEMORY CELLS (warm tier)")
    shown = []
    for group, label in ((always, "standing"), (recent, "recent"),
                         (topical, "topic: %s" % topic)):
        if not group:
            continue
        lines.append("")
        lines.append("### %s" % label)
        for c in group:
            if c in shown:
                continue
            shown.append(c)
            lines.append("### %s  [%s]  (updated %s)"
                         % (c.get("id", "?"), c.get("kind", "?"),
                            c.get("updated", "?")))
            lines.append(c.get("_body", "").strip())
            lines.append("")
    if not shown:
        lines.append("(no memory cells yet)")
    if retired:
        lines.append("")
        lines.append("(retired/superseded: %s)" % ", ".join(sorted(retired)))
    lines.append("")

    # ---- org state
    cards = load_dir_md(LAB / "org" / "cards")
    events = load_events(10)
    pings = load_pings()
    agents = {}
    for a in load_dir_md(LAB / "org" / "agents"):
        agents[a.get("id", "?")] = a

    lines.append("## 3. ORG STATE (now)")
    lines.append("Date anchor: %s (local time) — this is NOW." % now.strftime("%Y-%m-%d %H:%M"))
    lines.append("")
    lines.append("### Board")
    for col in COLUMNS:
        items = [c for c in cards if c.get("column", "backlog") == col]
        if not items:
            lines.append("- %s: (empty)" % col)
        else:
            lines.append("- %s:" % col)
            for c in items:
                lines.append("  - %s — %s [%s]"
                             % (c.get("id", "?"), c.get("title", ""),
                                c.get("assignee", "unassigned")))
    lines.append("")
    lines.append("### Open pings")
    if not pings:
        lines.append("- (none)")
    for p in pings:
        lines.append("- %s -> %s: %s (needs: %s)"
                     % (p.get("from", "?"), p.get("to", "?"),
                        p.get("subject", ""), p.get("needs", "-")))
    lines.append("")
    lines.append("### Recent events (newest first)")
    for e in events:
        lines.append("- %s | %s | %s%s" % (
            e.get("ts", "?"), e.get("agent", "?"), e.get("type", "?"),
            " | " + str(e.get("card_id", "")) if e.get("card_id") else ""))
    lines.append("")
    lines.append("### Roster")
    for aid in sorted(agents):
        a = agents[aid]
        lines.append("- %s — %s, %s | schedule: %s | focus: %s" % (
            aid, a.get("role", "?"), a.get("side", a.get("status", "?")),
            a.get("schedule", "-"), a.get("focus", "-")))

    recall = "\n".join(lines)
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "RECALL.md").write_text(recall, encoding="utf-8")
    print(recall)
    print("\n[recall written to state/RECALL.md — %d active cells, %d retired]"
          % (len(cells), len(retired)))


if __name__ == "__main__":
    main()
