# Templeton Systems — HQ

This repository is the **org record** for Templeton Systems, a small
human-plus-agents company run by Brad (CEO) with one local agent, **qwen**, and
a roster of dispatch-only cloud agents (copilot, cursor, grokbot, opencode).

Everything here is a file, append-only, so the record can be inspected and
traced rather than remembered:

| path | what it is |
|------|------------|
| `org/cards/` | one file per card; card IDs are permanent |
| `org/decisions/` | Brad's rulings — these override everything |
| `org/events/*.jsonl` | the event log: append-only timeline, incl. push provenance |
| `org/playbooks/check-in.md` | the operating protocol every agent follows |
| `org/inbox/` | messages between agents |
| `worker/` | the machinery: recorders, board sync, dashboard, memory tools |
| `memory/` | qwen's private memory (the Lattice) — not a general org system |

`state/` holds the **generated views** — `BOARD.md`, `BRIEF.md`, `RECALL.md`.
They are rebuilt at every check-in and are never sources of truth, so they are
not committed. The dashboard is generated on request too
(`python worker/serve.py` → http://localhost:8901).

## Two repositories

`swarm/` — the inspection-simulation project — is a **separate repository**
([Sardwyn/swarm-playpen](https://github.com/Sardwyn/swarm-playpen)) and is
gitignored here. HQ and swarm keep independent histories by design
([decision-006](org/decisions/2026-10-29-github-hosting.md)).

## Reading order

1. [`org/playbooks/check-in.md`](org/playbooks/check-in.md) — how work is claimed,
   recorded, and closed.
2. [`org/decisions/`](org/decisions/) — the rulings, newest first.
3. [`org/board/BOARD.md`](org/board/BOARD.md) — what is open right now.
