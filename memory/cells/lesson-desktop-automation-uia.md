---
id: lesson-desktop-automation-uia
kind: lesson
key: desktop-automation-uia
updated: 2026-11-01T04:05
supersedes: []
confidence: high
---

Driving Windows desktop apps through UI Automation (uia.ps1: tree/sub/find/invoke/select/type/value/expand/toggle -Pid0 -Name/-Id/-Class -Filter -Index -Depth -Wait). What was learned on the card-018 trial: an app's whole config UI can be invisible to UIA (Playnite returned every rect as (,,0x0)), which means clicking is impossible and config must go offline into the app's store while it is stopped. Other traps: apps can render popups far outside the window (SimpleLauncher's context menu appeared at x 4193 on a window at x 260, and it self-dismisses, so read the tree in the same call sequence), controls often carry no AutomationId so match on Class and rect size (SimpleLauncher game tiles are ~300x300, side buttons only identifiable by -Class Button), and a system page can show its games only after invoking a "Filter by All" button. Invoke a tile to launch a game, then read back the spawned process's command line - that is the honest evidence of what the frontend hands to the emulator.
