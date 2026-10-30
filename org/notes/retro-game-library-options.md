---
id: note-retro-game-library-options
title: Retro game library - frontend/options research
project: retro-game-library
card: card-017
created_at: 2026-10-30T01:51
---

Research only. Nothing installed, no direction chosen. Sources: GitHub API for
every repo below (stars, last push, latest release tag, license, language — read
2026-10-30), each project's own site/README, and community threads for the two
incumbents.

## Why the incumbents are out (evidence, not vibes)

| | What's actually true today |
|---|---|
| **Pegasus** | Site header reads "Latest version: **Failed to query the server**" for both the main and Scoop packages. Newest release tag on GitHub is `weekly_2024w38` (2024-10-05), i.e. two years of nightly/weekly builds and no stable cut — though commits still land (`mmatyas/pegasus-frontend`, last push 2026-10-29, 1,921 stars). Its users' recurring complaint is that **you maintain the metadata yourself** (no built-in scraper): the `.pegasus` metadata files are your problem. That matches "not cutting it". |
| **LaunchBox** | Closed-source, free base with **Big Box as a paid unlock** (~$20 lifetime per vendor-adjacent listings; I could not confirm the exact current tier from launchbox-app.com — the `/buy` path 404s). Its own changelog shows entitlement-shaped work: "*Big Box now has options to allow doing a bunch more things while **locked***", i.e. features are gated by lock mode rather than deleted. Community reports feature/paywall friction (TeknoParrot paywall thread) and 14.0 shipped with "27 planned changes". So "too locked down" is a real, documented drift, not Brad imagining it. Also: LaunchBox's library is its own XML trees under its install folder, which is portable but vendor-shaped. |

## The four models (this is the actual decision)

**A. Desktop launcher, local files** — one app on the machine, library on disk.
- **Playnite** (`JosefNemec/Playnite`) — MIT, C#, 14,393 stars, release **10.63**
  2026-10-19, Windows only. Unified library across Steam/Epic/GOG/EA/Battle.net
  *and* console emulators (Configure Emulators + ROM scanning), free fullscreen
  mode for controller/TV use, themes + extensions. Emulator setup is the weak
  spot: the community's own words are "adding emulators is a bigger hassle than
  Steam Rom Manager", and retro metadata scraping needs an extension (IGDB /
  ScreenScraper / SteamGridDB all free). **The strongest MIT, no-paywall,
  actively-released option for a Windows box.**
- **SimpleLauncher** (`purelogiccode/SimpleLauncher`) — GPL-3.0, C#/.NET, 266
  stars, release `release5.8.4` 2026-10-20, **Windows + Linux (x64/ARM64)**.
  WIMP frontend, cover art, multi-emulator, gamepad, **deep RetroAchievements
  integration**. Small project, single maintainer, moving fast; younger than
  Playnite so expect rougher edges.
- **ES-DE** (`es-de.org`, source on GitLab `es-de/emulationstation-de`) — free and
  fully open source on **Windows/macOS/Linux** (Windows installer *and* portable
  ZIP, Linux AppImages incl. Steam Deck/aarch64), latest **3.5.0 released
  2026-09-30**, ships preconfigured for 150+ systems with a **built-in scraper**
  for game info, media, videos and manuals, plus a theme downloader. Android
  exists but is a **paid app and partially closed source**. RetroBat
  (`RetroBat-Official/retrobat`, release 8.3.1 2026-10-16) is the Windows
  convenience wrapper that installs ES-DE + emulators for you — note its license
  is `NOASSERTION`, so it's freeware-distributed rather than cleanly licensed;
  ES-DE itself is the licensed part (GPL-family, MIT on the Batocera fork).
- **OpenBoxGL** (`vindeckyy/OpenBoxGL`) — AGPL-3.0, Python, 35 stars but shipping
  weekly (v1.19.1 on 2026-10-28), Linux/Windows/macOS, explicitly pitched as an
  open LaunchBox-style launcher: local-first `library.json`, one UI over Steam,
  Heroic, Lutris, ROM folders, ScummVM, RPCS3, Vita3K, executables, REST API,
  **Big Box mode**, no account/telemetry/cloud. Very young and one maintainer —
  architecturally the cleanest "no lock-in" story in the list.

**B. Self-hosted library *server* + thin clients** — metadata/artwork/saves in a
central service, browse from any device.
- **RomM** (`rommapp/romm`) — AGPL-3.0, Python, **14,160 stars**, release **5.4.1**
  2026-10-22, last push 2026-10-29. Scan + enrich from **IGDB, ScreenScraper,
  LaunchBox and MobyGames**, artwork from SteamGridDB, RetroAchievements, 400+
  platforms, multi-disk/DLC/mods/hacks, in-browser play via EmulatorJS/RuffleRS,
  save/state sync with conflict resolution, per-user permissions + OIDC SSO, ROM
  patcher, self-described "free forever: AGPL-3.0, no tracking, no paid features".
  Official clients: **Playnite app**, **Android (Argosy launcher**, 701 stars),
  and CFW builds (**grout** 250, **Freegosy** 258). **The one that solves Brad's
  problem outright** — it also *imports LaunchBox metadata*, so the years of
  library work don't get thrown away. Cost: it wants Docker + a mounted ROM
  folder + a machine that's always on.
- **Gaseous** (`gaseous-project/gaseous-server`) — AGPL-3.0, C#, 954 stars, last
  push 2026-10-28, but newest release tag is **v1.7.14 from 2025-07-31** — commits
  without releases. Same server model, plus `hasheous` (57 stars) as the ROM
  hashing/identification service. More of a hobby-grade equivalent to RomM.

**C. Import into Steam, use Steam as the frontend**
- **steam-rom-manager** (`SteamGridDB/steam-rom-manager`) — GPL-3.0, TypeScript,
  2,594 stars, release v2.5.44 2026-08-06. Bulk-adds ROMs/emulators as non-Steam
  entries with SteamGridDB art. Zero new UI to learn (Big Picture is the
  frontend), and it pairs well with Playnite or RomM later rather than competing
  with them.

**D. Build our own** — the honest third path. `OpenBoxGL`'s shape (flat JSON
library + scraper clients + REST API + controller mode) is roughly a weekend of
qwen work for the browse/launch core; the *real* cost is metadata providers,
platform identification (hasheous-style hashing), and artwork curation, which is
years of accumulated data, not code. Worth keeping on the table only if Brad wants
the library format to be his own.

## Dead / avoid

`SnowflakePowered/snowflake` (archived 2022), `hydra-emu/hydra`,
`kaylh/old-RetroBat-obsolete`, `Aloshi/EmulationStation` (last push 2024-07, last
release 2014 — use `batocera-linux/batocera-emulationstation`, pushed 2026-10-28,
MIT, or ES-DE instead). **Daijishō** is a trap worth naming: `TapiocaFox/Daijishou`
carries an MIT badge and 1,966 stars, but its README says it is **currently
closed-source** — that repo is assets plus the issue tracker; the app is free but
not open. If Apple devices are in scope, `Provenance-Emu/Provenance` (6,391 stars,
pushed today) is the iOS/tvOS frontend.

## If Brad wants a one-line answer

**RomM** if he wants the collection reachable from more than one device and is
fine running a server (and it can eat his existing LaunchBox metadata).
**Playnite** if he wants a Windows desktop app today with no paywall and no
server. **ES-DE** if he wants the couch/handheld feel with controller navigation
and a built-in scraper.

## Three questions Brad needs to answer before anything gets installed

1. **Target device(s)?** Windows desktop, a living-room box / Steam Deck, Android
   handhelds, or all three — the model choice follows the device, not the software.
2. **Desktop app, or self-hosted server with clients?** RomM/Gaseous need an
   always-on host and Docker; A-model options need none of that.
3. **Does the metadata source matter, and is "build it ourselves" allowed?**
   ScreenScraper vs IGDB vs LaunchBox's own data, and whether he wants the library
   format to be his own rather than somebody else's schema.
