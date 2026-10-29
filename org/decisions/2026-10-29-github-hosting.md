---
id: decision-006
date: 2026-10-29
status: active
---

# GitHub hosting — two repos, public, qwen as the carrier (CEO ruling)

Brad, 2026-10-29. Decide: `swarm/` was untracked at HQ with no provenance;
the org had local git only (no remote, no GitHub CLI).

1. **GitHub is the direction.** The org moves from local-only git to GitHub
   so history survives the box and cloud agents can read it.
2. **Two repositories, not one.** `swarm/` is already its own repo
   (`F:\Lab\swarm\swarm`, branch `main`, own history authored by Brad). Its
   history stays independent. HQ (`F:\Lab`) is the other repo and **ignores
   `swarm/`** rather than absorbing it — no submodule, no nested repo in the
   HQ tree (decision-005: least frictionless).
3. **Public visibility.** Brad's call. Consequence accepted: HQ protocol,
   board, event log, and swarm's source and commit history become world
   readable — including the author emails already recorded in history.
4. **Qwen is the carrier.** `gh` CLI installed on the box at Brad's approval;
   Brad authenticates once via the device flow; qwen creates the repos, lands
   commits, and pushes. Machine-readable provenance of every push goes in the
   event log as "landed by qwen".
