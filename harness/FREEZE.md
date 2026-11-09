# Mechanism freeze — Harness v0.1

**Frozen 2026-11-09, before E1b–E5 were written.** This file is the contract for
the falsification ladder. A rung may not change anything listed here. If a rung
needs a change, the need is the result; the change becomes a new version and a
new experiment.

## Version

```
Harness v0.1
frozen 2026-11-09
```

## Frozen implementation

Every rung re-checks these hashes at the top of its run and aborts if any
differs. `e1.py` is included because E1's recorded result must stay
reproducible; E1b imports it and may not edit it.

| file | sha256 | bytes |
|---|---|---|
| `core.py` | `8734d335a14810424296629c8500a5edda5b09b364c7f9387a42aee87aa0f150` | 15857 |
| `measure.py` | `1c9f076dcaafb274947cf61e6ac88cc7e86425ffb4d79b72983fb6798967c06f` | 6568 |
| `run.py` | `5440c370ff6c5ac764d8a02ae1bf71ab794f2b82b3a234a07abc01deccfc2b42` | 21382 |
| `scenarios.py` | `bc8e40d22b65b1397914c1a8ad553a2184d775d90b8966b2e33a0de87342ef22` | 22888 |
| `audit.py` | `e1cd2ee14e996ae122f8ad1633b27e1cbf0bae72f686fdc3560b40eba483e6be` | 5489 |
| `e1.py` | `720f90ac910c48240494409174af6cb22c1bda75f1552f0c2bf3576ff4719a8f` | 7975 |

## Fixed parameters

```
K          = 3          context length ceiling (P2)
GAP        = 2.0        minimum nearest-neighbour separation ratio (P4)
MIN_SIDE   = 2          observations required on each side of a cut (P5)
EPS        = 1e-12      distance floor
ACCURACY   = 0.80       reader-side anticipation threshold (run.py)
FAN        = 3          reader-side hub/fork arity (run.py)
READINGS   = separate, joined   both reported; neither is "the" reading
```

`ACCURACY` and `FAN` are reader-side. They are frozen here so a later rung
cannot quietly move the bar. New rungs may declare their own reader-side
thresholds only if the threshold is written into that rung's pre-registration
before its run.

## Priors P0–P6, verbatim from `core.py`

- **P0** the stream arrives as bounded sequences; an episode boundary is given
- **P1** magnitude of a difference = mean absolute deviation over components.
  Consequence: a component that never differs contributes 0, so its size is
  scale, not information — a constant carries no news
- **P2** context = the last 1..K ordered positions, K = 3
- **P3** competing continuations rank by support, then by lower error
- **P4** the cut between "this has happened before" and "this is something else"
  is the largest relative gap in the nearest-neighbour distance distribution,
  ratio ≥ `GAP`. The cut is valid anywhere inside the gap; the system picks the
  arithmetic midpoint, and `run.py` sweeps the whole interval to show the
  verdict does not depend on where
- **P5** a separation needs `MIN_SIDE` observations on both sides, and a width
  of two — the cheapest cut that still refuses an unstructured feed — is the
  floor
- **P6** recurrence is single-linkage grouping in observation order: an
  observation joins the recurrence of the earlier observation nearest to it,
  when that distance is under the cut. Nothing is averaged

## The architectural assumption, stated as such

**P0 is not derived. It is given.** Every reading depends on where an episode
ends: the `separate` reading declines the first position of every episode, the
`joined` reading manufactures a return edge at every splice, and the degree
readings inherit the stream's two ends. P0 is therefore flagged as the largest
unearned prior in v0.1. No rung in this ladder may use P0 as evidence for
anything; a rung that needs the boundary must say so and report both readings.

## Reporting rule: structure and prediction are separate results

Every rung reports these independently. Neither substitutes for the other.

**STRUCTURE** — gap ratio and cut; the number and sizes of recurrences; the
partition of observations into recurrences; per-class degree and successor
sets; invariants; per-class error means and spreads. A structural result is
about what the feed's geometry supports.

**PREDICTION** — positions asked, positions answered, positions declined;
hits; accuracy on answered positions; support and confidence; the full rival
list. A predictive result is about what the transition table supports.

A feed may produce clean structure and poor prediction: that is a result. A
feed may produce good prediction from a table that is only repeating the
feed's own sequence: that is also a result, and the E2 baseline exists to
separate the two.

## Failed-claim rule

1. A rung's claims are frozen **before** its feed is run.
2. A failed claim is reported as a failure in the rung output and in the build
   record. It is not repaired by editing the claim afterwards.
3. A diagnosis may be added *after* the run, in a dated section, clearly
   labelled post-hoc. A diagnosis is not a pass.
4. A fix is a new experiment: new pre-registration, new feed, new output. If
   the fix touches the mechanism, it is a new version, and every later rung is
   re-run against the new hash.
5. No tuning after seeing a rung's output. This includes `GAP`, `MIN_SIDE`,
   `K`, the reader thresholds, and the feed generator.

## What may change, and what may not

**May change / may be added:** new reader-side files (`e1b.py`, `e2.py`,
`e3.py`, `e4.py`, `e5.py`), new feed builders, new measurement functions that
do not enter `core.py`, and new rung-specific claim vocabularies declared in
advance. A new file may import the frozen modules.

**May not change:** `core.py`, `measure.py`, `run.py`, `scenarios.py`,
`audit.py`, `e1.py`, or any frozen parameter. A rung that edits any of these
has invalidated itself; the edit is reverted and the rung is recorded as
aborted.

## Evidence commitments

- Each rung writes its own `*-prereg.md` before its `*-out.txt`.
- Each rung's output is kept verbatim, including failures, n/a rows, declines,
  and unexpected values.
- The build record in `org/builds/` names the command, exit code, and the
  output file. A failing rung gets a `status: fail` build, not a silent retry.
- The project page records one line per rung and keeps the ladder's order.

## Ladder

```
E1b  close E1's C2 definition (post-hoc restatement, not a new blind test)
E2   fixed-lag interleaving, with the same-information baseline
E3   coordinate-disjoint families and the three outcomes
E4   cut scaling and chance-ratio distribution (cross-cutting validity test)
E5   blind feed, independently authored (the only rung that removes the author)
```

E4 is cross-cutting: it is run in its numbered position, but its result is
applied to how E2 and E3 are read. A failure in E4 does not retroactively pass
or fail E2/E3; it changes what their passes are worth.
