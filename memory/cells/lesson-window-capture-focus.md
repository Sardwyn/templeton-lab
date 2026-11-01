---
id: lesson-window-capture-focus
kind: lesson
key: window-capture-focus
updated: 2026-11-01T04:05
supersedes: []
confidence: high
---

Proving a game actually ran, on Windows, without disturbing the user: capture the emulator window's own client rect (GetClientRect + ClientToScreen, never a downscaled screenshot), hash two frames a few seconds apart, and check the process CPU delta. Two traps found on 2026-11-01. (1) Get-FileHash -InputStream on a MemoryStream returns the empty-stream hash E3B0C442... unless $ms.Position = 0 is set first - identical "hashes" there were a bug, not a static screen. (2) RetroArch defaults pause_on_window_lost_focus to ON, so an unfocused window is black with CPU delta 0; a capture must SetForegroundWindow on the trial window, shoot, then restore the previous foreground. A genuinely static screen (a paused save-notice) can hash the same twice while CPU still rises - read the pixels, not just the hash, and never claim the user's own window rect as the trial's.
