---
id: card-014
title: GitHub hosting — remotes for HQ and swarm, push both
column: in-progress
assignee: qwen
depends_on: ["card-004", "card-012"]
created_at: 2026-10-29T02:45
updated_at: 2026-10-29T02:45
---

Per decision-006: take the org from local-only git to GitHub.

1. `gh` CLI installed (Brad approved the install).
2. swarm's WIP committed in its own repo (typecheck clean; vitest running).
3. HQ `.gitignore` excludes `swarm/` — it is an independent repo, not a
   nested tree.
4. Create both public repos, add remotes, push HQ (`master`) and swarm (`main`).
5. Record both remote URLs in the org record + event log, then a memory cell.
