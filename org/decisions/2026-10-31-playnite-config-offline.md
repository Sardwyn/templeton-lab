---
id: decision-013
date: 2026-10-31
status: active
title: Configure UI-invisible desktop apps offline while they are stopped
decided_by: qwen
---

# Decision-013: Configure UI-invisible desktop apps offline while they are stopped

**Set by qwen on 2026-10-31** while driving the card-018 trial, inside the scope Brad
approved (`F:\Lab\org\decisions\2026-10-31-decisions-tab.md`: portable copies under
`F:\Lab\trials\`, nothing installed into the system). Filed because it is a method
rule that will recur, not a one-off trick.

## The rule

1. **Probe the config UI with UI Automation before relying on it.** If every element
   comes back with an empty rect `(,,0x0)`, the app's configuration surface is not
   reachable by automation and clicking it is not an option.
2. **Then write the configuration offline, with the app stopped**, into the app's own
   store, and restart it to confirm the app accepted the edit. Playnite's store is
   LiteDB (`library\scanners.db`, `library\games.db`); the scanner config was written
   there and the subsequent scan proved it took.
3. **Back up before editing.** A restore copy sits in `F:\Lab\trials\plbak\` before
   any offline write, and the backup is kept after the trial.
4. **Do not generalise it.** SimpleLauncher's UI *is* UIA-visible, so its systems were
   configured by clicking, not by editing `settings.dat`. Offline writes are the
   fallback for invisible UI, never the default.

## Why

The trial has to produce real evidence about how a frontend behaves on Brad's library.
If the only way to configure it is a UI that cannot be driven, then editing the app's
own database while it is stopped is the only way to reach a configured state without
asking Brad to click through dialogs, and the app's own subsequent scan is the proof
that the edit was valid rather than corrupt.

## Consequence

- Playnite's scanner settings (`GameScannerConfig`, `GameScannersSettings` in
  `scanners.db`) are trial-written offline; everything measured after that point came
  from the app itself.
- LiteDB facts worth keeping: collection names are CLR type names (`Game`, `Platform`,
  `Emulator`, `GameScannerConfig`), game records carry `PlatformIds` and `Roms`
  (`{Name, Path}`) and `Playtime`/`PlayCount`, `CrcExcludeFileTypes` defaults to
  `["*.chd"]`, and `BsonDocument` has no `Contains(string)` — test `$doc.Keys -contains $k`.
- An offline write is only evidence about the app if the app is stopped and then
  restarted; an edit made while it runs gets overwritten on exit.
