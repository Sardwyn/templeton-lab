---
id: lesson-console-cp1252
kind: lesson
key: console-encoding
updated: 2026-10-15T04:10
supersedes: []
confidence: high
---

Windows console here is **cp1252** — Unicode output (e.g. mu, em-dash, arrows)
raises UnicodeEncodeError when piped. Fix: set PYTHONIOENCODING=utf-8 in the
process env (done in run_build.py targets) and write files explicitly
utf-8. The org's em-dash "—" renders fine in files/dashboards; only console
prints bite.
