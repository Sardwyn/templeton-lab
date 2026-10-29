---
id: decision-007
date: 2026-10-29
status: active
title: Projects are first-class org artifacts
decided_by: brad
---

# Decision-007: Projects are first-class org artifacts

**Ruled by Brad on 2026-10-29** ("go ahead" on the card-015 design, with all three
scope recommendations accepted).

## The ruling

1. **`org/projects/<id>.md` is the source** for what a project is and what its
   artifacts are. The dashboard's per-project pages are generated from it, never
   the other way around (decision-005's derived-view rule holds).
2. **Scoping is by reference, not by keyword.** A project artifact names its
   memory cell explicitly (`memory_cell:`), so a project page shows exactly its
   own cell and nothing found by string-matching.
3. **Every card and build carries `project:`.** Back-filled across existing
   artifacts (18 files) so history is scoped too; SOP v1.6 requires it on new
   ones. Events stay unchanged — their `card` / `build_id` / `cell` / `repo`
   refs resolve to a project, which keeps the event log immutable.
4. **No new event types.** The project view is a *view*; projects are artifacts,
   not a verb. `state/PROJECTS.md` is regenerated each check-in like BOARD.md.

## Why

The org had five projects living in memory cells and heads, but no artifact an
agent could open to ask "what is swarm-playpen and what has been done in it".
Project pages close that gap without inventing a second system of record.

## Consequence

- card-015 delivers the pages (single `index.html`, hash route `#proj/<id>`).
- card-016 exists as the owner slot for the swarm-playpen test regression, which
  is unassigned until Brad says fix it.
