---
id: card-008
title: Dashboard v2 — pages (tabs) + detail drawers
column: done
assignee: qwen
project: templeton-lab
depends_on: ["card-002"]
created_at: 2026-10-14T08:35
updated_at: 2026-10-15T03:55
---

The single page is outgrowing itself (CEO note 2026-10-14). Split the
dashboard into pages/tabs — Board, Pings, Roster, Builds, Events — with
click-through detail drawers (card, message, build, agent entry) that open
the full artifact instead of a summary. Keep the static-file fallback
working; the /raw/ browse route stays as the escape hatch.

## Delivered (2026-10-15)

- Tab pages: Board | Pings | Roster | Builds | Events (hash-routed;
  works from file:// and via serve.py).
- Detail drawers: click any card, ping, build, agent, inbox, or decision
  to open the full artifact (frontmatter table + body + source link).
  Inbox drawers list unread messages; each opens in the drawer.
- Roster tab gained a Decisions table (decision-001..003 clickable).
- Artifact bodies embedded as JSON in the page — drawers work with no
  server; /raw/ browse route remains as escape hatch.
- serve.py now reloads the dashboard module per request — generator
  edits apply without a server restart (the stale v1 server was
  silently overwriting v2 output; caught, fixed, verified live).
- Verified: artifacts JSON parse (8 cards, 6 agents, 3 builds, 3
  decisions), all tab/drawer markers, live server HTTP 200, /raw 200,
  ping drawer round-trip via smoke-test ping (processed to done/).
