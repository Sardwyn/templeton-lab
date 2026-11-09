# E3 pre-registration — coordinate-disjoint families, and what "same shape" can mean

**PROVISIONAL. Not frozen until Brad rules on the redefinition in §Open
decision.** No E3 feed has been run. The mechanism is frozen by `FREEZE.md`.

## The problem with E3 as first stated

The first draft said: "two families with the same delta shape, components
permuted; pass if one class at one cut covers both and prediction transfers for
free." That is **vacuous under P1**. The magnitude is the mean absolute
deviation over components:

```
_dist(x, y) = mean_c |x_c - y_c|
```

which is invariant under any permutation of the component index. Permute every
state's coordinates and every distance is unchanged; therefore the gap, the cut,
the partition, and every prediction are unchanged. A pure component permutation
is a relabelling of the input, not a transformation the system can notice. It
cannot distinguish "found a schema" from "the metric is symmetric".

So E3 must be non-vacuous. The version below is the smallest one that is:

> Two families occupy **coordinate-disjoint subspaces**. Within each family the
> state-to-state delta vectors are the same up to a component permutation. The
> families are separated by more than the cut. Does the system unify them into
> one recurrence at the same cut?

A system that groups by proximity cannot. A system with an operator over delta
shape could. v0.1 has no such operator, so the expected result is negative — and
the point of E3 is to make the negative precise, not to give the mechanism a
comfortable pass.

## Feed

Family A, a triangle in components 0 and 1:

```
A0 = (0.00, 0.00, 0, 0)
A1 = (0.50, 0.00, 0, 0)
A2 = (0.25, 0.40, 0, 0)        cycle A0 -> A1 -> A2 -> A0
```

Family B is the same triangle in components 2 and 3, translated so the families
are disjoint:

```
B0 = (0, 0, 2.00, 2.00)
B1 = (0, 0, 2.50, 2.00)
B2 = (0, 0, 2.25, 2.40)        cycle B0 -> B1 -> B2 -> B0
```

With `perm = (2, 3, 0, 1)` (swap the two coordinate pairs) and
`t = (0, 0, 2.0, 2.0)`, `B_i = perm(A_i) + t`. The **delta vectors** of B are
exactly `perm` of the delta vectors of A:

```
A1-A0 = ( 0.50, 0.00, 0, 0)      B1-B0 = (0, 0,  0.50, 0.00)
A2-A1 = (-0.25, 0.40, 0, 0)      B2-B1 = (0, 0, -0.25, 0.40)
A0-A2 = (-0.25,-0.40, 0, 0)      B0-B2 = (0, 0, -0.25,-0.40)
```

Within-family distances are ≈ 0.47–0.50; every cross-family distance is
≈ 2.8–3.3. Jitter is the existing helper, amplitude `0.008`, on components 0
and 3. Four cycles of each family, as eight 3-state episodes,
`holdout_from = 4`. **The separate reading is primary** because each family is a
closed cycle; the joined reading is reported but its splices add artificial
cross-family edges.

## Claims

**S0 — the no-op is measured, not asserted.** For every pair of authored base
states, `_dist(x, y) == _dist(perm(x), perm(y))` within `1e-12`. This is a fact
about P1. It is reported first, because it is why the original E3 cannot stand.

**S1 — the families stay separate at the derived cut.** At the cut the harness
derives, there are 6 classes, each containing only states from one family. The
gap ratio is ≥ `GAP`. This is the expected structural result.

**S2 — no class contains both families.** Each class's members come from one
authored family. A cross-family class at the derived cut is the only thing that
would make E3's (a) true; it is checked explicitly.

**P1 — within-family prediction works.** After the feed, `expect([A0, A1])`
predicts A2, `expect([A1, A2])` predicts A0, `expect([A2, A0])` predicts A1,
and the same for B. All 6 probes are reported. This is a within-family claim,
not the E3 claim.

**P2 — transfer is measured, not assumed.** Build the class correspondence from
the known state correspondence: A_i's class ↔ B_i's class. For each of the 3
cycle transitions, ask the system to predict the next B class from a B prefix,
map that class back to A's label, and compare with the system's prediction from
the corresponding A prefix. Report the number of transfers (0–3). Because the
families are isomorphic by construction, transfer is expected; the reader
supplied the permutation, so transfer is **not** evidence of a discovered
schema.

## The four outcomes

E3's result is a classification, not only a pass/fail:

- **(a) same class at the same cut** — 3 classes at the derived cut, with each
  class containing both A_i and B_i. **This is the only pass.** It would mean
  the system unified coordinate-disjoint isomorphic families without a new
  threshold.
- **(b) same class only after changing the cut** — 6 classes at the derived
  cut, but 3 classes if the cut is raised until the cross-family distances fall
  under it. Report the smallest such cut, whether it lies outside the derived
  gap, and how many unrelated observations also merge at that cut. This is
  **cut shopping** and is a fail.
- **(c) separate classes, prediction transfers** — 6 classes at the derived
  cut, and P2 reports 3/3 transfers. This is **not a pass**: the system kept two
  classes and the reader's permutation made the tables line up. It is the
  expected result under v0.1.
- **(d) separate classes, prediction does not transfer** — 6 classes and fewer
  than 3/3 transfers. A stronger negative than (c): the tables are not even
  isomorphic under the planted correspondence.

## Pass / fail

E3 **passes only if (a) holds**, with S1, S2, and P1 reported alongside. Any of
(b), (c), or (d) is a **FAIL**, and the failure is classified. The expected
result is (c) or (b). That is a result about the mechanism, not a bug: v0.1 has
no operator over delta shape, only over state proximity, and E3 is the test that
makes that explicit.

Rules:

- A cut that has to be moved outside the derived gap to produce (a) is (b), not
  (a), even if the resulting class count is 3.
- A transfer count of 3 does not turn (c) into (a). The class count at the
  derived cut is the pass condition.
- If the derived gap itself is `None` (the feed does not separate), E3 is
  **inconclusive-fail**: the feed failed to author the separation it claimed.

## What E3 does not establish

- It does not test a relational schema in general. It tests the one relational
  structure v0.1 could plausibly have: proximity-based grouping. A negative says
  that grouping cannot unify coordinate-disjoint isomorphic families. It does
  not say no possible mechanism could.
- It does not remove the author. Both families and the permutation are
  authored.
- It does not test scale. That is E4.

## Open decision (Brad's ruling required)

2. **Redefinition.** Recommended: accept that the original E3 is a no-op under
   P1, adopt the coordinate-disjoint version above, and record its expected
   negative as a finding about the missing operator. If Brad prefers, E3 can be
   dropped rather than run in a form whose pass condition is known to be
   unreachable; it should not be run in its original vacuous form.

## Run protocol

```
python harness/e3.py            # writes e3-out.txt, appends nothing else
```

`e3.py` re-checks the `FREEZE.md` hashes, measures S0, builds the feed, runs both
readings, classifies the outcome (a/b/c/d), and prints every probe and transfer.
A failing rung gets a `status: fail` build record.
