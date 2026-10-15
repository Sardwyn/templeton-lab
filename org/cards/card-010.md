---
id: card-010
title: Session definition + incremental memory writes
column: done
assignee: qwen
depends_on: ["card-009"]
created_at: 2026-10-15T11:05
updated_at: 2026-10-15T11:10
---

Brad asked how "session" is defined — he keeps Qwen loaded in VRAM until he
needs to free it, so a session can span hours or a day. Ruling encoded:
session = one chat OR one continuous task (whichever ends first); new chat =
full recall, truncated context = re-hydrate; VRAM residency != on-duty;
memory writes are INCREMENTAL (when learned), session end = consolidation
only. SOP v1.3, core.md updated, pref-session-definition cell written.
