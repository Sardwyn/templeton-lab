---
id: decision-006
kind: decision
key: github-hosting-two-repos
updated: 2026-10-29T03:10
supersedes: []
confidence: high
---

**Brad's ruling (2026-10-29):** the org moves from local-only git to **GitHub**.
**Two repositories** — HQ (`F:\Lab`) and `swarm/` stay independent: no submodule,
no absorbing swarm's history into HQ; HQ gitignores `swarm/`. Visibility
**public** (Brad's call; author emails already in git history become public).
`gh` CLI installed at Brad's approval. **qwen is the carrier**: creates repos,
lands commits, pushes; every push logged as "landed by qwen". swarm's ~811-line
uncommitted WIP is committed as an honest WIP commit before pushing.
Full: org/decisions/2026-10-29-github-hosting.md.
