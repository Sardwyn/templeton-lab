"""Qwen remember — the Lattice write head.

Usage:
    python worker/remember.py <kind> <key> <text>
    python worker/remember.py <kind> <key> <text> --supersede <old-id>

Kinds: preference | person | project | decision | timeline | lesson | fact
Creates (or updates) memory/cells/<kind>-<key>.md with a fresh timestamp,
and appends a memory_write event to today's log.
"""
import datetime
import sys
from pathlib import Path

LAB = Path(r"F:\Lab")
MEMORY = LAB / "memory" / "cells"
EVENTS = LAB / "org" / "events"

KINDS = ("preference", "person", "project", "decision", "timeline",
         "lesson", "fact")


def slugify(s):
    out = []
    for ch in s.lower():
        out.append(ch if ch.isalnum() else "-")
    return "".join(out).strip("-")


def main():
    args = sys.argv[1:]
    supersede = []
    if "--supersede" in args:
        i = args.index("--supersede")
        supersede = args[i + 1]
        args = args[:i]
    if len(args) != 3:
        print(__doc__)
        sys.exit(2)
    kind, key, text = args
    kind = kind.lower().strip()
    if kind not in KINDS:
        print("kind must be one of: %s" % ", ".join(KINDS))
        sys.exit(2)
    key = slugify(key)
    if not key:
        print("empty key")
        sys.exit(2)

    now = datetime.datetime.now()
    path = MEMORY / ("%s-%s.md" % (kind, key))
    existing = None
    if path.exists():
        existing = path.read_text(encoding="utf-8")

    sup_line = ""
    if supersede:
        sup_line = supersede
    elif existing:
        # preserve previous supersedes on update — unwrap the frontmatter list
        # so a re-write doesn't nest brackets into `[[]]`
        for line in existing.splitlines():
            if line.strip().startswith("supersedes:"):
                raw = line.split(":", 1)[1].strip()
                parts = [p.strip().strip("\"'")
                         for p in raw.strip("[] ").split(",")
                         if p.strip().strip("[]").strip("\"'")]
                sup_line = ", ".join(parts)
                break

    body = text.strip()
    content = (
        "---\n"
        "id: %s-%s\n"
        "kind: %s\n"
        "key: %s\n"
        "updated: %s\n"
        "supersedes: [%s]\n"
        "confidence: %s\n"
        "---\n\n%s\n"
        % (kind, key, kind, key, now.strftime("%Y-%m-%dT%H:%M"),
           sup_line, "high" if not existing else "high", body)
    )
    MEMORY.mkdir(parents=True, exist_ok=True)
    action = "update" if existing else "write"
    path.write_text(content, encoding="utf-8")

    import json
    EVENTS.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": now.strftime("%Y-%m-%dT%H:%M"),
        "agent": "qwen",
        "type": "memory_write",
        "cell": "%s-%s" % (kind, key),
        "action": action,
    }
    if supersede:
        entry["supersedes"] = supersede
    with open(EVENTS / (now.strftime("%Y-%m-%d") + ".jsonl"), "a",
              encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    print("%s memory cell: %s (%s)" % (action, path.name,
                                      "supersedes " + supersede if supersede else action))


if __name__ == "__main__":
    main()
