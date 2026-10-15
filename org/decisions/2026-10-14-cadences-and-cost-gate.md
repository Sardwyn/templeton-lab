---
id: decision-003
date: 2026-10-14
status: active
---

# Agent cadences and cost gate (CEO rulings, 2026-10-14 ~07:25)

1. **qwen** is the daily driver and main workhorse (local, always
   available). Folded into architectural decisions, but high-level calls
   still route to Copilot until qwen's limits are known.
2. **Copilot** is cloud and stateless — not temporally aware. Mitigation:
   every handoff carries a brief (`worker/brief.py`); the org's
   date/board/events state is its memory.
3. Paid agents are **cost-gated** — activation requests route through the
   CEO with scope attached:
   - **cursor** — ~weekly, big Unreal Engine project work
   - **grokbot** (+ team) — ~1 week in every 4 (sprint)
   - **opencode** — ~2 weeks in every 4
4. Agents don't spend, agents ask (ping protocol, SOP v1.1).
