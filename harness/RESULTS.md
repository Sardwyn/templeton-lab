# Harness v0.1 — results

Recorded 2026-11-09. Python 3 stdlib only, one machine, deterministic feeds.

```
python harness/run.py          ->  0 failing claim(s)
python harness/run.py --sweep  ->  0 failing claim(s), 0 verdicts moved
python harness/audit.py        ->  AUDIT CLEAN
```

Full output: `out.txt`, `sweep.txt`. Machine-readable copy:
`F:\Lab\trials\evidence\harness-v01\evidence.json`.

20 runs = 10 scenarios × 2 readings (separate / joined). Every scenario has one
harness instance and one feed; probes are asked on the pre-holdout feed, the
structural counts are measured on the completed feed.

## Verdicts

| scenario | measured | reading |
|---|---|---|
| control (null) | gap `None`, 0 classes, 18/18 asked positions declined, accuracy 0.000, class share [0.0, 0.0] | both |
| prediction | gap 72.52, cut 0.20355, 3 classes `[9,9,9]`; accuracy **1.000** (6/9 answered separate, 9/9 joined); support **6** on context `[0,1]`; class errors 0.10 / 0.45 / 0.80 | both |
| identity | 3 classes `[9,9,9]`; a never-delivered state names classes 0, 1, 2 and all three names differ; a state beyond the cut names nothing (`null`) | both |
| continuity | accuracy 1.000; episode-boundary positions declined **3/3** when separate, **0/3** when joined | reading-dependent by construction |
| causality | gap 18.77, cut 0.0543, 6 classes `[9,7,5,3,3,3]`; hub = class 1 (in 9, out 2, `in_src` 3); arrive 0.4006 vs depart 0.1027; mean error at the hub **0.00**; the two exits cost 0.75 and 0.95 | both |
| agency | gap 77.88, cut 0.20141, 7 classes `[9,3,3,3,3,3,3]`; fork = class 1 (in 9, out 3, successor entropy 1.585 vs 0 at every neighbour); rivals `[[2,2,0.20],[4,2,0.50],[6,2,0.80]]` | both |
| self (frame) | gap 41.92, cut 0.10027, 5 classes `[3,3,3,3,3]`; invariant components **[1,2]**; worst single-component movement inside a class 0.0122 against a lower scale of 0.0047 | both |
| self (drift) | gap **2.46**, cut 0.13777; invariant component **[1]**; within-class drift 0.60 against a lower scale of 0.0797 | both |
| witness (equal) | gap 95.99, cut 0.20105, 4 classes `[12,12,6,6]`; rivals `[[2,3,0.25],[3,3,0.60]]` — equal support, different error, **both kept** | both |
| witness (ranked) | gap 72.26, cut 0.15187, 5 classes `[12,12,6,6,1]`; rivals `[[3,3,0.25],[4,3,0.90]]`; the cheaper continuation wins at equal support | both |

Every structural claim is identical in the two readings; only the claims marked
reading-dependent differ, and each of those is reported under its own name
(`*_separate` / `*_joined`) rather than averaged.

## The cut moved

`--sweep` re-runs each feed with the cut at 15 %, 50 %, and 85 % of its own gap,
and once outside it (`hi × 3`).

| scenario | gap (lo..hi) | cut moved inside | cut moved outside |
|---|---|---|---|
| control | no gap | — | imposed 0.10: 0 classes, accuracy 0.000 — refuses |
| prediction | 0.0055..0.4016 | verdicts hold | 3 classes, unchanged |
| identity | 0.0055..0.4016 | verdicts hold | 3 classes, unchanged |
| continuity | 0.0055..0.4016 | verdicts hold | 3 classes, unchanged |
| causality | 0.0055..0.1031 | verdicts hold | 6 classes, unchanged |
| agency | 0.0051..0.3977 | verdicts hold | 7 classes, unchanged |
| self_frame | 0.0047..0.1959 | verdicts hold | 5 classes, unchanged |
| self_drift | 0.0797..0.1959 | verdicts hold | 5 classes, unchanged |
| witness_equal | 0.0041..0.3980 | verdicts hold | 4 classes, unchanged |
| witness_ranked | 0.0041..0.2996 | verdicts hold | 5 classes, unchanged |

Two consequences worth keeping:

- An imposed cut that the feed does not support changes **nothing** — the
  control produces 0 classes at 0.10 and the patterned feeds keep their class
  counts even at `hi × 3`. The cut is derived, not tuned.
- The control's own null result is the load-bearing one: the 36-state random
  feed has no gap (largest chance nearest-neighbour ratio 1.987 against
  `GAP = 2.0`), so every class in the table above was paid for by a real
  separation. The 0.7 % margin is uncomfortably thin and is stated as such.

## Audit

```
1.  forbidden vocabulary in core.py executable lines .... PASS (26 words)
1b. forbidden vocabulary in identifier names ........... PASS (107 names)
2.  nothing derived is retained ........................ PASS [episode, memory, tau]
3.  no per-scenario knob ............................... PASS (tau only, instrument)
4.  memory entry is (tuple, float) ..................... PASS
```

## Three findings the run produced

1. **A probe at the gap's own edge is not a claim.** The identity probe was
   originally the cube centre, which sits at 0.400 from every corner against a
   gap high side of 0.4016 — unnamed only because the cut landed just short.
   The sweep flagged the verdict moving at larger in-gap cuts. It is now placed
   beyond the observed span (nearest recorded observation 0.450), so it is
   unnamed at every cut inside the gap. Recorded because the failure mode —
   a "null result" produced by a coin toss — is exactly the kind of thing this
   suite exists to catch.
2. **The cut estimator is the fragile part, not the pattern.** `self_drift`
   separates by a factor of 2.46, the control's chance maximum is 1.987, and
   `GAP` is 2.0 — the whole operating range of the method at this scale is the
   gap between 1.99 and 2.46. GAP 1.5 would have compressed genuine structure;
   GAP 2.5 would have erased this separation. That margin, not the classes, is
   what E4 has to test at larger n and higher dimension.
3. **The two readings disagree exactly where sequence means something.**
   Joining episodes manufactures a cycle across boundaries (witness_equal
   marginal class entropy 1.500 separate → 1.927 joined, and every class gains
   a successor), while separating them leaves final positions with no successor
   at all (agency fork successors 0 vs 1; causality closes `[2,4]` vs `[]`). The
   disagreement is reported, not suppressed: continuity claims are only
   meaningful when you say which reading you mean.

## E1 — the order test (pre-registered, `e1-prereg.md`)

Run after the frozen build: `python harness/e1.py` → `e1-out.txt`.
Result: **E1 FAIL** — two of four claims held, one failed for a mechanism that
was not the thing under test, one passed only weakly.

| claim | result |
|---|---|
| C1 partition invariance across three orders (up to relabelling) | **PASS** — 3 classes, `[9,9,9]` sizes and the same per-class errors in cycle, rotate, and grouped |
| C2 rotation identity of degrees and competitors | **FAIL** — the directed-edge multiset moves when the order rotates |
| C3 grouped order must drop accuracy, misses only at boundaries | **PASS (weak)** — 9/9 → 8/9, the one miss at the block boundary |
| C4 refusal order-independent in the separate reading | **PASS** — 3 declined / 6 answered in all three orders |

The C2 failure has a precise, non-mysterious cause, and the run proves it: the
directed edges are **identical as a cycle** (return edge added) and differ only
as a finite sequence. A stream has a first state with no predecessor and a last
state with no successor, so rotating the episode order moves which class carries
that one missing edge. Nothing is reading absolute position; the *graph* reading
is reading the stream's two ends.

What E1 therefore established and what it did not:

- **Established:** the recurrence partition is order-invariant, including when
  the order is rearranged into blocks (C1); the harness's refusal at episode
  starts does not depend on where episodes sit (C4).
- **Not established:** prediction is only weakly order-sensitive here. The one
  boundary miss is a real drop, but 8/9 is thin evidence, and the honest reading
  is that v0.1's 1.000 came mostly from within-episode repetition — exactly the
  concern `e1-prereg.md` C3 named in advance.
- **New constraint for v0.2:** any claim that rests on degree structure
  (causality's hub, agency's fork) inherits a two-ended-stream artifact. Either
  the reading is declared circular, or the first and last positions are excluded
  by the reader and said so.

## E2 — fixed-lag interleaving (pre-registered, `e2-prereg.md`)

Run: `python harness/e2.py` → `e2-out.txt`. Result: **E2 FAIL** on P2.

| claim | joined reading |
|---|---|
| S1 six classes of 8, gap ratio ≥ 2, no cross-region merge | **PASS** — 6 classes, `[8,8,8,8,8,8]`, gap 26.433, cut 0.065247 |
| S2 region-to-class bijection, no composite label | **PASS** — one authored region per class |
| P1 harness accuracy ≥ 0.80 | **PASS** — 24/24, 1.000 |
| P2 harness ≥ B1 + 0.10 on paired positions | **FAIL** — harness 1.000 vs B1 1.000, delta +0.000, both answered 24 |
| P3 B0 exact-suffix floor | reported — answered 0, as expected under jitter |

The separate reading is identical in shape and in the tie (20/20 both).

Why: the interleaving is still periodic. One 6-state cycle
(A0 B0 A1 B1 A2 B2) repeats eight times; any raw 3-prefix recurs in the
previous cycle with the same successor, so B1 memorises the period. The
design's local claim — the next state is not in the immediate prefix — was
true and irrelevant. E2 measured the thing it was built to measure and returned
the negative it allowed: on this feed, recurrence adds nothing over raw-prefix
nearest neighbour. A non-vacuous E2b would need a non-repeating stream, or a
successor that depends on more than `K`.

## Evidence file

`evidence.json` holds `priors`, `thresholds` (reader-side: accuracy 0.80, fan 3,
readings), and, per scenario × reading: every asked position with its actual and
predicted class, probe outputs with full competitor lists, class errors, and the
gap/cut used. Regenerate it from the plain run (not `--sweep`) so the recorded
cut is the derived one.
