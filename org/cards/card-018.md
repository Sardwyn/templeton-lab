---
id: card-018
title: Trial Playnite against the real PSP and multi-disc folders
column: done
assignee: qwen
project: retro-game-library
depends_on: []
created_at: 2026-10-30T02:35
updated_at: 2026-11-01T04:05
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

## Done 2026-11-01 — outcome

Step 4 was narrowed by Brad's ruling (**Decision-015**,
`F:\Lab\org\decisions\2026-11-01-launch-test-psp-only.md`): one live launch per
frontend on a PSP ISO, **no multi-disc live launch**. Full measured results, both
candidates, are in `F:\Lab\org\notes\retro-game-library-options.md`.

| Step | Result |
|---|---|
| 1 — portable Playnite in `trials\` | done, no system install |
| 2 — PSP platform on the real folder | **33 games** from `E:\Sony\PSP` (33 ISOs) |
| 3 — PSX platform, multi-disc | **38 games** from 52 CHDs, **all 9 multi-disc sets collapsed into one entry each** with a multi-entry `Roms` list |
| 4 — live PSP launch | **passed** — `playnite.log` shows RetroArch + `ppsspp_libretro.dll` + the ISO, frames hashed differently while focused, `Playtime 848` / `PlayCount 1` recorded |
| 5 — SimpleLauncher, same folders | PSP **33 tiles**, PSX **52 tiles** — every disc its own tile, **no grouping, no `.m3u`**; live PSP launch **passed** with the same RetroArch command line; `PlayHistory` / `SystemPlayTimes` recorded |

**Verdict:** Playnite passes the discriminator (PSP images + multi-disc without
hand-built playlists) and SimpleLauncher does not — its raw CHD machinery is stronger
on paper, but on the real folder it presents each disc as a separate game.

Also ruled along the way: reuse Brad's existing `F:\RetroArch` rather than ship
emulators (**Decision-012**,
`F:\Lab\org\decisions\2026-10-31-trial-reuses-existing-retroarch.md`), write config
offline when an app's config UI is invisible to automation (**Decision-013**,
`F:\Lab\org\decisions\2026-10-31-playnite-config-offline.md`), and carry required
runtimes inside `trials\` instead of installing them (**Decision-014**,
`F:\Lab\org\decisions\2026-11-01-portable-runtime-in-trials.md`).

Nothing of Brad's was disturbed: `F:\RetroArch` untouched, both trial apps and every
trial game window closed, restore points kept in `F:\Lab\trials\plbak\` and beside
`F:\Lab\trials\simplelauncher\settings.dat`. What happens to `trials\` is Brad's call.
