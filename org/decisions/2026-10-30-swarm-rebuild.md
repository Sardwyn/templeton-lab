---
id: decision-008
date: 2026-10-30
status: active
title: swarm-playpen gets rebuilt, not repaired
decided_by: brad
---

# Decision-008: swarm-playpen gets rebuilt, not repaired

**Ruled by Brad on 2026-10-30**, when asked how to handle card-016: "We going to
rebuild that entire project so don't worry about it for now."

## The ruling

1. **The current swarm-playpen WIP is not worth fixing.** The 3 red
   yacht-director contract tests at `22cc654` (build-20261029-001) stay as they
   are; no bisection, no repair.
2. **card-016 is parked, not worked.** It stays on the board as the record of the
   finding, unassigned, until the rebuild either absorbs it or Brad closes it.
3. **swarm-playpen's project status becomes `parked`** — nothing new gets built on
   top of this WIP. The repo stays public with `22cc654` on `main` as history.

## Why

Fixing a regression inside an architecture Brad intends to replace spends VRAM and
time to polish a thing that is about to be thrown away. The honest record is that
the WIP is red and that it is deliberately left red.

## Consequence

- The swarm project page keeps showing the red streak at `22cc654`; that is the
  truth of where the WIP stands, not an open to-do.
- Nothing in HQ depends on swarm-playpen's tests, so the org stays green.
