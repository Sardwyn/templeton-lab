---
id: project-emergent-harness
kind: project
key: emergent-harness
updated: 2026-11-09T01:28
supersedes: []
confidence: high
---

Harness v0.1 in F:\Lab\harness - a system given only state, difference, sequence and one error magnitude in [0,1]. v0.1 closed 2026-11-09: 10 scenarios x 2 readings, 0 failing claims; the cut is derived from the nearest-neighbour gap (ratio >= 2.0), swept across each gap and outside it with 0 verdicts moved and 0 classes added; audit clean (no forbidden words, no retained derived structure, live instance holds only memory/episode/tau). Control: 36 random states -> 0 classes, 18/18 declined, chance NN ratio 1.987 vs GAP 2.0. Six readings reproduce: prediction (3 classes, 9/9 anticipations joined), identity (never-delivered state named, beyond-cut state refused), continuity (3/3 boundaries declined separate, 0/3 joined), causality (hub class 1, arrive 0.4006 vs depart 0.1027), agency (fork class 1, entropy 1.585 vs 0 at parents, rivals 0.20/0.50/0.80), self (null space [1,2] frame and [1] drift), witness (rivals kept at equal support, cheaper one picked). Honest limits: metric prior is irreducible, self is cut-relative, causality is reliability not direction, the cut estimator is small-n fragile. E1 order test FAILED its own C2 (rotation identity) - partition is order-invariant, but the degree graph is not, because a finite stream has a first and last state that each lose one edge; proven identical as a cycle. Open: card-021 ladder - E1b restatement, E4 cut scaling (the decisive one), E2 composition, E3 substitution, E5 blind feed from Brad.
