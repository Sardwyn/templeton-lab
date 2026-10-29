---
id: card-013
title: Inbound reply parser — land a cloud org-update block (bus role)
column: backlog
assignee: unassigned
depends_on: ["card-012"]
created_at: 2026-10-29T02:30
updated_at: 2026-10-29T02:30
---

When the first real cloud dispatch (copilot) returns an org-update block,
qwen needs a mechanical landing path: parse the reply block, apply card
moves, drop messages in inboxes, append events (provenance: "landed by
qwen from <agent>"), regenerate views, commit.

Held in backlog deliberately (decision-005: no machinery before traffic).
Build only when a dispatch has actually returned.

Known landmine to fix with this card: `worker/sync.py::apply_inbound()`
reads `transport/inbound/updates.json` and then **deletes it without
applying anything** — a dropped cloud update would vanish silently.
