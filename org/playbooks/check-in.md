# Check-in SOP — all agents

Templeton Systems · F:\Lab · v1.6 (2026-10-29)

v1.6 (decision-007): projects are first-class artifacts. `org/projects/<id>.md`
is the source for what a project is; **every card and build carries `project:`**,
and `state/PROJECTS.md` is a generated view regenerated at every check-in. A
project's memory cell is named explicitly (`memory_cell:`), never guessed by
keyword. Events stay unchanged — their `card` / `build_id` / `cell` / `repo`
refs resolve to a project. No new event types.

v1.5 (decision-006): the org is hosted on GitHub. Two independent repos —
HQ and `swarm/` — both public, qwen is the carrier who lands and pushes.
Every push is logged with `repo` and `branch` context and `note: landed by
qwen`. `swarm/` is gitignored by HQ; never commit it into the HQ tree.

v1.4 (decision-005): single-writer org — qwen is the sole direct-check-in
agent; cloud agents are dispatch-only (no heartbeats); generated views
(board/outbound/brief/dashboard) regenerate at every check-in.

This is the operating protocol for every agent in the org. Where it conflicts
with an agent's defaults, this document wins — unless a newer file in
`org/decisions/` overrides it (human rulings are final).

## Roster (current)

| id | side | role |
|----|------|------|
| qwen | **local** (only local agent, on this box) | main executor |
| copilot | cloud | architect / coordinator |
| cursor | cloud | via IDE |
| grokbot | cloud | — |
| opencode | cloud | — |

Brad = CEO — the org addresses the human as **Brad** (ruled 2026-10-14).
Rulings land in `org/decisions/`. New agents only by human decision.

## Session start

0. **qwen (local only):** run `cd /d F:\Lab & python worker\recall.py [topic]`
   — the Lattice read head. One command hydrates: core memory, relevant
   memory cells, and full org state (board, pings, events, roster). See
   "Memory — the Lattice" below. Session rules (v1.3):
   - **New chat** = new session = full recall.
   - **New task in the same loaded chat** = light recall (core is already in
     context); full recall again if the context window truncated — that is
     partial amnesia, re-hydrate.
   - VRAM residency is not on-duty: loaded-and-idle = off-duty.
1. Read `F:\Lab\state\BOARD.md` (or the dashboard) — what's open, who owns what,
   what's blocked. For project-scoped work read `state\PROJECTS.md`, or the
   source itself at `org/projects/<id>.md`.
2. Check your inbox `F:\Lab\org\inbox\<you>\` — process every message file,
   then delete it (processed) or move it to `org/inbox/<you>/done/`.
3. Skim the newest files in `org/playbooks/` and `org/decisions/` for changes.
4. Pick work:
   - Card assigned to you in `in-progress` → resume it.
   - Otherwise claim from `backlog` (edit frontmatter: `column: in-progress`,
     `assignee: <you>`, bump `updated_at`).
   - Local agent (qwen) prefers work that needs this box: builds, local tests,
     F:\Lab maintenance, GPU jobs.
5. Log the claim: append one JSON line to `org/events/<YYYY-MM-DD>.jsonl`
   (see Event log below).

## Working rules

- **One file per artifact.** Never hold a lock on a shared file. If two agents
  might touch the same thing, split into files.
- **Cards:** frontmatter is the API. `column:` is one of
  `backlog | in-progress | review | done | blocked`. Cards move by editing
  their own file. IDs are permanent — never rename, never reuse. Every new
  card carries `project:` — the id of a project in `org/projects/`.
- **Projects:** `org/projects/<id>.md` is the source for a project's prose and
  status; its memory cell is named by `memory_cell:`, not by keyword search
  (decision-007). Update the project artifact when a project moves forward —
  that is where "where we're at" lives. `state/PROJECTS.md` is generated.
- **Blocked:** set `column: blocked`, put a note in `org/inbox/human/` saying
  exactly what decision is needed, then keep working other cards.
- **Builds:** run through `mLattice/tasks/` pipelines where one exists;
  record every build (pass **and** fail) per the build record format below.
- **History is immutable.** Never delete events, decisions, or done cards.
  Corrections are new files or new event lines — never rewrites (the event log
  is the one place in-place edits are tolerated for obvious typos).
- **No new agent identities** without a human decision in `org/decisions/`.

## Build records (`org/builds/`)

One file per build run, named `<id>.md`:

```markdown
---
id: build-YYYYMMDD-NNN        # NNN = that day's build number, 001-based
target: <repo or project>
project: <project id>         # required (decision-007); via apply.record_build_event(project=...)
agent: <you>
status: pass | fail
ts: <ISO 8601 local>
---

command: <what was run, one line>
exit: <code>
log: <last ~20 lines or link>
notes: <anything a future agent needs>
```

`NNN` continues from the highest existing `build-YYYYMMDD-*` file for that date.

## Message format (inboxes)

One file per message: `<YYYYMMDD-HHMM>-<short-topic>.md`

```markdown
---
from: <you>
to: <recipient>
subject: <one line>
---

Body. Keep it actionable: state, decision needed, link/path to details.
```

## Event log (`org/events/<YYYY-MM-DD>.jsonl`)

One JSON object per line, append-only. Fields:
`ts` (ISO local), `agent`, `type`, plus context (`card` or `card_id`,
`build_id`, `cell`, `repo`, `file`, `note`). Events stay unchanged even after
decision-007: a project page finds its events by resolving those refs to a
project through the card/build/cell that carries `project:` — so there is no
`project_event` type and no rewriting of old lines.

Types: `card_create`, `card_claim`, `card_done`, `build_pass`, `build_fail`,
`decision`, `message`, `identity_fix`, `note`, `memory_write`.

## Session end — always, even if you did nothing

1. Update your card(s): status, `updated_at`, and a short body note if the
   state changed meaningfully.
2. Record every build you ran.
3. Drop messages for other agents (their inboxes, your own inbox is yours).
4. Append events for everything notable.
5. Regenerate the derived views — they are never sources of truth
   (decision-005). `worker\sync.py` writes RECALL/outbound, `worker\dashboard.py`
   writes `dashboard/index.html` + `state/BOARD.md` + `state/PROJECTS.md`,
   `worker\brief.py` writes the cloud brief:
   ```
   cd /d F:\Lab & python worker\sync.py & python worker\dashboard.py & python worker\brief.py
   ```
   (cmd.exe: separate with `&`, not `&&`.)
6. **qwen:** consolidate memory — check core.md (update only if a standing
   preference changed); cells for new learning should already exist (written
   **when learned**, incrementally — see below).
7. Commit with `[<card-id>] <imperative summary>` as the message. **qwen is the
   carrier** (decision-006): commit in HQ, push HQ; commit and push `swarm/`
   separately — never a subtree of HQ. Cloud agents do not push.

## Heartbeats, schedules, liveness

- At session start and end, each agent updates its own file
  `org/agents/<you>.md`:
  - `last_heartbeat` — ISO local timestamp (`YYYY-MM-DDTHH:MM`).
  - `status` — one of `on-duty` | `off-duty` | `cloud`.
  - `focus` — what you're currently working on (one line).
  - `schedule` — your declared cadence (free text, e.g. "on demand",
    "daily 08:00 standup").
- The dashboard renders each agent's schedule, the age of their last
  heartbeat, and flags **STALE** when a `on-duty` agent's heartbeat is
  older than 24h.
- **Cloud agents are dispatch-only (v1.4, decision-005).** They do not
  heartbeat and no one flags them stale; a dispatch runs with a fresh brief
  and its result, if any, lands as files + events at qwen's next check-in.
- **Standup (v1, when the org is active)**: one small file per agent per
  day at `org/standup/<YYYY-MM-DD>/<agent>.md` — did / next / blocked.

## Pings and activation

- A **ping** is an inbox message with `activate: true` in its frontmatter.
  It is a request to spend attention — and, for paid agents, money.
- File: `org/inbox/<to>/<YYYYMMDD-HHMM>-ping-<topic>.md`, frontmatter:
  `from`, `to`, `subject`, `activate: true`, `card` (the work item —
  always link it), `work` (optional: path or URL of the actual
  artifact), `needs` (one line: the decision or action required),
  `cost` (for paid agents: low | med | high).
- **Agents don't spend, agents ask.** Pings to paid/cloud agents (cursor,
  grokbot, opencode) always route through the CEO: drop the ping in
  `org/inbox/brad/` with the card, the brief, and the expected
  deliverable. Brad decides activation.
- **Activation = one paste.** Every ping must be self-contained so the
  target session is one paste in, one org-update block out.
- **Cloud → qwen pings** arrive inside the cloud agent's org-update block;
  qwen acts on them at its next session (immediately if the CEO is already
  in a session with qwen).
- Open pings render in the dashboard **Pings** strip at the top.

## Temporal grounding (Copilot and all cloud agents)

- Cloud sessions are stateless. Never hand a cloud agent raw context.
- Before every cloud handoff, run:
  ```
  cd /d F:\Lab & python worker\brief.py <agent-id>
  ```
  It prints the brief (also written to `state/BRIEF.md`): current date,
  board snapshot, open pings, recent events, roster, and the reply format.
  Paste the brief into the cloud session, then the task. The date line in
  the brief is the anchor for "what is current".
- Copilot specifically: no temporal awareness (CEO-confirmed). It must
  receive a fresh brief in **every** session — never assume it remembers.

## Memory — the Lattice (qwen)

The Lattice is **Qwen's persistent memory** — the local model is stateless
between sessions, so everything Qwen knows about Brad, his preferences, and
the history lives here, not in any session. (Brad's ruling, 2026-10-15: the
Lattice is for Qwen — it is the local model that must remember him.)

- **Hot tier** — `memory/core.md`: identity, who Brad is, standing
  preferences, pointers. Always loaded. Small (< ~60 lines). Distill, don't
  dump.
- **Warm tier** — `memory/cells/`: one file per memory, frontmatter:
  `id` (kind-key), `kind` (preference | person | project | decision |
  timeline | lesson | fact), `key`, `updated`, `supersedes: []`,
  `confidence`. Body = the memory in 1-3 lines.
- **Read head** — `python worker/recall.py [topic]`: core + standing
  cells + 5 most recent + topic matches + org state. Superseded cells are
  excluded (overwrite semantics — never delete, replace).
- **Write head** — `python worker/remember.py <kind> <key> <text>`
  (or edit cells directly): creates/updates the cell, appends a
  `memory_write` event. When a preference *changes*, write a new cell with
  `--supersede <old-id>`.
- **Writes are incremental (v1.3).** Brad keeps Qwen loaded across hours or
  a day, so "session end" can be far away — never batch learning to it. Write
  the cell the moment a preference, lesson, or project fact is learned;
  session end is *consolidation* (core check, commit, heartbeat), not
  creation. A new chat always gets a fresh recall, so nothing depends on the
  previous chat still being open.
- **Timeline**: `org/events/*.jsonl` is the raw timeline; Qwen distills
  significant moments into `kind: timeline` cells.
- **Session end (qwen)**: write what was learned (new/updated cells);
  update `memory/core.md` only if a *standing* preference changed; commit.
- **Explicit trigger:** when Brad says "remember: X", "write that down",
  or "standing pref" — Qwen writes the cell **immediately** (before
  continuing) and shows **proof**: cell content, path, and the
  `memory_write` event. Standing prefs also get a line in core.md
  (hot tier). No verbal acknowledgement without the artifact.
- **A write is real only if the next session reads it back:**
  `kind: preference` / `person` cells are always loaded by recall.py;
  everything else is topic-searchable.
- **Audit:** `python worker\memory_audit.py` — cell integrity (parse,
  unique ids, valid kinds), coverage (every org/decisions/ ruling must be
  reflected in memory), freshness. Run after bulk memory work; close gaps.
- **Cloud agents do not have the Lattice.** Their memory is the brief
  (org state) — Qwen's relational memory stays local, and relevant bits
  (e.g. Brad's preferences) are shared via decisions/ and briefs.

## Escalation (when in doubt)

Ask the human before: deleting anything, installing software, touching
anything outside F:\Lab, spending money, or publishing anything.
Drop the question in `org/inbox/brad/` and set the relevant card to blocked
if it can't proceed without the answer.
