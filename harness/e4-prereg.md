# E4 pre-registration — does the cut survive scale, or is 1.987-vs-2.0 a small-n accident?

**FROZEN 2026-11-09, after Brad's ruling: the pooled 95 % Wilson upper bound on
the false-positive rate is the FPR criterion, with per-cell power and
cut-inside ≥ 0.80 and per-cell FPR reported descriptively.** No E4 feed had been
run when this was frozen. The mechanism is frozen by `FREEZE.md`.

## Why E4 is the cross-cutting rung

v0.1's whole operating range is the strip between two numbers:

```
control (36 random states)      largest chance NN ratio   1.987
GAP (the rule)                                            2.000
weakest real separation (self_drift)                      2.460
```

That is a 0.7 % margin on the control side and a 23 % margin on the signal side,
at n = 18 and dim = 4. If the chance ratio grows with n or dimension while the
authored separation does not, the method is a small-n artifact and every E2/E3
pass is worth less. E4 measures the chance distribution directly and reports the
false-positive rate, not just whether one control happened to fail to find a gap.

## Grid and sample sizes

```
n    ∈ {18, 50, 120, 300, 500}
dim  ∈ {4, 8, 16}
R    = 50 independent feeds per cell, random
R    = 50 independent feeds per cell, structured
```

15 cells × 100 feeds = 1500 feeds. Every feed gets an independent seed derived
from `(n, dim, kind, index)`. No feed is reused. The feed order is the order in
this file; no cell may be dropped after seeing a result.

## Random feeds — what chance looks like

Each state is `dim` independent draws from `Uniform(0, 1)`. The `n` states are
split into 6 episodes for the harness's memory layout; the gap is computed over
all observations, so the episode split does not change the nearest-neighbour
distribution, only the compression. Record for every feed:

- **chance ratio** = the largest valid consecutive ratio in the sorted positive
  nearest-neighbour distances, over the same scan `gap()` uses
  (`MIN_SIDE` observations on each side of the split, `lo > EPS`). This is
  defined even when no cut is derived.
- **derived cut** = `gap()`'s cut, or `None`.
- **false positive** = `gap() is not None`, i.e. the feed produced a cut that
  the system would act on.

Report per cell: median, p90, p95, p99, and max chance ratio; the number and
fraction of false positives; the median derived cut when one exists. Also report
the trend by `n` and by `dim` separately (median and p95 across the other axis).

## Structured feeds — what a real separation looks like

Two clusters of `n/2` states. Cluster centres are `0` and `D·1` with
`D = 0.12` per component; each coordinate is jittered `Uniform(-0.01, 0.01)`.
The states are shuffled into a deterministic order and split into 6 episodes.
This authors a clean separation: within-cluster nearest-neighbour distances are
small, cross-cluster nearest-neighbour distances are large.

For each structured feed, compute the **authored separation interval** from the
actual geometry, not from a formula:

```
lo_auth = max over points of (distance to nearest other point in the same cluster)
hi_auth = min over points of (distance to nearest point in the other cluster)
```

If `lo_auth >= hi_auth`, the feed did not author a separable interval; count it
as `not_separable` and report it. Otherwise the interval is `[lo_auth, hi_auth]`.

Record: chance ratio; gap found; derived cut; **cut inside the authored
interval** (strictly `lo_auth < cut < hi_auth`); class count; whether the class
count is exactly 2. Report per cell: median chance ratio, gap-found fraction,
cut-inside fraction, class-2 fraction, median cut, median interval width.

## Acceptance band

The pass criteria are fixed here and may not be moved after the run.

**FPR — pooled, not per cell.** Pool all random feeds across the 15 cells
(750 feeds). Let `k` be the number of false positives. The 95 % Wilson upper
bound on the false-positive rate must be **≤ 0.05**. With 750 feeds, this is
roughly "at most 1 false positive in 750" for the bound to stay at or below
0.05; the exact bound is computed and printed.

Per-cell FPR is **reported but not a pass criterion**, because 15 independent
95 % cells would have a large family-wise error rate and would make the rung
almost certain to fail for reasons unrelated to the method. A cell whose
observed FPR is above 0.10 is flagged for follow-up, not used to fail E4 by
itself.

**Power — per cell.** At least **0.80** of the 50 structured feeds in each cell
must derive a cut that lies strictly inside that feed's authored interval. This
is the probability that a real separation is found and placed correctly.

**Placement — per cell.** The cut-inside fraction is the same measurement as
power above; it is reported separately so that "gap found" and "gap found in the
right place" cannot be conflated. A feed with a derived gap outside the authored
interval counts as a detection failure, not a success.

**Trend — descriptive, and the early warning.** Report median and p95 chance
ratio against `n` and against `dim`. The shape matters more than n = 500. In
particular, report at which cells `p95 ≥ GAP`; those are the cells where the
method's false-positive rate is structurally at risk even if the sample FPR is
low. The trend is not a pass/fail criterion, but it is the main result if E4
passes narrowly.

## Pass / fail

E4 **passes** if:

1. the pooled 95 % Wilson upper bound on FPR is ≤ 0.05; and
2. every cell's structured power (cut strictly inside the authored interval) is
   ≥ 0.80.

E4 **fails** if either condition fails. A fail is reported with the cell(s)
that failed, the observed FPR, and the chance-ratio distribution. No parameter
(`GAP`, `MIN_SIDE`, `K`, `R`, `D`, jitter) may be changed after seeing the
result. If `GAP` needs to change, that is a **v0.2 experiment**, not a repair of
E4: new pre-registration, new run, new baseline for every later rung.

## What E4 does not establish

- It does not test a non-uniform world. Random uniform states are the null; a
  structured world with heavy tails, correlation, or a different metric could
  behave differently. The claim is about this null, at these dimensions.
- It does not test the *content* of the classes, only whether a cut is found
  and placed inside a known interval. A feed can pass E4 and still have
  meaningless class semantics.
- It does not remove the author: the structured feeds are generated by the same
  agent as the claims. E5 is the only rung that does.

## Ruling (2026-11-09)

Brad ruled: **the pooled band above is the criterion** — 95 % Wilson upper bound
on the pooled false-positive rate ≤ 0.05, per-cell structured power and
cut-inside ≥ 0.80, per-cell FPR descriptive with a 0.10 flag. The alternative
(per-cell FPR at α = 0.05, ≈ 60 feeds per cell) was not chosen; it would make E4
fail on multiple-comparison grounds as much as on method grounds. This section
is no longer open.

## Run protocol

```
python harness/e4.py            # writes e4-out.txt and e4.json, appends nothing else
```

`e4.py` re-checks the `FREEZE.md` hashes, prints the per-cell table first, then
the pooled FPR and the trend, then the verdict. `e4.json` holds every feed's
seed, n, dim, kind, chance ratio, cut, and interval, so the distribution can be
re-derived without re-running. The run is expected to take minutes, not seconds;
it must be run once, unmodified.
