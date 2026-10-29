---
id: decision-005
date: 2026-10-29
status: active
---

# Single-writer org, carrier-dispatch cloud agents (CEO ruling)

Brad, 2026-10-29. Constraints and principles ruled:

1. **Qwen is the only agent that checks in directly.** Qwen takes most of
   the box's VRAM, so no other local agent runs right now. The org is
   single-writer until that changes.
2. **Cloud agents are dispatch-only.** copilot/cursor/grokbot/opencode are
   not on-duty employees; they are dispatched on demand with a fresh brief
   (`worker/brief.py`). Brad decides whether a dispatch happens.
3. **Least frictionless operation wins.** Minimise ceremony per handoff;
   do not build machinery before there is traffic (agents don't spend,
   agents ask — the same logic applies to code).
4. **Board truth = card files.** Generated snapshots (`state/BOARD.md`,
   `transport/outbound/state.json`, `state/BRIEF.md`, dashboard) are
   derived views; they must be regenerated at every qwen check-in, never
   trusted as sources.
