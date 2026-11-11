---
id: ue-baebattles
title: Baewatch (UE 5.8; includes Bae Battles card game)
status: active
owner: brad
repo:
path: D:\Unreal Projects\Baewatch
memory_cell: project-ue-baebattles
updated_at: 2026-11-11T01:02
---

**What it is:** Baewatch, Brad's Unreal Engine 5.8 project. It includes the
Bae Battles card game. About 70k lines across 219 C++ files: beach sim,
missions, C++ UMG UI, Kimodo motion via Kimo, and Foil art. Not on GitHub.
Engine is `D:\Engines\UE_5.8`. The project tree is
`D:\Unreal Projects\Baewatch`.

**Where we're at:** active again on 2026-11-11. The previous entry called this
a parked UE 5.7 project at `C:\Users\sardw\UE_Projects\UE_BAEBattles` and tied
it to card-011. That was wrong. card-011 is the memory-audit card and is now
tagged `templeton-lab`. The id stays `ue-baebattles` so existing links still
resolve.

## State at restart (2026-11-11)

- Last activity 2026-08-16.
- Map1 tycoon HUD reskin is half-done. After a rebuild the overlays are
  stacked, the weather plate is too wide, the chip icons are squashed, the
  dialogue chrome is misaligned, and HQOperationsWidget is still navy.
- Aug 13 C++ audit: about 32 claimed bugs, most confirmed, not mass-fixed.
  The list lives on Brad's PC.
- Bae Battles 3-lane life TCG combat is deliberately parked.
- Kimodo walk, 12 idles, and sit/lie are done, awaiting PIE confirm.

**Next:** card-023 is the boot and smoke test (Brad, once Brad-Actual
reconnects). card-024 finishes the Map1 HUD chrome and then the HQ widget.
card-025 confirms the Kimodo idles in PIE. card-026 recovers the Aug 13 list
and picks a short P0 set. No mass-fix.
