---
id: adaptive-kv
title: llama.cpp Adaptive KV (research)
status: parked
owner: brad
repo: 
path: C:\Users\sardw\llama.cpp-adaptive-kv
memory_cell: project-adaptive-kv
updated_at: 2026-10-29T04:40
---

**What it is:** Brad's llama.cpp fork experimenting with adaptive KV-cache
eviction (HSTU, group queries, sliding-window, hybrid).

**Where we're at:** the org's part is done — card-010 mapped the repo
(37 evictors, ~120/126 CUDA kernels patched, Qwen2-0.5B experiments,
results under `results/exp-*/`). Findings cross-linked to muLattice in
`org/notes/mulattice-llama-kv.md`. Nothing has run through the org pipeline
from this repo.

**Next:** parked until Brad asks for an eval run or a muLattice-vs-adaptive-KV
comparison.
