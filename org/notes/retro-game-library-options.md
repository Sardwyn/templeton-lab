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

---

## 2026-10-30 — Brad's ruling and the verification pass

Brad answered all three (as **decision-009**,
`org/decisions/2026-10-30-retro-library-desktop-only.md`): **Windows desktop**,
**desktop app with no server**, and **RomM is a nogo because "it struggles with PSP
and Discs in general"**. Everything below supersedes the model B section and the
one-line answer above; nothing there is deleted, because it happened.

The discriminator became testable: **does the frontend handle PSP images and
multi-disc games without the user hand-building playlists?** Four candidates were
checked against their own source, not their marketing copy.

| Candidate | License / health | PSP formats it looks for | Multi-disc | LaunchBox path |
|---|---|---|---|---|
| **Playnite** (`JosefNemec/Playnite`) | MIT, 14.4k★, pushed 2026-10-19, WPF desktop | `.iso .cso .pbp .chd` (`emulator.yaml`, `Platforms: sony_psp`) | **Automatic** — official docs: "Playnite by default groups multi-disc games under one game entry", split/merge in the right-click menu; `source/Playnite/Common/M3U.cs` parses `.m3u` incl. RetroArch's `:`/`\|` extension suffixes | **Metadata only** — `Jeshibu/PlayniteExtensions` ships `Metadata_LaunchBox.yaml` / `LaunchBoxMetadata` plugin. No LaunchBox **library** importer exists; the library itself is re-scanned |
| **SimpleLauncher** (`purelogiccode/SimpleLauncher`) | GPL-3.0, 266★, pushed **2026-10-30**, .NET 10 WPF + Avalonia desktop | `cso, chd, iso, pbp, elf, prx` (`docs/parameters.md`), PPSSPPWindows64.exe | **Deepest mechanics, least automatic** — `ChdMountStrategy` (19 emulators, virtual drive via bundled `CHDMounter`/Dokan), `ChdToCueStrategy`, `DiscConverter` (CHD→ISO, CHD→CUE/BIN, **PBP→CUE/BIN**), plus a per-system "Group Files by Folder" knob and `.m3u` pass-through. It **generates** no `.m3u` | No import path found — `search: LaunchBox` in the repo returns 0 hits |
| **ES-DE** (`ltusius/EmulationStation-DE`) | MIT, 507★, pushed 2026-10-26, Qt desktop | PPSSPP **standalone only**, PSP = "single disc image file" | **Manual** — USERGUIDE: the user builds `Game.m3u/` directories themselves; the `.m3u` generator is a separate third-party script. Multi-disc "just works" is not on offer | none |
| **OpenBoxGL** (`vindeckyy/OpenBoxGL`) | AGPL-3.0, 35★, Python | `.pbp .iso .cso` — **no `.chd`** (`emulator_defs/ppsspp-psp.yaml`) | Its `docs/PARITY.md` marks multi-disc M3U generation **done** — but see below | Tracks LaunchBox parity deliberately |

**OpenBoxGL is out on architecture, not on features.** Its own parity doc describes
"a server-computed capability contract", and the tree is `handlers/` + `static/` +
`cloud_sync.py` — it is a localhost web app, which is model B wearing a desktop
costume. Under the no-server ruling it cannot be the answer, and its PSP definition
missing `.chd` would have disqualified it anyway. **ES-DE is out on multi-disc**:
it requires hand-authored playlists, which is precisely the failure Brad named.

### Recommendation

**Playnite**, with **SimpleLauncher** as the challenger worth a second look.

- **Playnite** is the only candidate that satisfies every constraint from Brad plus
  the discriminator without manual work: Windows desktop app, no server, MIT,
  14,393 stars, `.iso/.cso/.pbp/.chd` for PSP, automatic multi-disc grouping, and a
  LaunchBox **metadata** plugin so the old library's data isn't lost. The honest
  caveat: Playnite's community extension repo has no LaunchBox *library* importer —
  the games get re-scanned from the ROM folders, the metadata gets pulled from
  LaunchBox.
- **SimpleLauncher** has the strongest raw disc machinery of anything checked —
  CHD mounting, CHD→ISO/CUE conversion, PBP→CUE/BIN — and it released hours ago.
  It costs more to adopt: GPL-3.0, small community, no metadata scraper beyond
  RetroAchievements and image packs, no `.m3u` generation, no LaunchBox import.
- **Third runner-up, for the couch**: `batocera.emulationstation`-style frontends
  are moot while the target is one Windows desktop.

**Card-018** now exists in `backlog` for the trial: install Playnite (and optionally
a SimpleLauncher portable build), point it at the PSP and PSX folders, and check the
multi-disc grouping and PPSSPP launch behaviour on real files. Nothing installs
without Brad's explicit approval — that is decision-002 and it still holds.

---

## 2026-11-01 — the trial ran: measured results, both candidates

Card-018 executed against Brad's real library, not a sample folder. Everything below
is measured output from the two portable copies under `F:\Lab\trials\`, with the apps
driven over Windows UI Automation and the results read back out of each app's own
database. Nothing was installed into the system and nothing was written outside
`F:\Lab` except the game processes' own behaviour.

### The library being tested

| Folder | Contents | Why it is the hard case |
|---|---|---|
| `E:\Sony\PSP` | **33 `.iso`** files | PSP image handling |
| `E:\Sony\PSX` | **52 `.chd`** files, **23 discs across 9 multi-disc sets**, named `Name (Disc 1).chd` / `Name (Disc 2).chd` | Multi-disc grouping |
| anywhere under `E:\Sony` | **zero `.m3u`** files | So a frontend that only understands playlists has nothing to work with — this is exactly the failure Brad named |

### The emulator route (decision-012)

Both frontends were pointed at Brad's **existing** `F:\RetroArch` install —
`retroarch.exe` plus the `ppsspp`, `swanstation`, `mednafen_psx_hw`, `pcsx_rearmed`
and `pcsx2` cores, and `system\psx` which already holds a complete BIOS set. No
portable PPSSPP/DuckStation download and no Dokan virtual-drive driver were needed.
`content_history.lpl` in that install proves Brad already launches these CHDs and
ISOs through RetroArch, so the trial only had to prove the *frontend* hands over the
right command line.

Two things found while auditing it, worth knowing:

- `system\psp` holds only `ppge_atlas.zim` — **no `flash0` firmware**. PPSSPP booted
  the real ISO anyway, but anything needing firmware (some homebrew, PSN titles)
  would need that copied in.
- `retroarch.cfg` has no `single_instance`, no `pause_on_window_lost_focus`, and
  `system_directory = ":\system"`. Because focus-pause is default-on, **an unfocused
  RetroArch window renders black** — a capture has to grab the window while it has
  focus, which is why the frame hashes below were taken with focus briefly held and
  then restored.

### Playnite 14.x — scan and launch

| Check | Measured result |
|---|---|
| Scan total | **71 new games / 76 total** |
| PSP | **33** — every ISO from `E:\Sony\PSP` |
| PSX | **38** from the 52 CHDs, and **all 9 multi-disc sets collapsed into one game entry each**, each entry holding a multi-entry `Roms` list |
| Artwork | IGDB auto-filled during the scan |
| Play tracking | `Playtime` and `PlayCount` written on the game record |
| Live PSP launch | **passed** — `playnite.log`: `ProcessStarter:Starting process: F:\RetroArch\retroarch.exe, -L ".\cores\ppsspp_libretro.dll" "E:\Sony\PSP\Grand Theft Auto - Chinatown Wars.iso"`, spawned pid, two focused frame captures hashed differently, then `Playtime 848` / `PlayCount 1` recorded |

Playnite's multi-disc semantics were read from `JosefNemec/Playnite` master rather
than assumed: `GamesEditor.cs:1716-1728` expands the stored action into **one play
action per ROM**, each named `<Game>: <Disc N>` — so the user picks the disc manually
and there is no automatic disc chaining. `GamesEditor.cs:450` shows plain **Play**
uses `Roms[0]`. `Common/M3U.cs` and `Emulators/Scanner.cs:869-875` only *consume*
`.m3u`; **Playnite never generates one**, which is fine here only because the sets
collapse into a single entry.

Two things cost it: the config UI is invisible to UI Automation (every element rect
came back `(,,0x0)`), so the trial's scanner configuration had to be written
**offline into its LiteDB while the app was stopped** (decision-013), and RetroArch
had to be registered through the emulator dialog before any scan could resolve.

### SimpleLauncher 5.8.4 — scan and launch

| Check | Measured result |
|---|---|
| Runtime | needed **.NET 10**, satisfied by a portable runtime at `F:\Lab\trials\dotnet10` launched via `DOTNET_ROOT` (decision-014) — not a system-wide install |
| Config | done through UIA directly: PSP `E:\Sony\PSP`, extensions `cso, chd, iso, pbp, elf, prx`, `-L "F:\RetroArch\cores\ppsspp_libretro.dll" "%ROM%"`; PSX `E:\Sony\PSX`, extensions `chd, cue, bin, img, mds, mdf, pbp`, swanstation core. Persisted in `settings.dat` (SQLite, table `Systems`) — no `system.xml` |
| PSP page | **33 tiles** |
| PSX page | **52 tiles** — every `Name (Disc N).chd` is **its own tile**. No collapse, no disc chaining, no generated `.m3u` |
| Artwork | only for auto-imported Steam titles; `images\Sony PSP` and `images\Sony PlayStation` stayed empty, so those tiles fall back to `images\default.png` |
| Live PSP launch | **passed** — UIA invoke on the tile spawned `"F:\RetroArch\retroarch.exe" -L "F:\RetroArch\cores\ppsspp_libretro.dll" "E:\Sony\PSP\Grand Theft Auto - Chinatown Wars.iso"`, window `RetroArch PPSSPP c1581e6`, focused capture showed the real PSP auto-save Notice screen, CPU rose 6.109 → 6.703 |
| Play tracking | after a graceful close, `PlayHistory` = 1 row (`TimesPlayed 1`, `TotalPlayTime 287`, `2026-11-01 03:53:48`) and `SystemPlayTimes` = `Sony PSP 287` |
| Per-tile menu | `Launch Game`, `Add To Favorites`, `Remove From Favorites`, `View Achievements`, `Open Video Link`, `Open Info Link`, `Open ROM History`, `Cover` — **no disc picker and no emulator picker** |

Brad set the launch-test scope to **PSP ISO only** (decision-015), so the multi-disc
PSX live launch was deliberately skipped; Playnite's multi-disc behaviour above is
source-level evidence plus scan evidence, not a played disc swap.

### Side by side, on Brad's two criteria

| | PSP images | Multi-disc | Artwork | Play history | What it costs |
|---|---|---|---|---|---|
| **Playnite** | 33/33 scanned | **23 discs → 9 entries**, one play action per disc, manual pick | auto via IGDB | `Playtime` / `PlayCount` | config UI unreachable to automation; needs offline DB writes |
| **SimpleLauncher** | 33/33 scanned | **52 separate tiles**, no grouping at all | none for non-Steam systems | `PlayHistory` / `SystemPlayTimes` seconds | needs a portable .NET 10 runtime; UIA works but per-system setup is manual |

**Verdict, on the discriminator Brad set:** Playnite passes it and SimpleLauncher
does not. SimpleLauncher has the better raw CHD machinery on paper (mount and
conversion strategies) but in the real folder it treats each disc as a separate game,
which is precisely the behaviour Brad rejected; Playnite folds his 9 sets into 9
entries and still lets him choose a disc per launch. Both proved they can actually
boot a PSP ISO through his existing RetroArch, and both track playtime.

**Honest leftovers:** SimpleLauncher's per-disc tiles are only cosmetic if he adds a
"Gaming system" grouping or renames the files; Playnite's collapse means the second
disc is reachable only through the `<Game>: <Disc N>` play action, and neither app
produces a `.m3u` for RetroArch. Playnite's trial database has a restore backup at
`F:\Lab\trials\plbak\`; SimpleLauncher's store is `F:\Lab\trials\simplelauncher\settings.dat`
with a pre-run backup beside it. `F:\RetroArch` itself was left untouched, and both
trial apps and every trial game window are closed.

---

## Disposal and corrections (2026-11-01, after the trial closed)

Brad answered the "what happens to `F:\Lab\trials\`" question with **"delete what doesn't
matter"**, so this entry states what was kept, what was removed, and what the two
paragraphs above got wrong. Nothing above is rewritten.

### Corrections to what was written above

1. **`F:\Lab\trials\plbak\` never existed.** Brad has no installed Playnite
   (`C:\Users\sardw\AppData\Roaming\Playnite` does not exist), so there was no library of
   his to back up and nothing of his was ever at risk. The sentence claiming a restore
   backup at `plbak\` is false.
2. **SimpleLauncher persists no game list.** Its `settings.dat` is SQLite with tables
   `Meta`, `AppSettings`, `EmulatorSettings`, `Favorites`, `PlayHistory`, `Systems`,
   `SystemPlayTimes` — none of them holds a game or a metadata field. Tiles are re-derived
   by scanning `SystemFolders` at startup, so the 33 PSP and 52 PSX tiles are UI-side scan
   results, not stored state. The trial added exactly two rows: `PlayHistory`
   (`GTA - Chinatown Wars`, `TimesPlayed 1`, `TotalPlayTime 287`) and
   `SystemPlayTimes` (`Sony PSP` 287).
3. **Playnite's per-disc grouping is confirmed in the DB, not just in the UI.** Joining
   `games.db` against `platforms.db`, `emulators.db`, `sources.db` and `scanners.db` gives
   76 `Game` documents: 33 with PSP roms, 38 with PSX roms holding all 52 disc files, 9 of
   those entries holding more than one disc (histogram `{1: 29, 2: 6, 3: 1, 4: 2}`), and 5
   Steam imports. All 85 rom paths resolve to real files. `MergeRelatedFiles: true` is the
   setting that does it; the PSP folder is bound to the builtin PPSSPP profile and the PSX
   folder to Beetle PSX HW, both through `F:\RetroArch`.
4. **Metadata that Playnite imported on its own**, out of 76 entries: description 74,
   release date 74, genre 73, publisher 72, developer 71, series 66, links 70 — and
   `Image` set on **0**, so artwork is still a separate job. SimpleLauncher stores no
   metadata fields at all for non-Steam systems. Playtime on the 5 Steam entries is
   inherited from Steam, not measured here.
5. **`F:\RetroArch` was not edited, but RetroArch wrote about itself.** Launching a game is
   enough for it to rewrite `retroarch.cfg` (11-01 03:49), append to
   `playlists\builtin\content_history.lpl` (11-01 02:44) and create
   `playlists\logs\PPSSPP\Grand Theft Auto - Chinatown Wars.lrtl` (11-01 02:58). That is
   RetroArch's normal behaviour on exit, not a trial setting: no core, BIOS, firmware or
   save file was added, changed or removed, and `pause_on_window_lost_focus` is still unset
   (default on). `E:\Sony` really is untouched — no file there has been written since
   2026-10-31, and the roms were read only.

### What was kept

`F:\Lab\trials\evidence\` — 25 files, 2.2 MB, SHA256-listed in
`F:\Lab\trials\evidence\MANIFEST.txt`: the Playnite databases and their plain-text dumps,
Playnite's log and config, SimpleLauncher's before/after stores and the table diff, the
artwork tree listing, the measurement summaries, and the four scripts that produced them so
the numbers can be re-derived. `F:\Lab\trials\` is gitignored, so the evidence is
deliberately **untracked**; it lives on disk and on the local dashboard, not on GitHub.

### What was deleted

`F:\Lab\trials\dl` (368 MB of installers), `F:\Lab\trials\dotnet10` (172 MB portable .NET
10 runtime), `F:\Lab\trials\playnite` (707 MB app tree), `F:\Lab\trials\simplelauncher`
(548 MB app tree) — 1,794 MB removed, all re-downloadable. No process was still running
from `trials\` when they were deleted.

### The decision still Brad's to make

The verdict stands: **Playnite passes the PSP + multi-disc discriminator, SimpleLauncher
does not.** Adopting it for real — installing it and importing his LaunchBox metadata — is
Brad's call, not a consequence of the trial.
