---
id: fact-github-hosting
kind: fact
key: github-remotes-and-carrier
updated: 2026-10-29T03:30
confidence: high
---

**GitHub fact (2026-10-29, executing decision-006):** the org is hosted on
GitHub under Brad's account `Sardwyn`, both repos **public**:

- HQ `F:\Lab` → https://github.com/Sardwyn/templeton-lab (branch `main`,
  renamed from `master` — branch rename only, no history rewrite).
- `F:\Lab\swarm\swarm` → https://github.com/Sardwyn/swarm-playpen (branch
  `main`, its own independent history; HQ gitignores `swarm/`).

Mechanics worth remembering:
- `gh` CLI v2.103.3 works **without a fresh login**: `gh auth login
  --with-token` fed the OAuth token Git Credential Manager already held for
  `git:https://Sardwyn@github.com` (scopes include `repo`). The device flow
  expired on its own before Brad could use it — use the stored credential.
- Qwen is the carrier: repo creation, commits, and pushes are qwen's, logged
  as `repo_create` / `push` events with `note: landed by qwen`.
- HQ history uses the org identity `"Qwen" <qwen@templeton.local>`; swarm's
  history is Brad's own (`Bradley Templeton <sardwyn@hotmail.com>`), and both
  repos are public.

Details: org/notes/github-remotes.md.
