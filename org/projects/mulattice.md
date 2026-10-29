---
id: mulattice
title: muLattice (research)
status: active
owner: brad
repo: 
path: C:\Users\sardw\mLattice
memory_cell: project-mulattice
updated_at: 2026-10-29T04:40
---

**What it is:** Brad's research — a dynamically allocated memory lattice for
sequence models. Each token reads/writes exactly 9 cells on a 2D lattice;
flat per-token cost.

**Where we're at:** org cards 005/006/007 all done: the org build pipeline ran
Brad's CPU kernel tests (`build-20261015-002`, `-003` — review status), the
9-cell model was confirmed, and the adaptive-KV cross-link was recorded
(`org/notes/mulattice-llama-kv.md`). Local clone + venv, not on GitHub.
Numbers: ~9.5-9.8 us/token, 7,280x fewer ops than attention at 131K.

**Next:** Brad drives; the org stands by to run kernels or host results when
asked. (Terminology note: "the Lattice" as a *memory system* means qwen's
memory, not this project — decision-004.)
