---
id: swarm-playpen
title: Swarm Playpen (director/yacht sim WIP)
status: active
owner: brad
repo: https://github.com/Sardwyn/swarm-playpen
path: F:\Lab\swarm\swarm
memory_cell: project-swarm-playpen
updated_at: 2026-10-29T04:40
---

**What it is:** Brad's swarm-agent experiment — a small TypeScript/Vite app
(`Director`/`AgentController` classes) whose contract tests encode the rules
the runtime must obey. Independent repo; HQ ignores the folder.

**Where we're at:** WIP committed honestly on `main` (`22cc654`): typecheck
clean, `vitest run` **red** — 471 passed, 3 failed in
`test/view/yacht-director.test.ts` (build-20261029-001). The same file passed
11/11 at `29d7179`, so the WIP introduced the regression: director loses
`inchworm`, drifts to 6.5 (contract says < 6), drops `caterpillar`.

**Next:** card-016 (backlog, unassigned — Brad's call when to fix).
