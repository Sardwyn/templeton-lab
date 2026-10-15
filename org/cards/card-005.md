---
id: card-005
title: worker/lattice.py — YAML task-graph runner
column: backlog
assignee: unassigned
depends_on: ["card-002"]
created_at: 2026-10-14T06:45
updated_at: 2026-10-14T06:45
---

Implement a minimal interpreter for mLattice/tasks/*.yaml: typed steps
(shell | python), inputs/outputs, failure handling. Wire up
build_pipeline.yaml: run worker/run_build.py --target <repo>, capture
exit code + log, record result into org/builds/ (frontmatter: id, target,
agent, status pass|fail, ts) and append org/events/. This makes the
scaffolded pipeline real: any agent can trigger a build and the org
records it.
