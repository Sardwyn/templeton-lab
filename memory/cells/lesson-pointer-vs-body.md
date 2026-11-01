---
id: lesson-pointer-vs-body
kind: lesson
key: pointer-vs-body
updated: 2026-11-01T07:02
supersedes: []
confidence: high
---

A reference field is not a description field. In F:\Lab\org\events\*.jsonl, `file`/`card`/`cell`/`decision` are pointers and `note`/`message` are the event's own prose - the dashboard originally read `note` as the pointer, so every `note` row showed its body in the REF column and a body starting with "card-018" was dressed up as a path (F:\Lab\card-018 trial results recorded...). Rule now in F:\Lab\worker\dashboard.py: a token only becomes a path when it is one token with no whitespace; prose is printed as written; dim is reserved for a file that genuinely does not exist; event text follows the pointer link in muted type (.det). A bare filename resolves to the single file carrying that name (dashboard.py -> F:\Lab\worker\dashboard.py) and stays unresolved when the name is ambiguous.
