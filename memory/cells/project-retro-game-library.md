---
id: project-retro-game-library
kind: project
key: retro-game-library
updated: 2026-10-30T03:42
supersedes: []
confidence: high
---

Project 'retro game library' (org/projects/retro-game-library.md, status active, owner brad, no repo). Brad wants one place to browse and launch a retro collection with good metadata. Incumbents ruled out by Brad: Pegasus (no stable release since weekly_2024w38, metadata user-maintained) and LaunchBox (closed source, Big Box is a paid unlock). card-017 ran the options research (12 candidates, four models). decision-009 scoped it: Windows desktop frontend, no server, and PSP + multi-disc handling is the discriminator.

Verification pass against upstream source: Playnite (MIT, 14,393 stars, pushed 2026-10-19, release 10.63) is the leader - the shipped PPSSPP profile covers iso/cso/pbp/chd on sony_psp via PPSSPPWindows64.exe, source/Playnite/Common/M3U.cs parses playlists including RetroArch's ':'/'|' suffixes, and Scanner.cs treats .m3u/.cue/.gdi as playlists and groups '(...Disc 1)' style files into one game. Caveat: LaunchBox survives there only as a metadata provider plugin - no library importer - so the game list is re-scanned. SimpleLauncher (GPL-3.0, 266 stars, pushed 2026-10-30, release 5.8.4) is the challenger: PSP searches cso/chd/iso/pbp/elf/prx and ChdMountStrategy + DiscConverter are the deepest disc machinery found (CHD mount on 19 emulators, CHD->ISO, CHD->CUE/BIN, PBP->CUE/BIN), but no automatic m3u generation, no LaunchBox import, metadata limited to RetroAchievements + image packs. ES-DE out (multi-disc is hand-authored .m3u directories; psp = PPSSPP single disc image). Pegasus out (0 m3u code hits, no stable release in two years) despite shipping a LaunchBox data provider. OpenBoxGL out (localhost server architecture fails the ruling; PSP def has no chd).

card-018 exists in backlog to trial Playnite on Brad's real folders - blocked until he approves an install. Nothing installed.
