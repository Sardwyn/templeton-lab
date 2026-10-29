---
id: card-015
title: Projects as first-class artifacts + per-project dashboard page
column: done
assignee: qwen
project: templeton-lab
depends_on: ["card-008"]
created_at: 2026-10-29T04:40
updated_at: 2026-10-29T05:05
---

Brad: the dashboard needs a page per project showing everything done there and
where each project is at. Projects previously existed only as qwen's private
memory cells — no org artifact, no grouping for cards/builds/events.

Ruled scope (Brad chose all three recommendations, 2026-10-29):
1. Pages for **all five** projects (including the quiet ones — honest emptiness).
2. `project:` field **back-filled on every existing artifact** (14 cards + 4 builds).
3. **One index.html**, hash-routed `#proj/<id>`, new Projects tab.

Deliverables:
- `org/projects/<id>.md` — the org's project source (frontmatter: id, title,
  status, owner, repo, path, memory_cell; body: what / where-we-are-at / next).
  `memory_cell:` is an explicit ref, so memory scoping is by ref, not keyword.
- `project:` back-filled on all cards and build artifacts (byte-preserving edit).
- dashboard.py: Projects tab + one pane per project — prose, cards by column,
  builds with pass/fail streak, decisions by mention, the project's memory cell,
  and events scoped by project/card/build/repo/cell refs. Full event log used
  for scoping (the Events tab stays capped at 20).
- `state/PROJECTS.md` — plain-text twin, regenerated every check-in (gitignored).
- SOP v1.6: every new card/build must declare `project:`.
- No new event types: `project` is a ctx field on events.

**Done 2026-10-29T05:05 (qwen).** Delivered as scoped above: five `org/projects/*.md`
sources, decision-007 recorded, `project:` on all 18 existing artifacts, dashboard v2
with a Projects tab and `#proj/<id>` panes (verified live on :8901 — routing, crumb,
memory cell, scoped cards/builds/events all render; Events tab gained a Project column),
`state/PROJECTS.md` in the regenerated set, SOP v1.6, decision-007 memory cell.

Scope boundary found and reported, not fixed: 27 of 72 events stay unscoped because they
name no project artifact (org-level decisions, notes, messages, identity fixes). Those are
HQ-level by nature, so they belong on neither project page — labelled "by mention" for
decisions instead of forcing a scope. The swarm-playpen regression has its own card-016,
unassigned until Brad rules.
