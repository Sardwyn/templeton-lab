---
id: decision-012
date: 2026-10-31
status: active
title: The retro trial reuses Brad's existing RetroArch instead of shipping emulators
decided_by: brad
---

# Decision-012: The retro trial reuses Brad's existing RetroArch instead of shipping emulators

**Ruled by Brad on 2026-10-31**, when asked how the trial should get an emulator:
download portable PPSSPP and DuckStation into `F:\Lab\trials\`, or point the two
frontends at the `F:\RetroArch` install he already has. He chose his existing
RetroArch.

## The rule

1. **The trial's emulator is `F:\RetroArch`** — `retroarch.exe` and its cores
   (`ppsspp`, `swanstation`, `mednafen_psx_hw`, `pcsx_rearmed`, `pcsx2`). Frontends
   are configured to launch through it, not through a bundled standalone emulator.
2. **No emulator payloads inside `F:\Lab\trials\`.** The trial only carries the
   frontends and their own data. `F:\RetroArch` is read, not rewritten: its config,
   cores and BIOS folders stay as Brad left them.
3. **No virtual-drive driver.** SimpleLauncher's CHD mounting path wants Dokan;
   pointing its PSX system at the `.chd` files through a RetroArch core needed no
   driver at all, so nothing was installed at the system level.

## Why

The trial is meant to judge the *frontend*, and Brad's launch behaviour already runs
through RetroArch — his `content_history.lpl` shows the same CHDs and ISOs launched
that way. Adding a second emulator would have tested the emulator instead, and would
have put another install inside the trial boundary for no signal.

## Consequence

- The measured command lines in the trial are the real ones:
  `"F:\RetroArch\retroarch.exe" -L "F:\RetroArch\cores\ppsspp_libretro.dll"
  "E:\Sony\PSP\Grand Theft Auto - Chinatown Wars.iso"` — recorded in
  `F:\Lab\org\notes\retro-game-library-options.md`.
- Two facts about that install are now on record and matter later: `system\psx` has
  a complete BIOS set, and `system\psp` has **no `flash0` firmware** (only
  `ppge_atlas.zim`), so firmware-dependent PSP content would need it copied in.
- Because `retroarch.cfg` has no `single_instance` and `pause_on_window_lost_focus`
  is default-on, an unfocused RetroArch window renders black; any evidence capture
  has to hold focus briefly and restore it.
