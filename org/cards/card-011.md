---
id: card-011
title: Memory write guarantees — explicit trigger, proof, audit
column: done
assignee: qwen
project: ue-baebattles
depends_on: ["card-010"]
created_at: 2026-10-15T11:20
updated_at: 2026-10-16T02:57
---

Brad: "how do we SPECIFICALLY ensure something is written to your memory?"
The write path must not depend on judgment alone. Deliver:
1. worker/memory_audit.py — cell integrity (parse, unique ids, valid kinds,
   supersedes resolvable) + coverage (every org/decisions/ ruling must be
   reflected in memory) + freshness (last memory_write, oldest cells).
2. Protocol: explicit trigger ("remember: X" / "standing pref") -> immediate
   cell + PROOF (cell content, path, event). No verbal ack without artifact.
3. Close coverage gaps the first audit finds.

## Delivered (2026-10-16)

- worker/memory_audit.py — integrity (parse, unique ids, valid kinds,
  supersedes refs) + coverage (every decision reflected in memory) +
  freshness. First run found 2 real gaps (decision-002, decision-004);
  closed both; re-audit clean: 19 cells, all 4 decisions covered, PASS.
- Protocol: explicit trigger ("remember: X" / "standing pref") -> immediate
  cell + proof; standing prefs also to core.md. SOP v1.4 + core.md updated.
