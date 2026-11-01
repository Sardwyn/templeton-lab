---
id: templeton-lab
title: Templeton Lab (HQ)
status: active
owner: brad
repo: https://github.com/Sardwyn/templeton-lab
path: F:\Lab
memory_cell: project-templeton
updated_at: 2026-11-01T06:45
---

**What it is:** the org itself — HQ at `F:\Lab`. Board, inboxes, event log,
dashboard (:8901), playbooks, qwen's memory lattice. Agents are departments.
Projects are artifacts here too (`org/projects/`, decision-007).

**Where we're at (updated 2026-11-01):** everything is on GitHub (decision-006),
protocol is v1.6, and card-015 is closed: every project now has a page
(`#proj/<id>`) built from its own source file, with cards, builds and events scoped
by reference rather than keyword. Decision-010 (full-path links) and decision-011
(the decisions tab) are implemented — and on 2026-11-01 decision-010 was actually
enforced: `LINK_RE` in `worker/dashboard.py` was double-escaped, so paths written in
prose never became links and the fallback printed wrong labels; written directories
now render as directories instead of dim "missing" files, trial evidence under
`trials\` is indexed, and a `push` ref links to the commit it pushed.
16 cards done, 3 open — card-013 parked until real cloud traffic, card-016 belonging
to swarm-playpen, card-019 waiting on Brad's stage-0 sign-off. Only qwen has ever
checked in: the cloud departments exist as roster, not traffic (card-012 reality).

**Next:** nothing pending in HQ except Brad's calls — whether to adopt Playnite for
real, the swarm rebuild spec (decision-008), and whether to dispatch a cloud agent at
all; until a dispatch returns real work, card-013's inbound parser stays unbuilt.
