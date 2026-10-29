# GitHub remotes (recorded 2026-10-29, per decision-006)

Two independent public repositories. Neither is a submodule of the other;
`swarm/` is gitignored by HQ.

| repo | local path | branch | remote |
|------|------------|--------|--------|
| templeton-lab (HQ) | `F:\Lab` | `main` | https://github.com/Sardwyn/templeton-lab.git |
| swarm-playpen | `F:\Lab\swarm\swarm` | `main` | https://github.com/Sardwyn/swarm-playpen.git |

**Carrier:** qwen creates, commits, and pushes; every push is logged in
`org/events/*.jsonl` with `repo`, `branch`, and `note: landed by qwen`.

**Auth:** `gh` CLI v2.103.3 (installed at Brad's approval). `gh` reuses the
OAuth token Git Credential Manager already held for `Sardwyn@github.com`, so
no device flow and nothing pasted. HQ's branch was renamed `master` → `main`
(branch rename only — no history rewrite).

**Public means public:** HQ protocol, board, event log, memory cells, and
swarm's source and commit history (including author emails already recorded in
git history) are world-readable. Brad's call, decision-006 §3.
