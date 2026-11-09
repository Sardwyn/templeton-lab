# E2 pre-registration — fixed-lag interleaving, against a same-information baseline

**PROVISIONAL. Not frozen until Brad rules on the baseline choice in §Open
decision.** No E2 feed has been run. The mechanism is frozen by `FREEZE.md`.

## Question

v0.1's prediction accuracy could have come from two different places:

1. the recurrence classes carry enough structure that a class context predicts
   the next class even when the literal raw-state sequence has never been seen;
2. the feed's raw sequence is regular enough that a nearest-neighbour lookup on
   raw prefixes does the same job, and the classes are cosmetic.

E2 breaks the easy relationship between the literal recent prefix and the next
state by interleaving two families at a fixed lag. Then it asks whether the
harness beats a baseline that has **the same training feed, the same context
length, the same cut, and the same memory**, but does **not** compress to
recurrences first.

A pass is evidence that recurrence is doing work. A tie is evidence that it is
not. A fail is not repaired by weakening the baseline.

## Feed

Six authored regions in 4D: family A = `A0, A1, A2`, family B = `B0, B1, B2`.
Each family is a 3-cycle. The stream interleaves them at a fixed lag of two
positions:

```
A0 B0 A1 B1 A2 B2 | A0 B0 A1 B1 A2 B2 | ...   (8 cycles, 48 observations)
```

Every same-family successor is separated from its predecessor by one state of
the other family. The raw prefix at a tested position therefore never contains
the next state, and the next state is not the immediate successor of the
previous state within its own family.

Coordinates (before jitter):

```
A0 = (0.00, 0.00, 0, 0)      B0 = (0.00, 0.00, 0.60, 0)
A1 = (0.50, 0.00, 0, 0)      B1 = (0.50, 0.00, 0.60, 0)
A2 = (0.25, 0.45, 0, 0)      B2 = (0.25, 0.45, 0.60, 0)
```

Jitter uses the existing `scenarios.jit`/`jittered` helpers with a per-visit
seed, amplitude `0.008`, on components 0 and 3, exactly as v0.1. The error
values are fixed per region: `A0..A2 = 0.10, 0.30, 0.50`;
`B0..B2 = 0.20, 0.40, 0.60`. Errors are attached to states; nothing in the feed
names a family, a cycle, or a lag.

Eight episodes, each one 6-state cycle, `holdout_from = 4`. Both readings are
reported. The **joined** reading is the primary one for E2, because separating
episodes restarts the context at every cycle and weakens the interleaving.

## Structure claims

**S1 — six recurrences, not three or twelve.** At the derived cut the harness
finds exactly 6 classes, each of size 8, with gap ratio ≥ `GAP`. Every class's
members must come from one authored region; a class containing both an A state
and a B state is a cross-family merge and fails S1 even if the count is 6.

**S2 — no composite label.** The class ids are the 6 regions. No class is a
product, tuple, pair, or chunk of two regions; no class id appears at prediction
time that was not built from an observed state. Operationally: `classes() == 6`
and the region-to-class map is a bijection. A 12-class result is also a fail
(two classes per region is not a composite, but it is not the authored
structure and must be reported).

## Prediction claims

Let `H` be the harness's accuracy on answered positions and `B1` the
same-information raw-prefix baseline (below), measured on the same held-out
positions.

**P1 — the harness predicts.** `H ≥ ACCURACY = 0.80` on answered positions in
the joined reading. Declines are reported, not dropped.

**P2 — recurrence beats the same-information baseline.** On positions both
answer, `H ≥ B1 + 0.10` absolute, and the harness answers at least as many
positions as `B1`. This is the load-bearing claim. If `B1` answers fewer than 3
paired positions, P2 is **not applicable**, and E2 is recorded as **FAIL
(inconclusive: the baseline did not engage)** — not as a pass, and not as a
silent omission.

**P3 — the literal-match floor is reported, not used as the pass bar.** `B0`
(exact raw-suffix longest match) is measured and reported with its coverage.
Under jitter it is expected to answer almost nothing. It is a floor, not the
comparator; a system that only beats `B0` has not shown anything.

## The two baselines, exactly

**B1 — raw-prefix nearest neighbour, same information.**
For a probe of the last `k = min(K, len(probe))` raw states, consider every
training position that has at least `k` predecessors in its own episode and a
successor. For each candidate, compute

```
d = (1/k) * sum_{t=0..k-1} _dist(probe[-k+t], training_state[candidate-k+1+t])
```

using the system's own `_dist` (P1), not a new metric. Choose the candidate with
the smallest `d`. If `d < tau` (the same cut the harness derived from the same
training feed), predict the class of that candidate's successor; otherwise
decline. No compression, no class table. This baseline has strictly more raw
information than the harness (the actual coordinates), the same context length,
the same memory, and the same cut. It is the strongest fair comparator.

**B0 — exact raw-suffix longest match.**
Find the longest suffix of the raw probe (length 1..K) that occurs verbatim as a
contiguous subsequence of a training episode and has a successor. Predict the
successor's class. If no suffix matches, decline. This is literal sequence
matching with no tolerance. It is reported for coverage and accuracy.

## Pass / fail

E2 **passes** if S1, S2, P1, and P2 all hold. It **fails** if any of them moves.
Failure modes and what each means:

- S1 fails (classes merge or split): the interleaving is not recoverable at this
  cut; report which regions merged and at what distance.
- P1 fails: the harness cannot predict the interleaved stream even with classes.
- P2 fails or is not applicable: the harness does not beat a raw-prefix lookup
  with the same information. This is the negative result E2 exists to detect:
  recurrence adds nothing beyond nearest-neighbour on raw prefixes at this
  scale.
- P3 low coverage is expected and is not a failure by itself.

## What E2 does not establish

- It does not test composition in the sense of factorising the two families. The
  harness sees a 6-cycle and may simply memorise it. A pass on P2 says the
  *class context* carries predictive structure beyond raw-prefix lookup; it does
  not say the system recovered A and B as separate factors.
- It does not test transfer to a de-interleaved feed or to a changed lag. That
  would be a later experiment (E2b), and would need its own pre-registration.
- It does not remove the author. The feed is still built by the same agent as
  the claims.

## Open decision (Brad's ruling required)

1. **Baseline choice.** Recommended: run both, but make **B1 the primary
   comparator** and B0 the reported floor. B0 alone is a strawman under jitter:
   it will answer almost nothing, so "beats B0" would be uninformative. B1 is
   the only baseline with the same information and opportunity. If Brad rules
   B0 only, P2 must be rewritten before the run and the rung is much weaker.

## Run protocol

```
python harness/e2.py            # writes e2-out.txt, appends nothing else
```

`e2.py` re-checks the `FREEZE.md` hashes, builds the feed deterministically, runs
both readings, and prints the structure rows, the harness rows, B1, B0, the
paired comparison, and the S/P verdicts. The build record names the output file
and the exit code.
