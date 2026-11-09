---
id: card-021
title: Harness falsification ladder - E1b, E2, E3, E4, E5
column: in-progress
assignee: qwen
project: emergent-harness
depends_on: [card-020]
created_at: 2026-11-09T01:28
updated_at: 2026-11-09T01:55
---

Each rung is pre-registered before its run and each is allowed to fail. One
rung per sitting; do not batch. The mechanism is frozen by
`F:\Lab\harness\FREEZE.md` (v0.1 hashes, P0-P6, fixed parameters, reporting
rule, failed-claim rule). `core.py` may not change to make a rung pass; if a
rung needs a change, the need is the result.

**Order:** E1b, E2, E3, E4, E5. E4 is a cross-cutting validity test: it runs in
its numbered position, and its result changes what the E2/E3 passes are worth,
but it does not retroactively pass or fail them.

## E1b — DONE (PASS, 2026-11-09)

Post-hoc restatement of E1's C2, recorded in `harness/e1-prereg.md` (Amendment
E1b) and run by `harness/e1b.py` -> `harness/e1b-out.txt`. All four claims pass:

- **B1** circular edge multiset identical after relabelling (return edge added);
  as a finite sequence the edges differ. PASS.
- **B2** successor and predecessor presence sets identical after relabelling;
  the count delta is confined to one edge (one class +1 inbound, one -1; out 0
  everywhere). The originally drafted "end-excluded degree counts" claim was
  false and was replaced before the run. PASS.
- **B3** exactly 2 of 8 inter-episode edges violate `next = current+1 mod 3`,
  at block starts 3 and 6, types `(2->1)` and `(0->2)`; no within-episode
  violation. PASS.
- **B4** grouped joined 8/9 vs rotate 9/9, the only miss at the seam, all 6
  within-episode positions intact. PASS.

This closes the definition, not E1: E1 stays FAIL on its original claim set.
The two-ended-stream artifact is now a named architectural limit of every
degree-based reading, not a surprise.

## E2 — pre-registered, pending ruling (not run)

Fixed-lag interleaving of two 3-cycles (A0 B0 A1 B1 A2 B2, lag 2), so the next
state is not in the literal prefix. Pass = six classes at the derived cut, no
cross-family merge, harness accuracy >= 0.80, and harness beats a **raw-prefix
nearest-neighbour baseline with the same K, same cut, same memory** by >= 0.10
on paired positions. Exact-suffix longest match is the reported floor.
See `harness/e2-prereg.md`.

**Open ruling:** B1 raw-prefix NN is the primary comparator (recommended);
B0 exact-suffix alone is a strawman under jitter.

## E3 — redefined, pending ruling (not run)

The original E3 is a no-op under P1: mean absolute deviation is
permutation-invariant, so a pure component permutation changes nothing. The
redefinition uses coordinate-disjoint isomorphic families (triangle in
components 0,1 vs the same triangle in 2,3, separated by > the cut). Outcomes:
(a) 3 classes at the same cut = PASS; (b) 3 only after raising the cut = cut
shopping; (c) 6 classes but prediction transfers under the planted permutation;
(d) 6 classes, no transfer. Only (a) passes. Expected (c) or (b): v0.1 has no
operator over delta shape, only over state proximity. See `harness/e3-prereg.md`.

**Open ruling:** accept the redefinition and its expected negative, or drop E3
rather than run it in a form whose pass condition is unreachable.

## E4 — pre-registered, pending ruling (not run)

n in {18, 50, 120, 300, 500}, dim in {4, 8, 16}, 50 independent random and 50
independent structured feeds per cell. Report median / p90 / p95 / p99 / max
chance NN ratio, derived cut, cut-inside-authored-interval, and false-positive
rate. Pass: pooled 95% Wilson upper bound on FPR <= 0.05 and per-cell structured
power >= 0.80. Per-cell FPR is descriptive (flag > 0.10), not a pass criterion.
The 1.987 vs 2.0 margin is the thing under test. See `harness/e4-prereg.md`.

**Open ruling:** pooled FPR band (recommended) vs per-cell FPR at alpha 0.05
(needs ~60 feeds/cell and is much stricter).

## E5 — protocol frozen, feed pending

Brad writes one JSON feed (states, errors, episode boundaries, holdout, probes,
claims) without describing the generator. `harness/e5.py` re-checks the freeze,
prints and records the feed hash, runs it unchanged, and publishes every row,
including failures and n/a. No tuning after; a change is E5b with a new feed
hash. The claim vocabulary is fixed in `harness/e5-prereg.md`. E5 is the only
rung that removes the feed's author. See `harness/e5-prereg.md`.

## Discipline

`FREEZE.md` is the contract: fixed hashes, P0-P6 verbatim, P0 flagged as the
architectural assumption, structure and prediction reported independently, a
failed claim never repaired by editing it. A new runner may import the frozen
modules; it may not edit them.

**Artifacts:** `harness/FREEZE.md`, `harness/e2-prereg.md`,
`harness/e3-prereg.md`, `harness/e4-prereg.md`, `harness/e5-prereg.md`,
`harness/e1b.py`, `harness/e1b-out.txt`.
