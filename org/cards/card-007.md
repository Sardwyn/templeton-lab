---
id: card-007
title: Agent entries (scope/role/schedule) + ping/activation protocol
column: done
assignee: qwen
depends_on: ["card-003"]
created_at: 2026-10-14T07:25
updated_at: 2026-10-14T08:05
---

1. Upgrade org/agents/*.md to formal entries: scope, schedule (real cadences
   per CEO 07:25), activation cost, charter body.
2. Ping protocol: inbox messages with activate: true = activation requests
   for paid/cloud agents; dashboard Pings strip; agents don't spend, agents ask.
3. worker/brief.py — temporal-grounding brief for cloud agents (Copilot is
   not temporally aware; every handoff carries date + board + events + pings).
4. SOP v1.1: ping + temporal grounding rules. Decision-003: cadences + cost gate.

## Delivered

- All five org/agents/*.md upgraded to formal entries (scope, schedule,
  activation cost, charter) with CEO-ruled cadences.
- Ping protocol live: activate:true inbox messages + dashboard Pings strip.
  First ping filed: org/inbox/human/20261014-0740-ping-agent-scopes.md.
- worker/brief.py — temporal-grounding brief (tested against copilot;
  output verified clean in state/BRIEF.md).
- SOP v1.1: Pings and activation + Temporal grounding sections.
- decision-003 recorded (cadences, cost gate, Copilot brief requirement).
