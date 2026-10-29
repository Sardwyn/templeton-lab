---
id: card-016
title: Fix yacht-director contract regression in swarm (3 red tests)
column: backlog
assignee: unassigned
project: swarm-playpen
depends_on: []
created_at: 2026-10-29T04:40
updated_at: 2026-10-29T04:40
---

Recorded so the finding has an owner slot instead of living only in prose.

`test/view/yacht-director.test.ts` fails 3/11 at `22cc654` (verified red); the
same file passed 11/11 at `29d7179`, so the regression was introduced by the
unassigned WIP now on main (see build-20261029-001, card-014).

Symptoms (from card-014): the director loses the agent `inchworm`, drifts the
view to 6.5 where its own contract says < 6, and drops the agent `caterpillar`.

This is Brad's WIP — he decides whether/when to fix it. The swarm project page
shows it as the open item until someone claims it.
