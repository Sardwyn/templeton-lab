---
id: card-006
title: muLattice research: local clone verification
column: done
assignee: qwen
depends_on: []
created_at: 2026-10-14T06:45
updated_at: 2026-10-15T03:20
---

Research workstream (C:\Users\sardw\mLattice, cloned 14/10/2026):
1. Run CPU unit tests in the local venv: tests/test_kernel.py (~30s),
   tests/test_bridge.py (~10s).
2. Read PAPER.md + LIMITATIONS.md end to end.
3. Note relevance to llama.cpp-adaptive-kv (linear vs quadratic memory,
   9-cell fixed fan-out) in org/notes or an inbox note for the human.
Cross-link findings with the org build pipeline once card-005 lands.

## Delivered (2026-10-15)

- CPU tests run through the org pipeline: tests/test_kernel.py, 40 checks
  PASS (build-20261015-003). First attempt failed on cp1252 encoding
  (build-20261015-002) — fixed with PYTHONIOENCODING=utf-8 in the target.
- PAPER.md + LIMITATIONS.md read in full.
- Cross-link note written: org/notes/mulattice-llama-kv.md (cell = adaptive
  KV entry; delta rule = deletion without eviction; flat-cost target;
  ~8KB/pair budget; bolt-on bridge pattern; known gaps).
