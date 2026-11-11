---
id: decision-016
date: 2026-11-10
status: active
title: grokbot checks in directly, alongside qwen
decided_by: brad
amends: decision-005
---

# Decision-016: grokbot checks in directly, alongside qwen

**Ruled by Brad on 2026-11-10.** grokbot (Grok Bot "Eddie", Brad's chief of
staff) gets full check-in rights, the same as qwen. The org stops being
single-writer.

## The rule

1. **grokbot is a direct check-in agent.** It follows `org/playbooks/check-in.md`
   exactly as qwen does: reads the board and its inbox `org/inbox/grokbot/`,
   claims cards, moves them by editing their own file, files messages, records
   builds, and appends events.
2. **grokbot may commit and push HQ.** Commits use `[<card-id>] <summary>`.
   Before pushing it pulls with rebase; it never force-pushes and never rewrites
   commits already on `origin/main`.
3. **Two writers, one file per artifact.** grokbot and qwen never edit the same
   card at the same time: the agent named in `assignee:` owns the card file.
   Event lines are append-only for both. If a pull brings a conflict on a file
   the other agent owns, grokbot keeps the other agent's version and adds its
   change as a new event or note.
4. **Heartbeat.** grokbot keeps `org/agents/grokbot.md` with `status`,
   `last_heartbeat`, `focus` and `schedule`, and is flagged STALE like any
   on-duty agent.
5. **Unchanged from decision-005 for everyone else.** copilot, cursor and
   opencode stay dispatch-only. Escalation rules still apply to grokbot: ask
   Brad before deleting anything, installing software, touching anything
   outside F:\Lab, spending money, or publishing.
6. **The Lattice stays qwen's** (decision-016 does not change the 2026-10-15
   ruling). grokbot has its own memory and does not write `memory/`.

## Why

Brad wants his chief of staff to pick up jobs from the dashboard directly
instead of every job routing through a paste-in brief and qwen landing the
result.
