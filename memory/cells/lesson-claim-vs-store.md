---
id: lesson-claim-vs-store
kind: lesson
key: claims about an app must be proven by its own store
updated: 2026-11-01T06:25
supersedes: []
confidence: high
---

Two false claims survived card-018's first write-up and were only caught after dumping the apps' own databases: "Playnite's artwork is auto-filled" (`Image` was set on **0 of 76** entries) and "SimpleLauncher stores 33 PSP / 52 PSX games" (its SQLite has no game table at all - tiles are re-scanned from `SystemFolders` at startup). Both came from what the UI appeared to do, plus what upstream source suggested, rather than from what the app actually persisted.

Rule: when reporting what a tool did to Brad's data, dump the tool's own store and join it before writing the number - LiteDB/SQLite dumps plus one join script is ~60 lines and 2.2 MB, and it turns a plausible story into evidence. UI-side results (tiles, previews, generated candidates) are not state. When a claim turns out wrong, correct it as a new dated section that names the wrong sentence, and never rewrite the original text (history is immutable).
