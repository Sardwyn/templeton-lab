---
id: lesson-shell-eats-quotes
kind: lesson
key: shell-quoting
updated: 2026-10-15T04:10
supersedes: []
confidence: high
---

The shell wrapper **eats/ mangles quotes** and `&&` is unreliable here (Win10
cmd). Workarounds that worked: run commands separately or chain with `&`; put
quoted multi-word args (like `git commit -m "..."`) into a message file and use
`git commit -F file`; for PowerShell use a .ps1 file with -File instead of
inline -Command. Also: findstr/`type nul >` quoting is finicky — prefer
Python/PowerShell for anything complex.
