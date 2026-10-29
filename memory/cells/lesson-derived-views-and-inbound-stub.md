---
id: lesson-derived-views-and-inbound-stub
kind: lesson
key: derived-views-are-not-sources
updated: 2026-10-29T02:35
confidence: high
---

Two traps found while doing a real check-in on 2026-10-29:

1. **Generated views go stale silently.** `state/BOARD.md`,
   `transport/outbound/state.json`, `state/BRIEF.md`, `dashboard/index.html`
   are *derived*, not sources. On 15 Oct they were ~19h stale and looked like
   real state. Fix: regenerate `sync.py` + `dashboard.py` + `brief.py` at every
   check-in (SOP v1.4 step 5); card files are the only board truth.
2. **`sync.py::apply_inbound()` is a stub that deletes `updates.json` without
   applying it** — a cloud agent's dropped update would vanish silently.
   Card-013 owns the real inbound parser. Don't trust the transport folder to
   preserve anything.

Also: `apply.py::append_event(agent, type_, **ctx)` takes only two positional
args — extra context must be keyword args.
