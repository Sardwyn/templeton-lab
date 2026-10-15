---
id: project-mulattice
kind: project
key: mulattice-research
updated: 2026-10-15T04:10
supersedes: []
confidence: high
---

**muLattice** (C:\Users\sardw\mLattice, local clone + venv) — Brad's research:
a dynamically allocated memory lattice for sequence models. Each token
reads/writes exactly 9 cells on a 2D lattice; flat per-token cost (9.5-9.8us,
7,280x fewer ops than attention at 131K). CPU kernel tests pass via the org
pipeline (build-20261015-003). Cross-link to his llama.cpp-adaptive-kv work:
org/notes/mulattice-llama-kv.md. NOTE: "the Lattice" as a *memory system* is
meant for Qwen (me) — see memory/core.md.
