---
id: timeline-2026-10-30-retro-library-research
kind: timeline
key: 2026-10-30-retro-library-research
updated: 2026-10-30T03:42
supersedes: []
confidence: high
---

2026-10-30, retro game library research thread. Brad named the project and ruled out both incumbents: Pegasus ('not cutting it') and LaunchBox ('too locked down now'). card-017 researched 12 candidates against GitHub and each project's own site, grouped by model, naming two traps (Daijisho is closed-source despite the MIT badge; Aloshi/EmulationStation is dead). RomM initially looked like the standout because it can ingest LaunchBox metadata.

Brad then answered the three scoping questions (Windows desktop / desktop app with no server / RomM nogo because it struggles with PSP and discs) - that became decision-009 and reversed the RomM finding. Verification pass run against the ruling on upstream source: Playnite PPSSPP emulator.yaml reads iso/cso/pbp/chd on sony_psp; the DuckStation def includes m3u/chd/pbp/cue; M3U.cs parses playlists; Scanner.cs:1576-1622 extracts disc/disk/side properties as DiscName so multi-disc sets become one game; Jeshibu/PlayniteExtensions has Metadata_LaunchBox.yaml only (no library importer). ES-DE USERGUIDE 1316-1377 shows multi-disc needs hand-built .m3u-in-directory and psp is 'single disc image file'. SimpleLauncher parameters.md PSP extensions cso,chd,iso,pbp,elf,prx plus ChdMountStrategy/ChdToCueStrategy/PbpToCueStrategy/DiscConverter. Pegasus ships a LaunchBox data provider but has 0 m3u code hits. Note, project page, decision-009 file and card-018 written; nothing installed - card-018 waits on Brad's install approval.
