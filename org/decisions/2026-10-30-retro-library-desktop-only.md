---
id: decision-009
date: 2026-10-30
status: active
title: Retro game library is a Windows desktop app, no server; RomM is out
decided_by: brad
---

# Decision-009: Retro game library is a Windows desktop app, no server; RomM is out

**Ruled by Brad on 2026-10-30**, answering the three scoping questions in
`org/notes/retro-game-library-options.md`:

> "The current one are Pegasus, LaunchBox. It's for WINDOWS. RomM is a nogo, it
> struggles with PSP and Discs in general"

## The ruling

1. **Target platform is Windows desktop.** Not the Steam Deck, not Android
   handhelds, not a living-room box. Anything whose main value is being reachable
   from several devices is out of scope.
2. **Desktop app, not a self-hosted server.** The library is one program Brad runs
   on the machine the games live on. No Docker, no always-on host, no web UI.
3. **RomM is excluded**, on Brad's own experience: it struggles with PSP and with
   discs in general. By extension, model B (RomM, Gaseous) is off the table, and so
   is anything architecturally equivalent to it.
4. **PSP and multi-disc handling is the discriminator.** The incumbent tools fail
   there, so whatever replaces them must do PSP images and multi-disc games well —
   that requirement outranks artwork, scraper quality and UI polish.

## Why

The point of replacing Pegasus and LaunchBox is that disc-based systems are
mishandled today. A frontend that fixes browsing but repeats the disc problem is
not a replacement. A server also adds a second thing to administer on a machine
that already runs the emulators, and Decision-002 already says nothing gets
installed without Brad approving it.

## Consequence

- `org/projects/retro-game-library.md` is scoped to a Windows desktop app; RomM and
  Gaseous are no longer candidates.
- The shortlist is **Playnite** (MIT, desktop, automatic multi-disc grouping, PSP
  `iso/cso/pbp/chd`, LaunchBox metadata plugin) and **SimpleLauncher** (GPL-3.0,
  desktop, deepest CHD/disc conversion machinery), with **ES-DE** and
  **OpenBoxGL** ruled out — ES-DE needs hand-authored `.m3u` playlists, and
  OpenBoxGL is a localhost web app, which the no-server ruling excludes.
- **card-018** exists in `backlog` to trial Playnite on the real PSP/PSX folders.
  It cannot start until Brad approves an install.
