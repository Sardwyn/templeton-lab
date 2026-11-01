---
id: project-templeton
kind: project
key: templeton
updated: 2026-11-01T06:47
supersedes: []
confidence: high
---

**Templeton Systems** — the org on F:\Lab (HQ, GitHub: Sardwyn/templeton-lab, public). Agents = departments; qwen is the sole local writer, cloud agents dispatch-only. Board as of 2026-11-01T06:45: 16 cards done, 3 open — card-013 (inbound parser, parked until a real cloud dispatch), card-016 (swarm rebuild, needs Brad's spec per decision-008), card-019 (second-order read-through, waits on Brad's stage-0 sign-off, untracked). Live dashboard http://localhost:8901 has Projects, decisions (decision-011) and event panes; decision-010's full-path link rule was enforced on 2026-11-01 — LINK_RE in worker/dashboard.py was double-escaped so prose paths never linkified, and the fix also made directories render as paths, indexed trials\ evidence, and linked push refs to the commit they pushed. Protocol v1.6 in org/playbooks/check-in.md. The Lattice = Qwen's memory (memory/core.md + 44 cells, recall.py read / remember.py write) + the org build pipeline (mLattice/tasks, card-005).
