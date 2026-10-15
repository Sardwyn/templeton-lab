---
id: decision-004
date: 2026-10-15
status: active
---

# The Lattice is Qwen's memory (CEO ruling)

Brad, 2026-10-15: "the memory isn't really working the way I intended. The
lattice memory was really meant for Qwen — that's the local model that needs
to remember me, my preferences, the timelines etc."

Ruling:

1. The Lattice (memory/core.md + memory/cells/) is **Qwen's persistent
   memory** — not a general org task system. (The build pipeline in
   mLattice/tasks, card-005, is the org's build machinery — a separate use.)
2. Qwen loads memory at session start (`worker/recall.py`) and writes what
   it learned at session end (`worker/remember.py` / direct cell edits).
3. The dashboard **Memory** tab is the audit view of what Qwen remembers.
4. Memory semantics: hot tier (core.md) always loaded; warm tier (cells/)
   keyed, one file per memory, `supersedes` for overwrites — never delete,
   replace. The org events log remains the raw timeline.
