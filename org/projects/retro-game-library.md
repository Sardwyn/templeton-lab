---
id: retro-game-library
title: Retro game library (Windows desktop frontend)
status: active
owner: brad
repo: 
path: 
memory_cell: project-retro-game-library
updated_at: 2026-11-01T06:10
---

**What it is:** Brad's emulator/ROM library problem. He wants one place to browse
and launch a retro collection with good metadata, on a **Windows desktop**, as a
**desktop app with no server** (decision-009). Incumbents are ruled out:
**Pegasus isn't cutting it**, **LaunchBox is good but too locked down now**, and
**RomM struggles with PSP and discs in general**. PSP + multi-disc handling is the
discriminator the replacement has to pass.

**Where we're at:** card-017 (research) is done and the scoping questions are
answered. `org/notes/retro-game-library-options.md` now carries a verification
section: four candidates checked against their own source for PSP formats and
multi-disc behaviour. Shortlist is **Playnite** (MIT, WPF desktop, PSP
`iso/cso/pbp/chd`, automatic multi-disc grouping, LaunchBox *metadata* plugin but
no library importer) and **SimpleLauncher** (GPL-3.0, .NET desktop, deepest CHD/disc
mount-and-convert machinery, no metadata scraper beyond RetroAchievements/image
packs). **ES-DE** is out (multi-disc requires hand-authored `.m3u` folders) and
**OpenBoxGL** is out (localhost web app, and its PSP definition has no `.chd`).
Nothing is installed.

**Where the trial landed:** card-018 is **done 2026-11-01**, run as portable copies
under `F:\Lab\trials\` against the real folders, and
`org/notes/retro-game-library-options.md` now carries the measured results.
**Playnite passes the discriminator**: 76 library entries — 33 PSP ISOs plus 38 PSX
games from 52 CHDs with **all 9 multi-disc sets folded into one entry each**
(`MergeRelatedFiles`), text metadata auto-imported on 74 of 76 entries,
`Playtime`/`PlayCount` written, and a live PSP ISO launch through `F:\RetroArch`
passed. **SimpleLauncher does not pass it**: 33 PSP tiles and **52 PSX tiles, every
disc its own game**, no grouping, no generated `.m3u`, no metadata fields for
non-Steam systems — though its live PSP launch also passed and it tracks play time.
Ruled along the way: decision-012 (reuse Brad's RetroArch), decision-013 (offline
config when an app's UI is invisible to automation), decision-014 (runtime carried
portably in `trials\`), decision-015 (launch test limited to a PSP ISO).

**Correction, 2026-11-01:** artwork is **not** auto-filled. Playnite imported *text*
metadata automatically, but `Image` is set on **0 of 76** entries and no artwork
exists beside the roms, so artwork is still its own piece of work. See the disposal
and corrections section at the end of `org/notes/retro-game-library-options.md`.

**Trial disposal:** Brad said "delete what doesn't matter", so 1,794 MB of app trees,
portable runtime and installers were removed from `F:\Lab\trials\`. What remains is
`F:\Lab\trials\evidence\` — 25 files, 2.2 MB, SHA256-listed in
`F:\Lab\trials\evidence\MANIFEST.txt`: both apps' databases, plain-text dumps of them,
the measurement summaries and the scripts that derive them. `trials\` is gitignored, so
the evidence is deliberately untracked. `E:\Sony` was never written to; `F:\RetroArch`
was never edited, though RetroArch updated its own config and playlists when the trial
launched a game.

**Next:** the choice is Brad's. Adopting Playnite for real means a non-trial install
and a decision about his existing LaunchBox data (Playnite imports its *metadata*,
not its game list), plus a separate pass to get artwork.

