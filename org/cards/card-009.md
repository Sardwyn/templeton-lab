---
id: card-009
title: Qwen memory Lattice — persistent memory for the local agent
column: done
assignee: qwen
depends_on: ["card-003"]
created_at: 2026-10-15T10:45
updated_at: 2026-10-15T10:50
---

Brad's ruling (2026-10-15): "the lattice memory was really meant for Qwen —
that's the local model that needs to remember me, my preferences, the
timelines." Build the Lattice as Qwen's persistent memory:
1. memory/core.md — hot tier (always loaded): identity, Brad, standing prefs.
2. memory/cells/ — warm tier: one file per memory (preference, person,
   project, decision, timeline, lesson, fact), keyed, with supersedes.
3. worker/recall.py — read head: core + standing + recent + topic + org state.
4. worker/remember.py — write head: create/update cells + memory_write events.
5. Dashboard Memory tab (cells + core, drawer-openable).
6. SOP v1.2: memory protocol (session start recall, session end writes).

## Delivered (2026-10-15)

- Core memory + 16 seeded cells (Brad's prefs, people, projects, timelines,
  box lessons) — the first session's learning, captured.
- recall.py verified: full hydration + topic search ("pip" → pip lesson).
- remember.py verified: cell create + memory_write event (shell splits
  multi-word args — use single tokens or a file, per lesson).
- Dashboard Memory tab live (tab, pane, core row, 16 cell rows, drawer).
- SOP v1.2 + qwen charter updated; ruling recorded as decision-004.
