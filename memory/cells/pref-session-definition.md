---
id: pref-session-definition
kind: preference
key: session-definition
updated: 2026-10-15T11:10
supersedes: []
confidence: high
---

Brad keeps Qwen **loaded in VRAM until he needs to free it** — a "session" can
span hours or a day, not one task. Consequences (ruled 2026-10-15):
- Session = one chat conversation OR one continuous task, whichever ends
  first. New chat = full recall. New task in the same chat = light recall
  (full recall again if the context window truncated — that's partial
  amnesia; re-hydrate).
- **Memory writes are incremental**: write the cell WHEN learned (a
  preference, lesson, or project change), never batched to "session end."
  Session end is consolidation only (core.md check, commit, heartbeat).
- VRAM residency is NOT "on-duty": loaded-and-idle = off-duty. on-duty
  means actively working. A long idle chat going STALE is correct.
