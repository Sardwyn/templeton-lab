---
id: lesson-stale-server-overwrites
kind: lesson
key: stale-server
updated: 2026-10-15T04:10
supersedes: []
confidence: high
---

A **long-running serve.py can silently overwrite** dashboard output: it
imports dashboard at startup, so a stale server re-renders the OLD format on
every page load. Fixed in v2: serve.py now importlib.reload()s the dashboard
module per request. General rule: after changing a generator the server
imports, restart the server (or rely on the reload) — a stale process is a
silent regression.
