---
id: card-008
title: Dashboard v2 — pages (tabs) + detail drawers
column: backlog
assignee: unassigned
depends_on: ["card-002"]
created_at: 2026-10-14T08:35
updated_at: 2026-10-14T08:35
---

The single page is outgrowing itself (CEO note 2026-10-14). Split the
dashboard into pages/tabs — Board, Pings, Roster, Builds, Events — with
click-through detail drawers (card, message, build, agent entry) that open
the full artifact instead of a summary. Keep the static-file fallback
working; the /raw/ browse route stays as the escape hatch.
