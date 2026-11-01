---
id: lesson-rendered-page-vs-record
kind: lesson
key: rendered-page-is-not-the-record
updated: 2026-11-01T06:50
supersedes: []
confidence: high
---

Two mistakes made in one debug session on the dashboard (2026-11-01), both
about trusting a *rendered* thing as if it were the *record*:

1. **A page in a browser is not the generated file.** I reported that a `push`
   event was missing from the dashboard Events pane. It was present in the
   HTML and in the log; the tab was stale browser cache (`serve.py` rebuilds
   the dashboard per request and sends `Cache-Control: no-store`), and my probe
   searched for a commit SHA the ref column never prints. Check the generated
   file first, then the served DOM with a fresh URL, before claiming a record
   is missing.
2. **A raw-string regex has one escape level, not two.** `LINK_RE` was written
   `r"F:\\\\Lab\\\\[\w.\-\\]+"`, which requires TWO literal backslashes, so
   prose paths like `F:\Lab\org\cards\card-018.md` never matched; the
   basename branch then matched the tail and printed a wrong label
   (`F:\Lab\card-018.md`). Fix: `r"F:\\Lab\\(?:[\w.\-\\]*[\w\\])?"`. Test the
   generator function on sample strings before reporting a render rule works.

Related mechanics learned: a directory token is not a missing file —
`ref_cell` now renders `F:\Lab\trials\evidence\` as `.dir`, and `win_path`
strips an existing `F:\Lab\` prefix instead of doubling it. A label rule needs
the file index to contain the file, so gitignored evidence under `trials\` is
now in `INDEX_DIRS` (it links on the local dashboard, not on GitHub Pages).
