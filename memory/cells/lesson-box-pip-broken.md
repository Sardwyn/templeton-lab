---
id: lesson-box-pip-broken
kind: lesson
key: box-pip
updated: 2026-10-15T04:10
supersedes: []
confidence: high
---

This box's **system pip is broken** (Python 3.12 at C:\Program Files\Python312:
`pip._vendor.rich.console` missing; ensurepip doesn't repair it). Don't fight
it: prefer zero-dependency code (built-in parsers) or use a venv's python
(e.g. C:\Users\sardw\mLattice\.venv). I added a built-in YAML-subset parser to
worker/lattice.py for exactly this reason.
