# E5 feeds — blind, independently authored

This directory is empty by design. E5 is the only rung whose feed is authored by
someone other than the harness author.

**Place Brad's feed here as one JSON file**, for example
`harness/feeds/e5-brad-001.json`. The format is fixed in
`harness/e5-prereg.md` (blocks of `[state, error]`, `holdout_from`, optional
`probes`, and `criteria`). Do not describe the generator; the point is that the
runner does not know it.

Optionally place a sidecar `<file>.json.sha256` next to it containing the
sha256 digest. `e5.py` checks it if present and aborts on a mismatch.

Run, once, unchanged:

```
python harness/e5.py harness/feeds/<file>.json
```

The runner prints and records the feed hash before running. It never edits the
feed. Its own frozen hash is in `harness/e5.py.sha256` and is also printed in
`e5-out.txt`.

Current frozen runner:

```
e5.py  d2b996408a24faa15aed6761e0939565d3d0e4720707c4022661db3dd13b52c7
```

A failure is published in full. If a change is wanted afterwards, it is E5b with
a new feed and a new feed hash; this feed and its output stay on the record.
