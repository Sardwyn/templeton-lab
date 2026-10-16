"""Memory audit — Lattice integrity + coverage checks.

Usage: python worker/memory_audit.py

Checks:
  1. Cells: all parse, ids unique, kinds valid, supersedes resolvable.
  2. Coverage: every org/decisions/*.md is reflected in memory/
     (core.md or any cell). Reports gaps.
  3. Freshness: last memory_write event; oldest cells (informational).

Exit 0 = clean (coverage gaps are warnings), 1 = hard errors.
"""
import datetime
import json
import re
import sys
from pathlib import Path

LAB = Path(r"F:\Lab")
MEMORY = LAB / "memory"
EVENTS = LAB / "org" / "events"
DECISIONS = LAB / "org" / "decisions"
KINDS = ("preference", "person", "project", "decision",
         "timeline", "lesson", "fact")


def load_cell(path):
    text = path.read_text(encoding="utf-8")
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


def main():
    errors, warns = [], []
    cells = []
    cdir = MEMORY / "cells"
    if cdir.exists():
        for p in sorted(cdir.glob("*.md")):
            c = load_cell(p)
            if c is None:
                errors.append("unparseable cell: %s" % p.name)
                continue
            c["_file"] = p.name
            cells.append(c)

    # 1. integrity
    seen = {}
    refs = set()
    for c in cells:
        cid = c.get("id", "")
        if cid in seen:
            errors.append("duplicate id: %s (%s, %s)"
                          % (cid, seen[cid], c["_file"]))
        else:
            seen[cid] = c["_file"]
        if c.get("kind") not in KINDS:
            warns.append("bad kind %r in %s" % (c.get("kind"), c["_file"]))
        raw = c.get("supersedes", "")
        for s in raw.replace("]", "").replace("[", "").split(","):
            s = s.strip().strip('"').strip()
            if s:
                refs.add(s)
    retired = refs - set(seen)
    for r in sorted(retired):
        warns.append("supersedes ref has no file (retired in place?): %s" % r)

    # 2. coverage: every decision must live in memory
    core_text = ""
    core = MEMORY / "core.md"
    if core.exists():
        core_text = core.read_text(encoding="utf-8")
    cell_texts = "\n".join(
        c.get("_body", "") + " " + " ".join(c.values()) for c in cells)
    gaps = []
    n_dec = 0
    if DECISIONS.exists():
        for p in sorted(DECISIONS.glob("*.md")):
            n_dec += 1
            d = load_cell(p) or {}
            did = d.get("id", p.stem)
            heading = ""
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    heading = line[2:].strip()
                    break
            probe_ids = [did]
            probe_words = " ".join(heading.lower().split()[:5])
            in_mem = (did in core_text or did in cell_texts
                      or (probe_words and probe_words in cell_texts))
            if not in_mem:
                gaps.append(did)

    # 3. freshness
    last_write, n_writes = None, 0
    if EVENTS.exists():
        for p in sorted(EVENTS.glob("*.jsonl")):
            for line in p.read_text(encoding="utf-8").splitlines():
                if "memory_write" in line:
                    n_writes += 1
                    try:
                        ts = json.loads(line).get("ts", "")
                        if ts and (last_write is None or ts > last_write):
                            last_write = ts
                    except json.JSONDecodeError:
                        pass
    oldest = None
    for c in cells:
        u = c.get("updated", "")
        if u and (oldest is None or u < oldest[1]):
            oldest = (c.get("id", "?"), u)

    # report
    print("MEMORY AUDIT — %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("cells: %d (retired refs: %d) | kinds: %s" % (
        len(cells), len(refs),
        ", ".join("%d %s" % (sum(1 for c in cells if c.get("kind") == k), k)
                 for k in KINDS if any(c.get("kind") == k for c in cells))))
    print("memory_write events: %d | last: %s" % (n_writes, last_write or "never"))
    print("oldest cell: %s (%s)" % (oldest or ("none", "")))
    for w in warns:
        print("WARN  %s" % w)
    if gaps:
        print("GAPS  decisions not in memory: %s" % ", ".join(gaps))
    else:
        print("coverage: all %d decision(s) reflected in memory" % n_dec)
    for e in errors:
        print("ERROR %s" % e)
    print("result: %s" % ("FAIL" if errors else "PASS"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
