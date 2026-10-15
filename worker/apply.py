"""Canonical org recorders (builds, events). Single source of truth:
anything that records a build goes through record_build_event()."""
import datetime
import json
import re
from pathlib import Path

LAB = Path(r"F:\Lab")
BUILDS = LAB / "org" / "builds"
EVENTS = LAB / "org" / "events"


def _today_file():
    d = datetime.date.today()
    return d.strftime("%Y-%m-%d") + ".jsonl"


def append_event(agent, type_, **ctx):
    """Append one line to today's event log."""
    EVENTS.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "agent": agent,
        "type": type_,
    }
    for k, v in ctx.items():
        if v not in (None, ""):
            entry[k] = v
    with open(EVENTS / _today_file(), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _next_build_id(date_str):
    """build-YYYYMMDD-NNN, NNN continues from that day's existing builds."""
    pattern = re.compile(r"^build-%s-(\d{3})\.md$" % date_str)
    highest = 0
    if BUILDS.exists():
        for p in BUILDS.iterdir():
            m = pattern.match(p.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return "build-%s-%03d" % (date_str, highest + 1)


def record_build_event(target=None, agent="qwen", status=None,
                       exit_code=None, log_text="", log_file=None,
                       notes=""):
    """Record one build. Returns the build file path, or None if called
    as a no-op echo (no target and no status given — e.g. the scaffold
    record_build step running without context)."""
    if not target and not status:
        print("record_build_event: no-op echo (no build context passed)")
        return None

    BUILDS.mkdir(parents=True, exist_ok=True)
    build_id = _next_build_id(datetime.date.today().strftime("%Y%m%d"))
    status = (status or ("pass" if exit_code == 0 else "fail")).lower()
    ts = datetime.datetime.now().isoformat(timespec="seconds")

    body = [
        "command: %s" % (target or "?"),
        "exit: %s" % (exit_code if exit_code is not None else "?"),
        "log: %s" % (log_file or "-"),
        "notes: %s" % (notes or "-"),
    ]
    if log_text:
        body.append("")
        body.append("log tail:")
        body.append("```")
        body.append(log_text.strip())
        body.append("```")

    path = BUILDS / ("%s.md" % build_id)
    with open(path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("id: %s\n" % build_id)
        f.write("target: %s\n" % (target or "?"))
        f.write("agent: %s\n" % agent)
        f.write("status: %s\n" % status)
        f.write("ts: %s\n" % ts)
        f.write("---\n\n")
        f.write("\n".join(body))
        f.write("\n")

    append_event(agent, "build_pass" if status == "pass" else "build_fail",
                 build_id=build_id, target=target)
    return str(path)
