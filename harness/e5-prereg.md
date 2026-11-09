# E5 pre-registration — blind feed, independently authored

**FROZEN protocol. The runner and claim vocabulary below are fixed before any
feed is seen. The feed itself is pending: Brad authors it.** No E5 feed has been
run. The mechanism is frozen by `FREEZE.md`.

## Why E5 exists

Every feed in E1–E4, and every claim about it, was written by the same agent.
A success therefore means "the authored structure is recoverable", not "the
system works in a world it was not shaped by". E5 is the only rung that removes
the feed's author. It cannot remove the claims' author — Brad writes those — but
it removes the circularity that matters most: the person choosing the states is
no longer the person who knows what the mechanism needs.

## Protocol (fixed)

1. **Brad provides the feed.** A single JSON file, with the states, errors,
   episode boundaries, holdout point, probes if any, and the claims he expects
   with their pass/fail conditions. He does not describe the generator.
2. **The implementation and parameters are frozen.** `FREEZE.md` hashes are
   re-checked at the top of the run. `e5.py` is written and hashed before the
   feed is placed.
3. **The feed is run unchanged.** No edit, no reordering, no rescaling, no
   replacement of a malformed value. If it does not parse, that is the result.
4. **All output is published**, including unexpected values, n/a rows, declines,
   and failures. Nothing is filtered, and no claim is dropped.
5. **No tuning after seeing the output.** If something needs changing, it
   becomes a new experiment (E5b) with a new feed hash and a new
   pre-registration. The original feed and output stay on the record.

## Feed format

```json
{
  "name": "e5-brad-001",
  "authored_by": "brad",
  "created": "2026-11-09T00:00",
  "kind": "prediction",
  "holdout_from": 3,
  "readings": ["separate", "joined"],
  "blocks": [
    [[[0.0, 0.0, 0.0, 0.0], 0.10],
     [[0.5, 0.0, 0.0, 0.0], 0.45]]
  ],
  "probes": [
    {"why": "a state never delivered, inside a recurrence",
     "prefix": [[0.5, 0.0, 0.0, 0.0]],
     "expect_state": [[0.0, 0.0, 0.0, 0.0]],
     "named": true}
  ],
  "criteria": {
    "classes": 3,
    "sizes": [9, 9, 9],
    "anticipatory": 0.8
  }
}
```

Rules:

- `blocks` is a list of episodes. Each episode is a list of `[state, error]`.
  Every state must have the same length. Every error must be a number in
  `[0, 1]`.
- `holdout_from` is the index of the first episode held out. The feed is
  written through `holdout_from`, probes are asked, then the held episodes are
  delivered while asking before every position — exactly the v0.1 protocol.
- `readings` is optional; default `["separate", "joined"]`. The names are the
  only two readings the system supports.
- `kind` is reader-side only (`prediction`, `identity`, `continuity`,
  `causality`, `agency`, `self`, `witness`). It tells `centre_of` which
  direction to read. A feed that expects a hub or a fork must set `kind` to
  `causality` or `agency`; otherwise those claims are n/a, not silently passed.
- `probes` is optional. A probe is the same object `run.py` accepts: `why`,
  `prefix` (raw states), `expect_state` (raw states or a list of them),
  `named` (bool).
- `criteria` is the claim set. Values are the expected numbers/booleans. A
  claim with `null` is reported n/a. An unregistered key is a **FAIL**, not a
  skip.

## Claim vocabulary (fixed)

All keys already defined in `run.py` are accepted. The current set is:

```
classes states episodes sizes invariant no_cut
no_convergence no_divergence no_collapse below_claims no_dominance
centre converges diverges arrival_gt_departure fork_successors_open
err_within_class err_within_class_min err_across_classes err_center
err_worse_after err_floor probe_support probe_named probe_distinct
probe_unnamed probe_silent anticipatory boundary_declined equal_support
pick_is_cheaper rivals_min rivals_count closes_joined closes_separate
drift_visible
```

E5 adds four reader-side checks, fixed here before any feed:

| key | need | pass when |
|---|---|---|
| `gap_ratio_min` | number | `gap` exists and `gap["ratio"] >= need` |
| `cut_inside` | `[lo, hi]` | `tau` exists and `lo < tau < hi` |
| `answered_min` | integer | answered positions ≥ need |
| `declined_max` | integer | declined positions ≤ need |

No other key is accepted. `_joined` / `_separate` suffixes work exactly as in
`run.py`: the claim is asked only of that reading.

## Runner

```
python harness/e5.py harness/feeds/<file>.json
```

`e5.py`:

1. Re-checks every hash in `FREEZE.md` and aborts on a mismatch.
2. Computes and prints the feed file's sha256. If `<file>.sha256` exists, it
   must match the file byte-for-byte; a mismatch aborts the run.
3. Validates the feed shape (same state length, error in `[0,1]`,
   `holdout_from` in range, readings known). A validation failure is a failed
   run, printed in full.
4. Runs each requested reading with `run.py`'s `run_one`, evaluates `criteria`
   with `judge` plus the four extra checks, and prints every row with
   `pass` / `FAIL` / `n/a` and its value.
5. Writes `e5-out.txt` (human) and `e5-<name>.json` (machine, including the
   feed hash, every row, and every asked position), then exits `0` only if every
   non-n/a claim passed.

`e5.py` never edits the feed and never writes to it. Its own hash is recorded
in `e5-out.txt` and in the build record, so the runner used is auditable.

## Pass / fail

E5 **passes** if every claim in Brad's `criteria` passes. It **fails** if any
claim fails, if a claim is unregistered, if the feed is malformed, or if the
feed's hash does not match its sidecar.

A failure is a result and is published in full. It is not repaired by editing
the feed or the claim. If Brad wants a second attempt, it is E5b with a new feed
hash; the first attempt stays on the record.

## What E5 does not establish

- It does not remove the author of the claims. Brad chooses what to expect; the
  claims are still a human hypothesis, not a neutral oracle.
- It does not prove the system avoids a world model. It removes one specific
  source of false confidence — the feed author — and it is the only rung that
  can.
- A pass is not a generalisation claim. It is one independently authored feed,
  run once, unchanged.

## Status

- `e5.py` and this vocabulary are frozen now.
- Feed: **pending Brad**. Place it at `F:\Lab\harness\feeds\` and send the path;
  the runner will print and record its hash before running.

## Post-hoc diagnosis (added 2026-11-09, after the run — E5-D)

Per the failed-claim rule, this section was appended after the run; it is a
diagnosis, not a pass. The feed and every E5 number above are unchanged.

The follow-up question was whether the global cut is a stable property of the
observations or a temporary property of the current sample. The diagnostic
`e5d-prereg.md` / `e5d.py` replayed this feed one observation at a time under
the frozen `Harness` (fresh instance per prefix, consistency checks C1–C4 all
pass; `e5d-out.txt`):

- The cut was admissible only at **p = 23..24 of 30** prefixes.
  Stretches: p 1..22 no, p 23..24 yes, p 25..30 no.
- **Gained at p=23:** observation ep7.pos1 `[0.57, 0.47, 0.62, 0.62]` arrived
  with its own nearest-neighbour distance **0.0075** — a near-duplicate of
  ep5.pos2 `[0.58, 0.46, 0.63, 0.62]`. That opened the window 0.0075..0.0200 at
  ratio **2.667** (≥ GAP).
- **Lost at p=25:** the first held observation ep8.pos0
  `[0.16, 0.81, 0.21, 0.27]` arrived with its own nearest-neighbour distance
  **0.0125** — a near-duplicate of ep0.pos0 — landing strictly **inside** the
  old window. The best ratio fell to 1.667 and the gap died.
- At neither event did any earlier observation's nearest-neighbour distance
  change: the arriving observation alone caused each flip.
- The feed's seasonal continuum never approached GAP = 2.0 on its own: the best
  ratio was ≤ 1.5 through p = 22 and 1.6–1.667 after; the admissible prefixes
  compressed 24 observations into 21–22 classes, i.e. the cut grouped only
  near-duplicates.
- Exact repeats (NN = 0.0, present from p = 11) are skipped by the `lo ≤ EPS`
  rule and never open a window.
- The cut was identical under a joined-reading replay at every prefix (C4), so
  this is not an episode-boundary artifact.

**Answer, scoped to this feed:** the global cut was a temporary property of the
sample — created by one near-duplicate and destroyed by another. E5's probe was
asked at p = 24, inside the only admissible window, and named the
near-duplicate class; that class had exactly one observed continuation, which is
why `probe_support` failed (1 < 2). Whether any cut can be stable on a
continuum feed at GAP = 2.0 is a v0.2 question; nothing here was changed to
make it one.
