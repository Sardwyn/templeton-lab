---
id: fact-vram-single-writer
kind: fact
key: vram-constraint-single-writer
updated: 2026-10-29T02:35
confidence: high
---

**Hardware fact (Brad, 2026-10-29):** qwen's model takes most of the box's
VRAM, so no other local agent can run alongside it. Consequence for the org:

- qwen is the **only agent that checks in directly** — single-writer org.
- copilot / cursor / grokbot / opencode are **dispatch-only**: stateless
  sessions, fresh brief via `worker/brief.py`, result lands as files + events
  at qwen's next check-in. No cloud heartbeats, nothing to flag stale.
- Implication for design: prefer least-frictionless operation; don't build
  multi-writer machinery before there is actual traffic.

Ruling: org/decisions/2026-10-29-single-writer-dispatch.md (decision-005).
