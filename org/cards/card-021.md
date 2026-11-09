---
id: card-021
title: Harness ladder - order invariance, cut scaling, composition, substitution, blind feed
column: backlog
assignee: unassigned
project: emergent-harness
depends_on: [card-020]
created_at: 2026-11-09T01:28
updated_at: 2026-11-09T01:28
---

Rungs after v0.1, each pre-registered before its run and each allowed to fail.
One rung per sitting; do not batch.

**E1b (next, cheap).** Restate the rotation claim for the circular reading
(edges plus return edge) and exclude the first/last positions where the degree
claims are stated. E1 already proved the mechanism: the partition is
order-invariant, the directed-edge multiset is identical only as a cycle, and
the difference is exactly one missing inbound at the stream's start and one
missing outbound at its end. Deliverable: a two-line amendment in
`harness/e1-prereg.md` (new dated section) plus the matching check in
`harness/e1.py`.

**E4 (highest information).** Does the cut estimator survive scale? n from 18
to 500, dimensions 4 to 16, measure the chance nearest-neighbour ratio
distribution and whether the derived gap still lands inside an authored
separation. The whole method's operating range today is the thin strip
between the control's 1.987 and the weakest real separation at 2.46. A fail
here falsifies the method, not a scenario, and should be reported as the
headline. **Do this before E2/E3** -- if the cut does not scale, composition
results are small-n artifacts.

**E2.** Composition without symbols: A/B interleaved at a fixed lag, so the
next state is not in the literal prefix. Pass = beats the longest-match
fallback with no composite label added. Fail = prediction needs a chunk, i.e.
composition was smuggled in.

**E3.** Substitution: two families with the same delta shape, components
permuted. Pass = one class at one cut covers both and prediction transfers
without extra memory. Fail = a schema was required.

**E5.** Blind feed from Brad: he writes states, errors, episode boundaries,
and the claims he expects, without describing the generator. Run against
`core.py` unmodified and log whatever happens. The only rung that removes the
author.

**Discipline:** `core.py` may not change to make a rung pass; if a rung needs
a change, the need is the result. Every rung writes its own prereg, then its
output file, then one line in the project page.
