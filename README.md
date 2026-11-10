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
not committed. The dashboard is generated on request. From the repo root
(on the HQ box that is `F:\Lab`):

    python worker/serve.py

Then open http://localhost:8901 . The server uses the checkout that contains
`worker/serve.py`, so the same command works in that folder and in any other
clone. The page is the control surface: a kanban of one project at a time (drag a
card between columns to change its status; the project is in the URL) and a
thread per project and per agent, built from `org/inbox/` (including `done/`)
and `org/events/`. Saving a card updates that card's frontmatter and appends
one event line. Posting a message writes a new file in `org/inbox/<recipient>/`
and appends a `message` event. Posting a note appends a `note` event. Nothing
is deleted, event lines are not rewritten, and `org/decisions/` is not
editable from the page. `python worker/dashboard.py` still regenerates
`dashboard/index.html`, `state/BOARD.md`, and `state/PROJECTS.md` without
starting the server.

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
