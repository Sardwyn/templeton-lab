---
id: emergent-harness
title: Emergent Harness (research)
status: active
owner: brad
repo:
path: F:\Lab\harness
memory_cell: project-emergent-harness
updated_at: 2026-11-09T03:10
---

**What it is:** a minimal system fed only state (numbers), difference,
sequence (ordering), and one error magnitude in [0,1]. No objects, labels,
entities, graph, time axis, self, or cause. The question: what has to be added
before prediction, identity, continuity, causality, agency, and self appear --
and does the system stop short of building a world model?

**Why it matters to the org:** it is the only project here that tests the
org's own claim-making machinery. If a system with no priors recovers only what
its author planted, that is a warning about every "we found a pattern" claim
the org makes.

## v0.1 (closed)

- System: `F:\Lab\harness\core.py` (~350 lines, stdlib), priors P0-P6 in code,
  no per-scenario knob, no retained derived structure (audit-checked).
- Claim suite: 10 scenarios x 2 readings = 20 runs, **0 failing claims**;
  control (36 random states) yields 0 classes and declines 18/18 positions.
- Cut: derived from the nearest-neighbour gap (ratio >= 2.0), swept across each
  gap at 15/50/85% and once outside it -- **0 verdicts moved**.
- Audit: **AUDIT CLEAN** -- no forbidden vocabulary, live instance holds only
  `[episode, memory, tau]`, memory entry is `(tuple, float)`.
- Evidence: `F:\Lab\trials\evidence\harness-v01\evidence.json`; write-up
  `F:\Lab\harness\README.md` + `RESULTS.md`.
- **E1 (order test, pre-registered): FAIL by its own rule.** Partition
  invariance PASS (3 classes, [9,9,9] in cycle / rotate / grouped), refusal
  PASS, prediction sensitivity PASS but weak (9/9 -> 8/9, miss at the seam),
  rotation identity of the degree graph FAIL. Cause proven: edges are identical
  as a cycle and differ only as a finite sequence; the stream's first and last
  state each lose one edge. Not position memory; a two-ended-stream artifact
  that every degree-based reading (causality hub, agency fork) inherits.

## The falsification ladder

The mechanism is frozen in `F:\Lab\harness\FREEZE.md` (full hashes, fixed
parameters, P0-P6 verbatim, P0 flagged as the architectural assumption,
structure and prediction reported independently, failed-claim rule). The ladder
attacks a different source of false confidence at each rung.

| rung | question | status |
|---|---|---|
| **E1b** | Is the rotation claim true for the graph a finite stream actually supports? | **DONE, PASS 2026-11-09** -- B1 cyclic edge multiset, B2 presence degrees, B3 two seam violations, B4 seam-only prediction drop. E1 itself stays FAIL. |
| **E2** | Can recurrence predict through fixed-lag interleaving beyond a raw-prefix nearest-neighbour lookup with the same information? | **FAIL 2026-11-09** — structure and the harness's own prediction pass, but B1 ties at 1.000; the feed is periodic at K=3. See `harness/e2-prereg.md`. |
| **E3** | Does relational structure survive a coordinate transformation? | **FAIL 2026-11-09 (outcome d)** — 6 classes, no transfer in the primary separate reading; joined reading transfers 3/3 (outcome c). v0.1 groups by state proximity, not delta shape. See `harness/e3-prereg.md`. |
| **E4** | Does the cut survive n up to 500 and 16 dimensions, or is 1.987-vs-2.0 a small-n accident? | **FAIL 2026-11-09 on power** — null side clean (FPR 1/750, Wilson upper 0.0075), but structured cut-inside is 0.00-0.02 against a 0.80 bar. **Cross-cutting validity test.** See `harness/e4-prereg.md`. |
| **E5** | Can the results survive a feed authored by Brad, not by the system's author? | **FAIL 2026-11-09** — blind feed ran once: 0 classes, no gap, 0/6 held positions answered; pre-holdout probe named a class, but adding the held data erased the cut. See `harness/e5-prereg.md`. |

E4 runs in its numbered position but its result is applied to how E2 and E3 are
read. A failure in E4 does not retroactively pass or fail them; it changes what
their passes are worth.

E2 failed on P2 because the interleaving is periodic: the 6-state cycle repeats,
so a raw 3-prefix recurs with the same successor and the baseline ties at 1.000.
The harness's structure and its own prediction were perfect; recurrence simply
added nothing over raw lookups on that feed. That is the negative the rung
existed to be able to return.

E3 failed as outcome (d): the same triangle translated into a disjoint pair of
coordinates became six classes, not three, and the planted correspondence did not
transfer through the derived cut (2/3 in the separate reading). The joined
reading restores the cycle-closing transitions and transfers 3/3, but it is not
primary. The negative is definitional: v0.1 has an operator over state proximity,
not over delta shape.

E4 failed on power while passing the null: the chance ratio does not grow with n
and shrinks with dimension (median 1.272 at dim 4, 1.095 at dim 16), so the
1.987-vs-2.0 margin is not a small-n artifact. But the structured feed carries
only one between-cluster nearest-neighbour distance, and `MIN_SIDE=2` needs two
on each side of the cut, so the derived cut cannot sit inside the authored
separation (power 0.00-0.02). E4 therefore does not validate the cut at scale; it
shows the cut's validity interval is empty on a two-point-per-cluster signal.

E5 failed on Brad's blind feed, and the failure is about the cut rather than the
feed. The feed's probe named a class before holdout, so a cut existed at 24
states. After the two held episodes were delivered, the completed 30-state feed
had no admissible gap: `tau` became undefined, `classify` returned `None`, and
every held position was declined in both readings (0/6 answered). The cut is
recomputed from all memory on every call, so adding data can erase a separation
that was there. That is the honest negative E5 existed to return, and it is not
repaired by editing the feed or the claims. A second attempt is E5b with a new
feed hash and its own pre-registration.

## Three definitional findings (ruled 2026-11-09)

1. **E3 as originally stated is vacuous.** P1 is mean absolute deviation, which
   is permutation-invariant, so a pure component permutation changes no
   distance, no cut, no class, and no prediction. E3 was redefined as
   coordinate-disjoint isomorphic families; the only pass is 3 classes at the
   same cut, which v0.1 is expected to fail because it has no operator over
   delta shape. Recommended: accept the redefinition and record the negative,
   or drop E3 rather than run a test whose pass condition is unreachable.
2. **E2's baseline.** Exact-suffix longest match is a strawman under jitter (it
   will answer almost nothing). The fair comparator is raw-prefix nearest
   neighbour with the same K, same cut, same memory, which has strictly more
   information than the harness. Recommended: B1 primary, B0 reported floor.
3. **E4's acceptance band.** Recommended: pooled 95% Wilson upper bound on the
   false-positive rate <= 0.05, per-cell structured power >= 0.80, per-cell FPR
   descriptive with a 0.10 flag. A per-cell alpha 0.05 criterion needs ~60
   feeds/cell and is much stricter; it would fail E4 on multiple-comparison
   grounds as much as on method grounds. Confirm the pooled band or choose the
   per-cell one before the run.

**Ruled 2026-11-09:** Brad accepted the recommendation on all three. E3 is the
frozen coordinate-disjoint rung; E2 uses B1 primary and B0 as the reported
floor; E4 uses the pooled Wilson band. All three preregs are frozen.

## Standing caveat

Every v0.1 feed and claim was written by the same agent. A pass means "authored
structure is recoverable", not "no world model". E1 removed one specific way a
world model could hide (position memory) and found a two-ended-stream artifact
instead. E5 is the only rung that removes the feed's author.

**A cut is cheap. What it carries is not.**

## Files

`harness/README.md`, `harness/RESULTS.md`, `harness/FREEZE.md`,
`harness/e1-prereg.md`, `harness/e1b.py`, `harness/e1b-out.txt`,
`harness/e2-prereg.md`, `harness/e3-prereg.md`, `harness/e4-prereg.md`,
`harness/e5-prereg.md`, `harness/e3.py`, `harness/e3-out.txt`, `harness/e4.py`,
`harness/e4-out.txt`, `harness/e4.json`, `harness/e5.py`,
`harness/e5.py.sha256`, `harness/feeds/README.md`, `harness/out.txt`,
`harness/sweep.txt`.
