# μLattice × llama.cpp-adaptive-kv — cross-link note

(qwen, 2026-10-15 — from card-006 verification: CPU tests via org pipeline,
PAPER.md + LIMITATIONS.md read in full)

## What we verified on this box

- `tests/test_kernel.py` (40 checks) **PASS** via the org build pipeline
  (build-20261015-003; first attempt build-20261015-002 failed on a Windows
  cp1252 console-encoding issue, fixed with PYTHONIOENCODING=utf-8).
- Flat-cost claim reproduced on CPU at scale: per-token cost 56.8 → 65.9
  µs/token/seq (ratio 1.16) while allocated cells grew 9,504 → 293,795.
- Content-addressing invariants hold: 2D fan-out exactly 9, batched scan ≡
  cell-parallel scan ≡ hash-map lattice, packed keys overlap 1.000 vs
  spread keys 0.000, gate/floor/escalation behavior verified.

## What it is, in one breath

Each token reads/writes **exactly 9 cells** (3×3 bump kernel) on a
dynamically allocated 2D lattice of gated-delta states. Per-token access is
O(1) by construction; storage grows with distinct addresses. At 131K tokens:
7,280× fewer ops than attention (151M cell accesses vs 1.1T key-query
comparisons), recall 1.0000 on capacity/forgetting/real-text protocols.

## Bridges to adaptive-KV work

1. **The cell IS an adaptive KV entry** — but content-addressed, not
   position-addressed. The learned address projection replaces positional
   indexing; your KV eviction problem becomes its *address-scale / density*
   problem (recall degrades above ~0.22–0.25 keys/cell — a soft ceiling).
2. **Overwrite without deletion** — the gated delta rule
   (`W ← αW + β(v − v̄)κᵀ`) algebraically cancels stale values. That is
   exactly the property KV eviction heuristics approximate; here it is
   structural (0.998 updated / 1.000 untouched at 50% overwrite).
3. **Flat-cost target property** — adaptive KV *approximates* flat
   per-token cost via retention budgets; μLattice achieves it
   architecturally (measured: 9.3 → 9.0 µs/tok from 1K→131K tokens, while
   cells grew 1,246 → 37,100).
4. **Memory budget number** — ~8 KB per stored pair (2 heads × 32×32 × 4 B,
   ~1 cell/pair); 131K pairs ≈ 0.9 GB. A concrete figure for budgeting any
   lattice-style memory in a llama.cpp runtime.
5. **Bolt-on pattern** — the 10.8M-param bridge (8 soft tokens into a frozen
   Qwen3.5-4B) is the template for adding lattice memory to a *frozen*
   model without retraining the backbone (fresh-fact recall 0.645 vs 0.025
   floor; 1.000 RAG ceiling). If a lattice mixer ever needs to sit beside a
   stock llama.cpp model, this is the attachment path — note their
   *direct* bolt-on to a frozen 3B failed; the soft-token bridge is what
   worked.
6. **Known gaps to respect** — no LM-pretraining results; Copy/positional
   echo fails (0.003, no positional encodings); single-run reporting for
   capacity/forgetting; 3D addressing (27 cells, ~3 orders of magnitude
   density headroom) is kernel-supported but unimplemented.

## Open threads (for Brad / Copilot)

- The 131,072-pair benchmark (scale ~385) is untested — a natural next
  experiment if capacity, not cost, becomes the question.
- Whether the density-ceiling math (~0.22 keys/cell) maps cleanly onto
  adaptive-KV retention budgets is the single most useful thing to
  investigate for the llama.cpp side.
