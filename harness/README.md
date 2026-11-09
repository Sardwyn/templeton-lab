# Harness v0.1

A system built from four things and nothing else:

| primitive | what it is |
|---|---|
| **state** | a tuple of numbers |
| **difference** | componentwise `abs(a - b)` |
| **sequence** | ordering — this observation came after that one |
| **constraint signal** | one number in `[0, 1]`: how undesirable this state was. Nothing about *why* |

The system is not told that anything exists, that anything repeats, that two
states are the same, that one change follows from another, or that there is a
self doing the observing. It is not given objects, labels, entities, a world, a
graph, a symbol table, a time axis beyond ordering, or a notion of truth.

**The question it exists to ask:** if you are fed only state, difference,
sequence, and an error magnitude, what has to be *added* before prediction,
identity, continuity, causality, agency, and self appear — and does it stop
short of building a world model?

v0.1 answers the first half. It has not yet answered the second — see
"what this does not show" below.

## What is stored

Memory holds observed episodes, each a list of `(state tuple, err float)`, and
nothing else. Every structure — nearest neighbours, the gap, the cut,
recurrences, the transition table, competitor sets, the invariant set — is
recomputed from memory on every call. `audit.py` asserts it: a live instance
holds exactly `['episode', 'memory', 'tau']`.

## The rules (PRIORS)

A prior here is a **way of measuring**, not a conclusion. The list is complete;
anything not on it is not in the system.

- **P0** the stream arrives as bounded sequences; an episode boundary is given.
- **P1** magnitude of a difference = mean absolute deviation over components.
  Consequence: a component that never differs contributes 0, so its size is
  scale, not information — a constant carries no news.
- **P2** context = the last 1..K ordered positions, K = 3.
- **P3** competing continuations rank by support, then by lower error.
- **P4** the cut between "this has happened before" and "this is something else"
  is the largest relative gap in the nearest-neighbour distance distribution,
  ratio ≥ `GAP = 2.0`. The cut is valid anywhere inside the gap; the system
  picks the midpoint and `run.py --sweep` moves it across the whole interval to
  show verdicts do not depend on where it sits.
- **P5** a separation needs `MIN_SIDE = 2` observations on each side. A width of
  two is the floor: the control feed (36 states, 6 episodes) throws a largest
  chance nearest-neighbour ratio of 1.99, so a narrower rule would compress
  noise. The margin is 0.7 %, which is why the cut is swept rather than trusted.
- **P6** recurrence is single-linkage grouping in observation order: an
  observation joins the recurrence of the earlier observation nearest to it when
  that distance is under the cut. Nothing is averaged — a class is made of
  observations that exist, not of a centre no observation occupies.

P1 and P4 are the load-bearing ones. P1 makes a constant a scale. P4 makes "same"
a *derived* quantity, with a validity interval rather than a number.

## What each word reduces to

| word | operational reading in this build |
|---|---|
| prediction | `expect(prefix)` — the longest observed context's most-supported continuation, with its rivals |
| identity | `classify(state)` — the distance-under-a-cut test that built the classes, applied to a state never stored |
| continuity | an episode boundary the harness declines to predict across when nothing was ever observed to cross it |
| causality | a recurrence many arrive at, in one way, from several places (`hub_of`) + arriving is cheaper than departing |
| agency | a recurrence that continues in at least `FAN` distinguishable ways, more than its parents and children do (`fan_of`) |
| self | the null space of the difference operator — the components the cut cannot resolve (`invariant`) |
| witness | rivals are retained and ranked, not collapsed to a winner (`competitors`) |

None of these words appears in `core.py`'s executable code; `audit.py` checks
that too. They are readings applied from outside, in `run.py`.

## Files

```
core.py       the system under experiment (~350 lines, stdlib only)
measure.py    feeding, shape measurement, anticipation, rival extraction
scenarios.py  ten feeds + the criteria fixed before any run
run.py        driver, reader-side thresholds, claim judge, sweep
audit.py      forbidden-vocabulary, no-retained-structure, no-knob checks
FREEZE.md     the frozen mechanism: hashes, parameters, P0-P6, reporting rules
e1.py         the first follow-up: order test, against a frozen core hash
e1b.py        the restatement of E1's rotation claims (post-hoc, frozen)
e2-prereg.md  fixed-lag interleaving + same-information baseline (pending)
e3-prereg.md  coordinate-disjoint families + the four outcomes (pending)
e4-prereg.md  cut scaling and chance-ratio distribution (pending)
e5-prereg.md  blind-feed protocol and claim vocabulary (frozen, feed pending)
out.txt       full run output (20 scenario x reading runs)
sweep.txt     the same, plus the cut-moved report
RESULTS.md    what the run measured, three findings, the E1 outcome
e1-prereg.md  the claim set frozen before E1, plus Amendment E1b
e1-out.txt    E1 output (FAIL on C2 -- see RESULTS.md)
e1b-out.txt   E1b output (PASS; E1 itself stays FAIL)
```

## Run

```
python harness/run.py          # all scenarios, both readings, writes evidence.json
python harness/run.py --sweep  # + move the cut across each gap, and outside it
python harness/audit.py        # prior-leak checks on core.py
python harness/e1b.py          # restatement of E1's rotation claims
```

## The falsification ladder

v0.1 is closed and frozen (`FREEZE.md`). The ladder attacks a different source
of false confidence at each rung; each rung is pre-registered and each is
allowed to fail.

| rung | question | status |
|---|---|---|
| E1b | Is rotation invariance true for the graph a finite stream supports? | **PASS** — cyclic edges and presence degrees invariant; two seam violations; only the seam position misses |
| E2 | Can recurrence predict through fixed-lag interleaving beyond a same-information raw-prefix NN? | pre-registered, pending baseline ruling |
| E3 | Does relational structure survive a coordinate transformation? | redefined (original is a no-op under P1), pending ruling |
| E4 | Does the cut survive n=500 and dim=16, or is 1.987-vs-2.0 a small-n accident? | pre-registered, pending acceptance-band ruling; cross-cutting |
| E5 | Can the result survive a feed authored by Brad? | protocol frozen, feed pending |

A pass on E1b does not make E1 a pass. E1's original claim set stays FAIL on
the record; E1b closes the definition, and the two-ended-stream artifact is now
a named architectural limit of every degree-based reading.

## What this does not show

1. **Freedom from priors is impossible.** A metric ("near exists"), an
   aggregation (mean absolute deviation), and a cut are all still there. The
   honest claim is prior-*minimality*, plus the cut's insensitivity: the same
   verdicts hold anywhere inside each gap, and a cut imposed outside is ignored.
2. **It has not been shown to avoid a world model.** Every feed was authored by
   the same person who wrote the claims, so success means "authored structure is
   recoverable", not "this works in a world it was not shaped by". E1
   (`e1-prereg.md`) was the first test aimed at that: the recurrence partition
   survived reordering, prediction moved only at a broken seam, and the degree
   graph failed invariance because a finite stream has two ends. E5 (a blind
   feed from Brad) remains the only rung that removes the author.
3. **Causality here is reliability, not direction.** A hub is a place things
   converge on cheaply. Nothing in the code defines a cause, and magnitude
   cannot carry direction across an oscillation.
4. **"Self" is only a cut-relative null space.** It is whichever components the
   cut cannot resolve — not a thing that observes.
5. **The cut estimator is small-n fragile.** GAP was moved from 1.5 to 2.0
   because 18 unstructured points produce a chance ratio of 1.99; `self_drift`
   binds at a gap of 2.46, so a stricter GAP would erase a real separation.
   That is a property of the method, not of the feed.

**A cut is cheap. What it carries is not.**
