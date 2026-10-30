---
id: card-018
title: Trial Playnite against the real PSP and multi-disc folders
column: backlog
assignee: unassigned
project: retro-game-library
depends_on: []
created_at: 2026-10-30T02:35
updated_at: 2026-10-30T02:35
---

**Blocked on Brad's approval — nothing installs without it** (decision-002 still
holds). This card exists so the next step is on the board rather than only in prose.

**Goal:** find out whether Playnite actually handles Brad's PSP and multi-disc games
better than Pegasus and LaunchBox do today, before anything becomes dependent on it.

Steps once approved:
1. Install Playnite (portable ZIP is the least invasive option) — **Brad approves
   the install first**.
2. Add the PPSSPP emulator (its built-in definition already covers `iso, cso, pbp,
   chd`) and point the PSP platform at the real ROM folder; scan.
3. Point the PlayStation platform at the multi-disc folder; check that multi-disc
   games land under one entry rather than N separate ones.
4. Launch one PSP ISO/CSO and one multi-disc game end to end; note anything that
   needs manual `--` fiddling.
5. Optional second pass: SimpleLauncher portable build, same folders, judged on the
   same two criteria (PSP formats, multi-disc grouping).

**Known caveat to verify, not assume:** Playnite has a LaunchBox *metadata* plugin
but no LaunchBox *library* importer, so the library gets re-scanned and only the
metadata is carried over.
