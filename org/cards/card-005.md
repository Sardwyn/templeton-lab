---
id: card-005
title: worker/lattice.py — YAML task-graph runner
column: done
assignee: qwen
project: mulattice
depends_on: ["card-002"]
created_at: 2026-10-14T06:45
updated_at: 2026-10-15T03:15
---

Implement a minimal interpreter for mLattice/tasks/*.yaml: typed steps
(shell | python), inputs/outputs, failure handling. Wire up
build_pipeline.yaml: run worker/run_build.py --target <repo>, capture
exit code + log, record result into org/builds/ (frontmatter: id, target,
agent, status pass|fail, ts) and append org/events/. This makes the
scaffolded pipeline real: any agent can trigger a build and the org
records it.

## Delivered (2026-10-15)

- worker/lattice.py — YAML task-graph runner (PyYAML if present, built-in
  subset parser otherwise — the box's pip is broken, so zero-dep matters).
- worker/run_build.py — target registry (selftest, mulattice-tests),
  log capture, records via worker/apply.py.
- worker/apply.py — record_build_event(): canonical build recorder
  (org/builds/build-YYYYMMDD-NNN.md + events), append_event().
- Pipeline live: build-20261015-001 selftest PASS; -002 mulattice-tests
  FAIL (cp1252 encoding — real, correctly recorded); -003 mulattice-tests
  PASS after PYTHONIOENCODING fix. Failures stop the pipeline and are
  recorded; that's the system working as designed.
