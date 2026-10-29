---
id: card-014
title: GitHub hosting — remotes for HQ and swarm, push both
column: done
assignee: qwen
depends_on: ["card-004", "card-012"]
created_at: 2026-10-29T02:45
updated_at: 2026-10-29T03:35
---

Per decision-006: take the org from local-only git to GitHub.

1. `gh` CLI installed (Brad approved the install). Auth reused the OAuth token
   Git Credential Manager already held — no paste, no device flow.
2. swarm's WIP committed in its own repo as `22cc654` under Brad's identity:
   typecheck clean, `vitest run` red on `test/view/yacht-director.test.ts`
   (3 of 11, introduced by the WIP — the same file passes at `29d7179`).
   Recorded honestly as a build, not hidden.
3. HQ `.gitignore` excludes `swarm/` — it is an independent repo, not a
   nested tree.
4. Both public repos created and pushed: Sardwyn/templeton-lab (HQ, branch
   renamed `master` → `main`) and Sardwyn/swarm-playpen (`main`).
5. Remote URLs recorded in org/notes/github-remotes.md, event log, and
   memory/cells/fact-github-hosting.md.

Open finding (not this card's scope): the director WIP breaks its own
contract tests — the director loses the agent inchworm, drifts to 6.5 where
the contract says < 6, and spends 0.4999 against > 0.5 of its time on the
machines. Brad's work to resolve.
