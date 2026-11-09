---
id: card-021
title: Harness falsification ladder - E1b, E2, E3, E4, E5
column: in-progress
assignee: qwen
project: emergent-harness
depends_on: [card-020]
created_at: 2026-11-09T01:28
updated_at: 2026-11-09T03:30
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

## E2 — DONE (FAIL, 2026-11-09)

Fixed-lag interleaving of two 3-cycles (A0 B0 A1 B1 A2 B2, lag 2), 8 episodes,
holdout 4. Frozen after Brad's ruling: B1 raw-prefix NN (same K/cut/memory) is
the primary comparator; B0 exact-suffix is the reported floor.

Result: **E2 FAIL on P2.** Structure and the harness's own prediction both pass:
6 classes `[8,8,8,8,8,8]`, gap 26.433, cut 0.065247, no cross-region merge,
bijection intact, harness 24/24 joined (1.000). But B1 is also 24/24, so
harness - B1 = +0.000 < +0.10. B0 answered 0. The separate reading is identical
(20/20 both).

Cause: the interleaving is periodic. One 6-state cycle repeats eight times; a
raw 3-prefix recurs with the same successor, so B1 memorises the period and the
harness has nothing to add. This is the negative E2 was built to be able to
return, not a repaired pass. A non-vacuous E2b needs a non-repeating stream or
a successor depending on more than K. See `harness/e2-prereg.md` (post-hoc
diagnosis).

## E3 — DONE (FAIL, outcome d, 2026-11-09)

The original E3 is a no-op under P1: mean absolute deviation is
permutation-invariant, so a pure component permutation changes nothing. The
redefinition uses coordinate-disjoint isomorphic families (triangle in
components 0,1 vs the same triangle in 2,3, separated by > the cut). Outcomes:
(a) 3 classes at the same cut = PASS; (b) 3 only after raising the cut = cut
shopping; (c) 6 classes but prediction transfers under the planted permutation;
(d) 6 classes, no transfer. Only (a) passes.

Result: **E3 FAIL (outcome d)** in the primary separate reading, run by
`harness/e3.py` -> `harness/e3-out.txt`. S0 confirms the no-op exactly (worst
distance change under component permutation 0.000e+00). Separate reading: 24
states, 6 classes `[4,4,4,4,4,4]`, gap 28.924, cut 0.066316; every class holds
one authored region (A0/A1/A2/B0/B1/B2), so there are 6 classes not 3; P1 4/6
(the two cycle-closing transitions are declined at episode boundaries); transfers
2/3. The joined reading gets P1 6/6 and transfers 3/3 (outcome c), but it is not
primary and its splices add cross-family edges. No cut up to the largest pairwise
distance yields three paired classes; the first cross-family merge is at tau
0.997273 and gives 2 classes with 0 spanning both families.

This is a classified failure, not a bug: v0.1 groups by state proximity, not by
delta shape, so an isomorphic triangle moved into a disjoint coordinate subspace
becomes a separate set of classes and the planted correspondence does not
transfer through the cut. A reader-side joined-label mapping correction was
applied before the recorded run; the separate verdict was unchanged.

## E4 — DONE (FAIL, 2026-11-09)

n in {18, 50, 120, 300, 500}, dim in {4, 8, 16}, 50 independent random and 50
independent structured feeds per cell. Pass: pooled 95% Wilson upper bound on
FPR <= 0.05 and per-cell structured power >= 0.80. Per-cell FPR is descriptive
(flag > 0.10), not a pass criterion. The 1.987 vs 2.0 margin is the thing under
test. See `harness/e4-prereg.md`.

Result: **E4 FAIL on power**, run by `harness/e4.py` -> `harness/e4-out.txt` +
`e4.json`. The null side is clean: pooled FPR 1/750 = 0.0013, Wilson upper bound
0.0075, no cell above 0.10, no cell with p95 chance ratio >= GAP. Chance ratios
do not grow with n and fall with dimension (median 1.2722 at dim 4 -> 1.0951 at
dim 16). The signal side fails everywhere: structured cut-inside-authored-
interval is 0.02 at n=18 dim=4 and 0.00 in the other 14 cells, against a 0.80
bar.

Cause, identified before the run: the structured feed has exactly ONE
between-cluster nearest-neighbour distance, while `MIN_SIDE=2` requires two
observations on each side of a candidate gap. A single cross-cluster distance can
never open an admissible gap at the true separation, so `gap()` sometimes fires on
a spurious within-cluster gap (gap-found 0.00-0.04) with a cut far below the
authored interval (~0.0004-0.0061 against a width of ~0.10). E4 therefore does
not show that the cut survives scale; it shows the cut's validity interval is
empty on this two-point-per-cluster signal. E2 and E3 are not retroactively
passed or failed.

## E5 — DONE (FAIL, 2026-11-09)

Brad's blind feed `harness/feeds/brad_e5.json` (`e5-brad-weather-001`,
sha256 `88716892b5b5f0b5a2a414f2bca6eaa5b27d852640ac25eaf039c5a834e81bdc`)
was run once, unchanged, by the frozen runner
(`e5.py` sha256 `d2b996408a24faa15aed6761e0939565d3d0e4720707c4022661db3dd13b52c7`).
Validation passed. Result: **E5 FAIL**, identical in both readings.

| claim | need | result |
|---|---|---|
| `gap_ratio_min` | 2.0 | **FAIL** — no gap in the completed feed |
| `answered_min` | 3 | **FAIL** — 0 answered, 6 declined |
| `declined_max` | 10 | pass — 6 declined |
| `probe_named` | true | pass — `[1]` |
| `probe_support` | 2 | **FAIL** — support 1 |

30 states, 10 episodes (1 joined), 0 classes, gap `none`, accuracy 0.000.

The feed is a four-component seasonal-looking cycle, 10 episodes of 3 states,
holdout at episode 8. Before holdout the probe was answered and named class 1,
so a cut existed at 24 states. After the two held episodes were delivered, the
completed 30-state feed has no admissible gap, `tau` is undefined, `classify`
returns `None`, and every held position is declined in both readings. The cut is
recomputed from all memory on every call, and adding data erased the separation
that was there. That is a measured instability of the cut, not a bug and not a
repaired pass.

No feed value was changed and no claim was dropped. A second attempt is E5b with
a new feed hash and its own pre-registration; this feed and output stay on the
record. See `harness/e5-prereg.md` and `harness/e5-out.txt`.

## E5-D — diagnostic: cut stability trajectory (DONE, 2026-11-09)

Brad's follow-up question: is the global cut a stable property of the
observations, or a temporary property of the current sample? Frozen in
`harness/e5d-prereg.md` before the run; run once by `harness/e5d.py` ->
`e5d-out.txt` + `e5d.json`; consistency checks C1–C4 all PASS (feed hash,
p=24 probe facts, p=30 completed-feed facts, reading-independence at every
prefix). This is a diagnosis, not a capability verdict; nothing was repaired.

Findings:

- Admissible only at **p = 23..24 of 30** (stretches: 1..22 no, 23..24 yes,
  25..30 no).
- **Gained at p=23:** ep7.pos1 arrived with its own NN 0.0075 (near-duplicate of
  ep5.pos2); window 0.0075..0.0200 opened at ratio 2.667.
- **Lost at p=25:** ep8.pos0 — the first held observation — arrived with its own
  NN 0.0125 (near-duplicate of ep0.pos0), landing strictly inside the old
  window; best ratio fell to 1.667.
- No earlier observation's NN distance changed at either event: the arriving
  observation alone caused each flip.
- The seasonal continuum never approached GAP = 2.0 on its own (best ratio
  ≤ 1.5 before the near-duplicates, 1.6–1.667 after); the admissible cut grouped
  only near-duplicates (21–22 classes over 24 observations).
- E5's probe was asked at p = 24 — inside the only admissible window — and named
  the near-duplicate class, whose single observed continuation is why
  `probe_support` failed.

Answer, scoped to this feed: the cut was a temporary property of the sample,
created by one near-duplicate and destroyed by another.

## Discipline

`FREEZE.md` is the contract: fixed hashes, P0-P6 verbatim, P0 flagged as the
architectural assumption, structure and prediction reported independently, a
failed claim never repaired by editing it. A new runner may import the frozen
modules; it may not edit them.

**Artifacts:** `harness/FREEZE.md`, `harness/e2-prereg.md`,
`harness/e3-prereg.md`, `harness/e4-prereg.md`, `harness/e5-prereg.md`,
`harness/e5d-prereg.md`,
`harness/e1b.py`, `harness/e1b-out.txt`, `harness/e3.py`, `harness/e3-out.txt`,
`harness/e4.py`, `harness/e4-out.txt`, `harness/e4.json`, `harness/e5.py`,
`harness/e5.py.sha256`, `harness/feeds/README.md`,
`harness/feeds/brad_e5.json`, `harness/e5-out.txt`,
`harness/e5-e5-brad-weather-001.json`, `harness/e5d.py`, `harness/e5d-out.txt`,
`harness/e5d.json`.
