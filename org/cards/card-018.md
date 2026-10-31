---
id: card-018
title: Trial Playnite against the real PSP and multi-disc folders
column: in-progress
assignee: qwen
project: retro-game-library
depends_on: []
created_at: 2026-10-30T02:35
updated_at: 2026-10-31T06:54
---

**Unblocked 2026-10-31** — Brad approved the trial (logged as a note event, and in
`F:\Lab\org\decisions\2026-10-31-decisions-tab.md`): Playnite **and** SimpleLauncher
side by side, as portable copies under `F:\Lab\trials\` — nothing installed into the
system, nothing touched outside `F:\Lab`, `trials/` gitignored.

It was created on 2026-10-30 as a blocked card, when decision-002 still required
Brad's sign-off before anything installed; that approval is now on record, so the
blocked wording is superseded by the paragraph above.

**Goal:** find out whether Playnite actually handles Brad's PSP and multi-disc games
better than Pegasus and LaunchBox do today, before anything becomes dependent on it.

Steps (approved 2026-10-31, both apps in scope):
1. Get Playnite as a portable ZIP into `F:\Lab\trials\` — no system install, no
   registry, nothing written outside `F:\Lab`.
2. Add the PPSSPP emulator (its built-in definition already covers `iso, cso, pbp,
   chd`) and point the PSP platform at the real ROM folder; scan.
3. Point the PlayStation platform at the multi-disc folder; check that multi-disc
   games land under one entry rather than N separate ones.
4. Launch one PSP ISO/CSO and one multi-disc game end to end; note anything that
   needs manual `--` fiddling.
5. Same four steps for SimpleLauncher's portable build against the same folders, so
   the two are judged on the same two criteria (PSP formats, multi-disc grouping).

**Known caveat to verify, not assume:** Playnite has a LaunchBox *metadata* plugin
but no LaunchBox *library* importer, so the library gets re-scanned and only the
metadata is carried over.
