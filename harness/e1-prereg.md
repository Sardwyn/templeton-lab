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

---

# Amendment E1b — 2026-11-09, after E1 ran

**Status: post-hoc restatement. This is not a new blind test and it does not
turn E1's FAIL into a PASS.** E1's original C1–C4 stay on the record and its
verdict stays FAIL. E1b exists because C2 failed for a reason that was not the
thing under test, and the failure would otherwise be open to two dishonest
readings: "the classes encode position" or "it is only a bookkeeping detail".
Neither is established. The claim is restated precisely and measured once.

E1's own diagnostic already established the mechanism: the directed-edge
multiset is **identical as a cycle** (return edge added) and differs only as a
finite sequence. A stream has one first observation with no predecessor and one
last with no successor; rotating the episode order moves which class carries
each missing edge. The restatement below separates the invariant part from the
artifact part. It was written before `e1b.py` was created and its expected
values are already known from E1's diagnostic, which is exactly why it is
labelled an amendment rather than a prediction.

## New claims

**B1 — circular edge invariance.** Up to a bijective relabelling of class ids,
the directed-edge multiset of `cycle` and `rotate`, **including the return edge
`(last class → first class)`**, is identical. This is the graph object a finite
stream actually supports. PASS if the sorted edge multisets are equal after the
relabelling.

**B2 — presence-degree invariance.** Up to the same relabelling, every class has
the same **set** of successor classes and the same **set** of predecessor
classes. Transition **counts** are not claimed to be invariant: the linearisation
drops one cyclic edge, so at most one class loses one inbound count and one
class loses one outbound count. The exact count delta is reported per class.
PASS if every successor set and predecessor set matches after relabelling, and
the count deltas are confined to the single linearisation edge (no class has a
presence difference).

This is deliberately weaker than the original C2 and stronger than "the edges
are equal as a cycle": it says the **neighbourhoods** survive rotation even
though the counts cannot.

**B3 — grouped seam accounting.** In the `grouped` order, with the class rule
`next = current + 1 (mod 3)`, exactly **2 of the 8 inter-episode edges** violate
the rule, both at block starts, with transition types `(2→1)` at the T1→T2 seam
and `(0→2)` at the T2→T3 seam. Every within-episode edge satisfies the rule.
PASS if the violation count is 2, both are at block starts, and both types are
exactly those two.

**B4 — restated C3, with the floor made explicit.** In the joined reading,
`grouped` accuracy is strictly below `rotate`; **every** miss is at a block
boundary; and **no within-episode position degrades** (every answered
non-boundary position is a hit). The separate reading is unaffected and is
reported for completeness, not as part of B4.

## Pass / fail

E1b **passes** if B1–B4 all hold. It **fails** otherwise, and the failure is
recorded as a failure of the restatement. A fail on B1 or B2 means the
recurrence graph is genuinely position-dependent; a fail on B3 means the seam
accounting is wrong and E1's C3 diagnosis needs re-deriving; a fail on B4 means
the "drop only where the information was removed" claim is false.

## What E1b does not establish

- It does not remove the author, the feed, or the same nine episodes. It is a
  definitional closure of E1, not independent evidence.
- It does not test composition, substitution, or scale. Those remain E2, E3,
  E4.
- It cannot show that the degree readings are safe in general; it shows only
  that *this* cycle's neighbourhoods survive *this* rotation. The two-ended
  stream artifact is still present in every finite feed and is now a named
  architectural limit, not a surprise.
- Passing B1–B4 does not make E1 a pass. The original claim set is unchanged.

## Run protocol

```
python harness/e1b.py           # writes e1b-out.txt, appends nothing else
```

`e1b.py` imports `e1.build`/`e1.run` and never edits `e1.py`. It re-checks the
frozen hashes in `FREEZE.md` and aborts on any difference.
