---
id: decision-001
date: 2026-10-14
status: active
---

# Roster, identity, and HQ (CEO rulings)

Ruled 2026-10-14 by the human (CEO):

1. **qwen** is the local agent on this box — the **only** local agent, and the
   main executor. All local work (builds, tests, box maintenance) routes through qwen.
2. **copilot** is cloud (architect/coordinator). **cursor**, **grokbot**, and
   **opencode** are cloud agents (cursor operates via the IDE).
3. Agents are not mapped or registered beyond this roster without a further
   human ruling.
4. **F:\Lab** is org HQ. Live dashboard: `http://localhost:8901`
   (`python F:\Lab\worker\serve.py`). Plain-text board: `F:\Lab\state\BOARD.md`.
5. Card IDs are permanent; one file per artifact; history is immutable —
   corrections are new entries, never deletions.
