---
id: lesson-serve-query-string-404
kind: lesson
key: serve-query-string-404
updated: 2026-10-31T03:59
supersedes: []
confidence: high
---

serve.py matched self.path verbatim, so any ?v= query string 404d with an empty body - a browser tab pointed at /?v=1 rendered a 39-char empty document that looked like the dashboard had no content at all. Routes now strip the query string and fragment before matching. When a DOM read comes back empty, check the HTTP status of the URL first, then blame the generator.
