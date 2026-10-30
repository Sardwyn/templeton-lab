---
id: retro-game-library
title: Retro game library (Windows desktop frontend)
status: active
owner: brad
repo: 
path: 
memory_cell: project-retro-game-library
updated_at: 2026-10-30T02:35
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

**Next:** card-018 — trial Playnite (optionally SimpleLauncher alongside) against
the real PSP/PSX folders and check multi-disc grouping and PPSSPP launch. It waits
for Brad's approval to install; nothing gets installed without him.
