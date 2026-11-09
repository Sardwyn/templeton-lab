# E1 pre-registration — does the harness read order, or position?

**Frozen 2026-11-09, before any E1 code was written or any E1 feed was run.**

What v0.1 did not show is that the system avoids a world model: every feed was
authored by the person who wrote the claims. E1 is the first test aimed at that.
It asks a narrower question first, one that a position-memorising system fails:

> When the **order of whole episodes** changes but every observation and every
> internal episode sequence stays the same, do the recurrence claims move?

A system that reads states only should not care. A system that reads absolute
position will.

## Frozen system under test

```
core.py        sha256 8734d335a1481042...  (353 lines)
scenarios.py   sha256 bc8e40d22b65b139...  (470 lines)
run.py         sha256 5440c370ff6c5ac7...  (468 lines)
measure.py     sha256 1c9f076dcaafb274...  (173 lines)
```

**E1 may not change `core.py`, `measure.py`, or the `run.py` judge.** New
reader-side code (`harness/e1.py`) and new feed builders are allowed and are
themselves part of the test. If the system needs a change to answer E1, the
need is the result: it means order is carrying something the four primitives
were supposed to leave out.

## Feed

Base episodes are three distinct internal sequences on the four corners used by
v0.1, jittered with the same `jit`/`jittered` helpers and holdout protocol
(3 held episodes, `M.feed` + `M.anticipate`, both readings):

```
T1 = [c0, c1, c2]     T2 = [c1, c2, c0]     T3 = [c2, c0, c1]
```

Nine episodes, three of each type. Three orders are run:

| order | episode sequence |
|---|---|
| **cycle** (baseline) | T1 T2 T3 T1 T2 T3 T1 T2 T3 |
| **rotate** (invariance) | T2 T3 T1 T2 T3 T1 T2 T3 T1 |
| **grouped** (sensitivity) | T1 T1 T1 T2 T2 T2 T3 T3 T3 |

In the joined reading, **cycle** and **rotate** are the same stream up to a
cyclic shift: every consecutive pair is `x -> x+1 mod 3`, so the transition
multiset is identical. **Grouped** keeps every episode intact but breaks the
cycle at two of its eight boundaries.

## Claims

**C1 — partition invariance (must hold).** Across all three orders, up to a
bijective relabelling of class ids: same number of classes (3), same size
multiset (9 each), same per-class mean error. The *episode → class* map must
also agree after relabelling. If it does not, the classes are a function of
episode order — single-linkage is online, so this is the claim most likely to
fail, and a failure here is a result about the method, not a bug to patch.

**C2 — rotation invariance (must hold).** `cycle` and `rotate` must agree
exactly, up to relabelling, on: classes, sizes, per-class mean error, successor
multiset, anticipation accuracy, answered/declined counts, and the ranked
competitor list at every asked position. A difference means the system is
reading position, not transitions.

**C3 — grouped sensitivity (must drop, and only at boundaries).** Accuracy on
`grouped` must be strictly below `rotate`, and **every** miss must be at a
block-boundary position (position 1 of an episode, joined reading). Failure
modes, each a distinct result:

- accuracy stays high with all boundary positions answered correctly: the
  system is reproducing the cycle from the feed's internal episode content
  alone, so "prediction" here is within-episode repetition, not association;
- misses appear inside a block: something other than the order changed, which
  would invalidate the comparison;
- accuracy collapses to 0: the transition table is not doing any work at all,
  and v0.1's 1.000 was an artifact of the cycle being the only pattern in the
  feed.

Predicted values: `rotate` 9/9 joined and 6/6 answered separate; `grouped` 8/9
joined and 6/6 answered separate, the single miss at position 0. **Provenance:**
these numbers were derived from the transition table by hand, then confirmed in
a model-level sanity run before `e1.py` existed; the formal run is `e1.py` and a
mismatch is reported as a discrepancy. A one-position drop is directionally
right but weak evidence on its own — C3 is reported as *weak*, and C1/C2 carry
the weight.

**C4 — refusal is order-independent (must hold).** In the separate reading, the
first position of each held episode is declined in every order: 3 declined of 9
rows, 6 answered, in `cycle`, `rotate`, and `grouped` alike. Refusal must not
depend on where the episodes were placed.

## Pass / fail

E1 **passes** if C1–C4 all hold. E1 **fails** if any of them moves; the failure
record names which claim and prints the actual/expected value side by side. A
failure is not repaired by editing the claim — it is recorded, and the next
rung (E2) is re-scoped in light of it.

No claim here mentions "world model". The specific thing under test is
**order-invariance of the recurrence claims** and **boundary-sensitivity of
prediction**. If C3's first failure mode occurs, that is the closest thing to a
positive result for a constructed world model available at this scale, and it
will be reported in those words.

## What E1 does not establish

- It does not remove the author: the feeds are still written by the same person
  as the claims. E5 (a blind feed from Brad) is the only rung that does.
- It does not test composition, substitution, or scale. Those are E2, E3, E4.
- A pass does not prove no world model exists; it removes one specific way one
  could have been hiding (position memory), and it is the only rung that can be
  decided by numbers this cheaply.

## Run protocol

```
python harness/e1.py            # writes e1-out.txt, appends nothing else
```

`e1.py` records: the three orders' partitions, sizes, errors, degrees,
anticipation rows, and the C1–C4 verdicts. `core.py`'s hash is re-checked at
the top of the run and the run aborts if it differs from the frozen value.
