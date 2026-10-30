---
id: retro-game-library
title: Retro game library (options research)
status: active
owner: brad
repo: 
path: 
memory_cell: project-retro-game-library
updated_at: 2026-10-30T01:51
---

**What it is:** Brad's emulator/ROM library problem. He wants one place to browse
and launch a retro collection with good metadata. Current incumbents are ruled
out: **Pegasus isn't cutting it** and **LaunchBox is good but too locked down
now**.

**Where we're at:** card-017 (research) is done — `org/notes/retro-game-library-options.md`
holds the candidate set with evidence: 12 live repos checked against GitHub
(stars, last push, latest release, license), plus the two incumbents' status.
The candidates split into four models: desktop launcher (Playnite, SimpleLauncher,
ES-DE/RetroBat, OpenBoxGL), library *server* + clients (RomM, Gaseous),
import-into-Steam (steam-rom-manager), and build-our-own. No software installed,
no direction chosen.

**Next:** Brad picks the model and the target device(s); that decides the shortlist.
Three questions are open in the note — desktop vs self-hosted server, whether the
metadata source matters, and whether "build it ourselves" is on the table.
A trial build (card-018) follows his answer; nothing gets installed without him.
