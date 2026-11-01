---
id: decision-012
kind: decision
key: 012
updated: 2026-11-01T04:05
supersedes: []
confidence: high
---

Brad ruled on 2026-10-31 (filed 2026-11-01): the retro trial reuses his existing F:\RetroArch install (ppsspp, swanstation, mednafen_psx_hw, pcsx_rearmed, pcsx2) instead of shipping portable PPSSPP/DuckStation, so no Dokan driver was ever needed and F:\RetroArch stays read-only. Facts found there: system\psx has a complete BIOS set, system\psp has only ppge_atlas.zim and NO flash0 firmware, retroarch.cfg has no single_instance and no pause_on_window_lost_focus (default-on, so an unfocused RetroArch window renders black).
