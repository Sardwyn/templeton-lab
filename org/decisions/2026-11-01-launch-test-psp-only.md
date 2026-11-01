---
id: decision-015
date: 2026-11-01
status: active
title: Launch testing on the real library is limited to a PSP ISO
decided_by: brad
---

# Decision-015: Launch testing on the real library is limited to a PSP ISO

**Ruled by Brad on 2026-11-01**, when asked how far to take the live launch test
against his own games. He chose **PSP ISO only**, and explicitly skipped the
multi-disc PSX live launch.

## The rule

1. **One live launch per frontend, on a PSP ISO.** Grand Theft Auto - Chinatown Wars
   (`E:\Sony\PSP`) is the probe: it boots, it is unambiguous, and the spawned command
   line shows exactly what the frontend hands to the emulator.
2. **No multi-disc live launch.** Disc-swapping inside a real PSX session is not
   tested. Multi-disc behaviour is judged from what each frontend **does to the
   library at scan time**, plus its own source, not from a playthrough.
3. **Keep the trial windows separate from Brad's.** His OpenCode window occupies
   `260,260x2580x1029`, so trial captures target the trial app's own rect only, and
   focus is briefly held on a game window and then restored.

## Why

The discriminator Brad set is whether a frontend handles multi-disc games without him
hand-building playlists, and that is answered by what the scan produces: Playnite
folds 23 discs into 9 entries, SimpleLauncher makes 52 separate tiles. Watching a disc
swap add nothing to that judgement, while launching his PSX games for real would have
touched saved-state files and burned time on a point already settled by the scan.

## Consequence

- Playnite's per-disc play actions (`<Game>: <Disc N>`, from `GamesEditor.cs:1716-1728`)
  and plain-Play using `Roms[0]` (`GamesEditor.cs:450`) are recorded as **source-level
  evidence**, and the note says so rather than claiming a verified disc swap.
- Both live PSP launches passed, so the emulator handoff is proven for both
  candidates; the multi-disc verdict rests on scan output plus source, which the note
  labels honestly.
- If Brad later wants the disc-swap behaviour proven by play, that is a new trial with
  its own approval — it needs a PSX session he is willing to have started.
