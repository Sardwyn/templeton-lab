---
id: decision-013
kind: decision
key: 013
updated: 2026-11-01T04:05
supersedes: []
confidence: high
---

Method rule set 2026-10-31 while driving the card-018 trial: probe an app's config UI with UI Automation first; if every element rect comes back (,,0x0) the UI is unreachable, so write the configuration offline into the app's own store while it is STOPPED, back it up first, then restart and let the app's own behaviour prove the edit took (Playnite's scanners.db / games.db are LiteDB 4.1). Do not generalise it - SimpleLauncher's UI is UIA-visible, so it was configured by clicking.
