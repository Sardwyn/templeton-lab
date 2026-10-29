---
id: card-012
title: Single-writer reality — dispatch-only roster + check-in freshness
column: done
assignee: qwen
project: templeton-lab
depends_on: ["card-003", "card-007"]
created_at: 2026-10-29T02:30
updated_at: 2026-10-29T02:35
---

Per decision-005: make the org's state and SOP reflect reality — qwen is
the sole direct-check-in writer (VRAM constraint); cloud agents are
dispatch-only, never heartbeat-bearing.

1. SOP v1.4: dispatch-only note + freshness step (sync + dashboard + brief
   at every check-in, board derived from cards).
2. Cloud agent entries: `dispatch_only: true`; dashboard/roster honest.
3. Run the freshness cycle; stale BOARD/outbound/brief snapshots corrected.
4. Decision recorded in memory (cell + audit).
