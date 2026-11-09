---
id: emergent-harness
title: Emergent Harness (research)
status: active
owner: brad
repo:
path: F:\Lab\harness
memory_cell: project-emergent-harness
updated_at: 2026-11-09T01:28
---

**What it is:** a minimal system fed only state (numbers), difference,
sequence (ordering), and one error magnitude in [0,1]. No objects, labels,
entities, graph, time axis, self, or cause. The question: what has to be added
before prediction, identity, continuity, causality, agency, and self appear --
and does the system stop short of building a world model?

**Why it matters to the org:** it is the only project here that tests the
org's own claim-making machinery. If a system with no priors recovers only what
its author planted, that is a warning about every "we found a pattern" claim
the org makes.

**Where we're at (2026-11-09, v0.1 closed):**

- System: `F:\Lab\harness\core.py` (~350 lines, stdlib), six priors P0-P6
  listed in code, no per-scenario knob, no retained derived structure
  (audit-checked).
- Claim suite: 10 scenarios x 2 readings = 20 runs, **0 failing claims**;
  `python harness/run.py`. Control feed (36 random states) yields 0 classes
  and declines 18/18 positions.
- Cut: derived from the nearest-neighbour gap (ratio >= 2.0), swept across
  each gap at 15/50/85% and once outside it -- **0 verdicts moved**, an
  outside cut changes nothing, an imposed cut on the control produces 0
  classes.
- Audit: **AUDIT CLEAN** -- no forbidden vocabulary in executable code or
  identifiers, live instance holds only `[episode, memory, tau]`, memory entry
  is `(tuple, float)`.
- Evidence: `F:\Lab\trials\evidence\harness-v01\evidence.json`; write-up
  `F:\Lab\harness\README.md` + `F:\Lab\harness\RESULTS.md`.
- **E1 (order test, pre-registered): FAIL by its own rule.** Partition
  invariance PASS (3 classes, [9,9,9] in cycle / rotate / grouped), refusal
  PASS (3 declined, 6 answered in every order), prediction sensitivity PASS
  but weak (9/9 -> 8/9, miss at the seam), rotation identity of the degree
  graph FAIL. Cause proven: edges are identical as a cycle and differ only as
  a finite sequence -- the stream's first and last state each lose one edge.
  Not position memory; a two-ended-stream artifact that any degree-based
  reading (causality hub, agency fork) inherits.

**Next (the ladder, in order):**

1. E1b: restate rotation invariance for the circular reading, and exclude
   first/last positions explicitly in the degree claims. Cheap, closes E1.
2. E4: scale the cut estimator (n 18->500, dims 4->16). The control's chance
   ratio is 1.987 against GAP 2.0 and the weakest real separation is 2.46 --
   that margin is the method's whole operating range. **This can falsify the
   method, not just a scenario.**
3. E2: composition (A/B interleaved at a fixed lag) -- does the next state
   need a chunk/symbol?
4. E3: substitution (same shape, permuted components) -- does reuse need a
   schema?
5. E5: a blind feed from Brad -- the only rung that removes the author.

**Standing caveat:** every v0.1 feed and claim was written by the same agent.
A pass means "authored structure is recoverable", not "no world model". E1 was
the first partial escape; E5 is the real one.

**Files:** `harness/README.md`, `harness/RESULTS.md`, `harness/e1-prereg.md`,
`harness/e1-out.txt`, `harness/out.txt`, `harness/sweep.txt`.
