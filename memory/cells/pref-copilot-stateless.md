---
id: pref-copilot-stateless
kind: preference
key: copilot-temporal
updated: 2026-10-15T04:10
supersedes: []
confidence: high
---

Copilot is not temporally aware — it has no memory between sessions and that
is a known problem Brad is trying to alleviate with the org. Rule: every
handoff to Copilot (and any cloud agent) carries a fresh brief
(`python worker/brief.py copilot`) so the org's date/board/events state is its
memory. Never assume Copilot remembers anything.
