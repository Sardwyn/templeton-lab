---
id: decision-011
date: 2026-10-31
status: active
title: Decisions get their own dashboard tab, listed newest first
decided_by: brad
---

# Decision-011: Decisions get their own dashboard tab, listed newest first

**Ruled by Brad on 2026-10-31**, when asked whether the decision log should stay
inside the Roster pane or become a tab of its own. He chose a dedicated tab.

## The rule

1. **`#decisions` is a tab and a pane.** Decisions no longer render under
   `#roster`; the roster pane holds agents and inboxes only. The tab bar reads
   `board · projects · pings · roster · decisions · memory · builds · events`.
2. **Newest ruling first.** The decision files in `F:\Lab\org\decisions\` are
   *date*-named (`2026-10-29-single-writer-dispatch.md` = `decision-005`), so
   filename order is not ruling order. The pane sorts by the frontmatter `date`,
   falling back to the zero-padded `id` for same-day rulings — so the pane reads
   `decision-010 … decision-001`, and the caption is truthful.
3. **Decision-010's linking rule still applies here:** every row's first column is
   a clickable link labelled with the full `F:\Lab\...` path of the decision file,
   a missing file renders dim rather than hidden, and clicking the row opens the
   whole ruling in the drawer with its own source link.

## Why

The decision log is the thing Brad re-reads to remember why something is the way it
is. Buried under Roster it is the hardest part of the dashboard to find, and sorted
by filename it presents rulings out of order — a log that reads `003, 001, 002, 004`
is easy to misread as the sequence of events when it is only alphabetical.

## Consequence

- `F:\Lab\worker\dashboard.py`: a `data-pane="decisions"` section, a `Decisions`
  tab in the nav and the sub-line, and `load_decisions()` sorts its output newest
  first instead of by filename.
- Verified over http on 2026-10-31: `#decisions` activates both the pane and the
  tab, the pane holds exactly 10 decision rows in order `010, 009, 008, 007, 006,
  005, 004, 003, 002, 001`, clicking a row opens its drawer (2,745 chars) with the
  source link `F:\Lab\org\decisions\2026-10-31-dashboard-full-path-links.md`, 226
  full-path anchors page-wide, and zero dim/missing links.

## Other rulings the same session (recorded as events, not new policy)

Brad also approved the card-018 trial — **Playnite and SimpleLauncher side by
side**, portable copies under `F:\Lab\trials\`, nothing installed into the system —
and authorised deleting the three doubled-name memory cells. Both are logged as
`note` events in `F:\Lab\org\events\2026-10-31.jsonl`; the trial stays inside the
Windows-desktop-only constraint already ruled in Decision-009
(`F:\Lab\org\decisions\2026-10-30-retro-library-desktop-only.md`).
