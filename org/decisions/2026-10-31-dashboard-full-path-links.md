---
id: decision-010
date: 2026-10-31
status: active
title: Every artifact reference in the dashboard is a clickable full-path link
decided_by: brad
---

# Decision-010: Every artifact reference in the dashboard is a clickable full-path link

**Ruled by Brad on 2026-10-31**, after he could not open the recommendations note:

> "I can't open your recommendations file... nothing in the Dashboard links to it"

## The rule

1. **Anything that names an artifact is a link to that file.** Cards, projects,
   notes/deliverables, decisions, builds, memory cells, agent files, and event
   refs are all clickable, in the board, the project panes, the drawers and the
   event tables.
2. **The label is the full Windows path**, `F:\Lab\org\notes\...`, not a bare id
   and not a filename. Brad reads a path and opens it; `card-017` is not something
   he can open.
3. **A missing file is shown, never hidden and never invented.** If the file on
   disk does not exist, the row prints dim text with the path it was written to.
   Prose that is not a path stays prose — an event's `note` text is never dressed
   up as a path it does not have.
4. **Two serving modes.** `worker/serve.py` on :8901 resolves links as
   `/raw/<repo-relative path>`; opening `dashboard/index.html` straight from disk
   rewrites them to `../<repo-relative path>`. The page picks the mode from
   `location.protocol`. Absolute `F:\Lab\...` labels are never used as hrefs — a
   `file://` href would only work from the machine that generated the page.

## Why

The dashboard is the org record's front door. A reference that cannot be opened is
a reference Brad has to go find himself, which defeats the point of a record that
is supposed to be self-contained. Fabricating a path for an artifact that has no
file would be worse than showing nothing, because it looks authoritative and is
wrong.

## Consequence

- `worker/dashboard.py` gained the link machinery: `win_path()`, `rel_of()`,
  `ref_link()`, `ref_cell()`, `linkify()`, `event_ref_html()`, a `FILE_INDEX`
  built from the repo tree, and a `PATHISH_RE` guard that keeps prose out of the
  path column.
- Notes/deliverables are first-class artifacts now: a `Deliverables & notes`
  table on the board, a `Deliverables here` table per project, and a Notes column
  on the card board. Scope comes from the note's own `project:` frontmatter.
- Every drawer shows its own source line, labelled with the full Windows path
  (`win` field on every artifact record).
- `worker/serve.py` serves `.md` as `text/plain; charset=utf-8` so a clicked note
  renders in the browser instead of downloading.
- Verified over http on 2026-10-31: 231 full-path anchors, 216 of them pointing at
  `/raw/…` (74 unique), every one fetching 200, and zero hrefs pointing at a file
  that does not exist on disk.
