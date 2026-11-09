# E5-D pre-registration — is the cut a property of the observations, or of the sample?

**FROZEN 2026-11-09, at Brad's direction, before the diagnostic was run.** This
is a diagnostic experiment, not a capability rung: it explains the E5 failure
and repairs nothing. The feed `harness/feeds/brad_e5.json`
(sha256 `88716892b5b5f0b5a2a414f2bca6eaa5b27d852640ac25eaf039c5a834e81bdc`) and
the frozen implementation (`FREEZE.md` hashes) are used unchanged. No claim in
E5 is re-run, re-scored, or repaired; if anything is to change, it is a new
version under the FREEZE amendment protocol.

## The question (Brad's, verbatim)

> Is the global cut supposed to be a stable property of the observations, or is
> it merely a temporary property of the current sample?

## The protocol (Brad's six points, frozen)

1. Replay the E5 feed one observation at a time.
2. Record the gap ratio and derived cut at every prefix.
3. Record exactly when the cut first becomes admissible.
4. Record when it becomes inadmissible.
5. Identify which observations change the nearest-neighbour distribution
   sufficiently to destroy the gap.
6. Repeat the analysis without changing the original implementation or feed.

## Method (fixed before the run)

- Prefixes `p = 1..30` in feed order (episodes as authored, states in order).
  A **fresh `Harness` per prefix** — nothing is retained across prefixes, which
  is exactly the system's own rule that everything is recomputed per call.
- `gap`, `tau`, and class count come from the frozen `Harness` methods only.
  The reader may additionally measure, outside the harness: the full sorted
  nearest-neighbour distance list, per-observation nearest-neighbour distances
  (from `Harness._nearest`), and the largest consecutive ratio **whether or not
  it reaches GAP** — so the trajectory shows how far the distribution was from
  admissibility at every prefix, not just in/out.
- An **event** is any prefix where admissibility (gap exists or not) differs
  from the previous prefix. Each event records: the observation that caused it
  (episode, position, state, error), that observation's own nearest-neighbour
  distance, **every earlier observation whose nearest-neighbour distance
  changed** (old -> new; a new observation can only shrink an existing nearest
  distance), and where the previous window's `lo`/`hi` moved in the new sorted
  list — which new distances were inserted at or below it.
- The largest-ratio window is reported at every prefix with its position in the
  sorted list, so "destroyed" is visible as a window that closed or moved, not
  as a bare None.

## Consistency checks (the diagnostic is invalid if any fails)

- **C1** the feed's sha256 equals `88716892b5b5f0b5a2a414f2bca6eaa5b27d852640ac25eaf039c5a834e81bdc`;
  every `FREEZE.md` hash matches.
- **C2** at `p = 24` (the E5 holdout point) the replayed harness reproduces the
  E5 probe-time facts: `classify` of the probe's last state returns class `1`,
  and `expect` on the probe prefix returns support `1`.
- **C3** at `p = 30` the replay reproduces the E5 completed-feed facts: gap is
  `None` and there are 0 classes.
- **C4** the gap and cut are identical under a joined-reading replay (one
  episode) at **every** prefix. `_nearest` walks observations in memory order,
  so episode boundaries must not move the cut; if they do, that is itself a
  finding and the diagnostic reports it as a failure of C4.

## Output and exit

`e5d.py` writes `e5d-out.txt` (human) and `e5d.json` (per-prefix table, events,
consistency checks). Exit `0` when the trajectory completed and C1-C4 all hold;
`1` when a consistency check fails (published in full); `2` on abort (hash or
feed mismatch). A completed diagnostic is not a pass or fail of any capability
claim; its findings are recorded as diagnosis, post-hoc by nature, under the
FREEZE failed-claim rule.
