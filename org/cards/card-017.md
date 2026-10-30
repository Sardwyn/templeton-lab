---
id: card-017
title: Research frontend/library options to replace Pegasus and LaunchBox
column: done
assignee: qwen
project: retro-game-library
depends_on: []
created_at: 2026-10-30T01:35
updated_at: 2026-10-30T01:51
---

**Done — findings are in `org/notes/retro-game-library-options.md`.** Research
only: nothing installed, no direction chosen (that's Brad's call).

Checked 12 live candidates against GitHub for maintenance signal, latest release,
license and platforms, and confirmed why the two incumbents are out:
Pegasus's own site can't report its latest version and its newest release tag is
`weekly_2024w38` (2024-10-05); LaunchBox's base is free but the Big Box mode is a
paid unlock and its changelog gates features behind a lock mode.

Two findings worth Brad's attention before he chooses:
- **RomM** can import LaunchBox metadata directly (IGDB / ScreenScraper /
  LaunchBox / MobyGames), so the existing library isn't stranded.
- **Daijishō** looks open-source by its repo badge but the README says it is
  currently **closed-source**; the repo is assets + issue tracker only.

**Next:** needs Brad's answers to the three questions in the note (target device,
desktop launcher vs self-hosted server, whether a build-our-own path is allowed)
before any trial build gets scheduled.
