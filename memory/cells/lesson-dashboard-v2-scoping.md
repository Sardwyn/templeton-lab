---
id: lesson-dashboard-v2-scoping
kind: lesson
key: dashboard-v2-scoping
updated: 2026-10-29T23:55
supersedes: []
confidence: high
---

**dashboard.py v2 mechanics (learned 2026-10-29, card-015).** HTML_TEMPLATE is a `%`-format string with a dict, so every literal percent inside CSS/JS must be written `%%` — one bare `%` raises ValueError at build time. Project scoping is a resolver, not a filter: `project_scopes()` maps an event's ctx refs (`card`/`card_id`, `build_id`/`build`, `cell`, `repo`, `file`) onto the project carried by that artifact; `memory_write` cells are stemmed without `.md`, and old lines that comma-join several cells or name no artifact stay unscoped (27 of 72 — org-level decisions, notes, messages, identity fixes). `build_streak()` needs builds sorted newest-first and always returns `(kind, count)`; `serve.py` reloads dashboard.py and re-runs `build_page()` per request, so generator edits appear without a restart.
