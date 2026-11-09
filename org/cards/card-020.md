---
id: card-020
title: Harness v0.1 - four primitives, six emergent claims, falsifiable suite
column: done
assignee: qwen
project: emergent-harness
depends_on: []
created_at: 2026-11-09T01:28
updated_at: 2026-11-09T01:28
---

**Done.** Built and recorded `F:\Lab\harness\` -- a system given only state,
difference, sequence, and one error magnitude, asked whether prediction,
identity, continuity, causality, agency, and self appear without being seeded.

**Result on the record:**

- `python harness/run.py` -> **0 failing claim(s)** over 10 scenarios x 2
  readings. `python harness/run.py --sweep` -> 0 failing, **0 verdicts
  moved** inside any gap, outside cuts ignored. `python harness/audit.py` ->
  **AUDIT CLEAN**.
- Control (36 random states): gap None, 0 classes, 18/18 positions declined,
  accuracy 0.000. The chance nearest-neighbour ratio is 1.987 against GAP 2.0
  -- stated as the thin margin it is.
- Structural numbers: prediction 3 classes, accuracy 1.000 on answered
  positions; identity names a never-delivered state (3 distinct names) and
  refuses one beyond the cut; causality hub class 1 (in 9, out 2, `in_src` 3,
  arrive 0.4006 vs depart 0.1027); agency fork class 1 (in 9, out 3, successor
  entropy 1.585 vs 0 at parents, rivals 0.20/0.50/0.80); self = null space of
  the difference operator ([1,2] frame, [1] drift); witness keeps both rivals
  at equal support and picks the cheaper one when support ties.
- Two probe defects found by the sweep and fixed **before** the final record:
  the identity "unnamed" probe sat at 0.400 against a gap high side of 0.4016
  (a coin toss, not a claim) and was moved beyond the observed span; a P5
  string concatenation was missing a space.

**Honest limits recorded, not hidden:** priors cannot be removed (claim is
prior-minimality + cut-insensitivity); the metric prior "near exists" is
irreducible; "self" is only a cut-relative null space; causality is
reliability, not direction; the cut estimator is small-n fragile; every feed
was authored by the same agent as the claims.

**Follow-up filed:** card-021 (E1b/E2/E3/E4/E5 ladder). E1 was run under this
card against a frozen core hash -- see `harness/e1-prereg.md` and
`harness/e1-out.txt`: partition and refusal invariant, degree graph not
rotation-invariant because a finite stream has two ends (proven: identical as
a cycle, different as a sequence).

**Artifacts:** `harness/README.md`, `harness/RESULTS.md`,
`harness/e1-prereg.md`, `harness/e1-out.txt`, `harness/out.txt`,
`harness/sweep.txt`, `trials/evidence/harness-v01/evidence.json`.
