---
id: decision-005
kind: decision
key: single-writer-dispatch
updated: 2026-10-29T02:35
supersedes: []
confidence: high
---

**Brad's ruling (2026-10-29):** only qwen checks in directly (VRAM goes to
qwen; no other local agent). Cloud agents are **dispatch-only** with a
fresh brief; Brad decides dispatches. Design principle: **least frictionless
operation** — no ceremony, no machinery before traffic. Generated snapshots
(board/outbound/brief/dashboard) are derived views: regenerate every
check-in, never treat as sources. Full: org/decisions/2026-10-29-single-writer-dispatch.md.
