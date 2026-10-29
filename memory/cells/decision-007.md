---
id: decision-007
kind: decision
key: 007
updated: 2026-10-29T04:59
supersedes: []
confidence: high
---

**Brad's ruling (2026-10-29, decision-007): projects are first-class org artifacts.** `org/projects/<id>.md` is the source for what a project is and where it is at; the dashboard's per-project pages (`#proj/<id>`) are generated views. Scoping is **by reference, not keyword**: a project names its memory cell with `memory_cell:`, and every card and build carries `project:` (back-filled across 18 existing artifacts). Events stay immutable — their card/build/cell/repo refs resolve to a project. No new event types; `state/PROJECTS.md` is regenerated each check-in. Consequence: card-015 delivered the pages, card-016 is the owner slot for the swarm-playpen test regression and stays unassigned until Brad rules. Full: org/decisions/2026-10-29-projects-first-class.md.
