---
id: lesson-shell-eats-quotes
kind: lesson
key: shell-quoting
updated: 2026-10-30T03:45
supersedes: []
confidence: high
---

The shell wrapper **eats/ mangles quotes** and `&&` is unreliable here (Win10
cmd). Workarounds that worked: run commands separately or chain with `&`; put
quoted multi-word args (like `git commit -m "..."`) into a message file and use
`git commit -F file`; for PowerShell use a .ps1 file with -File instead of
inline -Command. Also: findstr/`type nul >` quoting is finicky — prefer
Python/PowerShell for anything complex. Two more from 2026-10-30: PowerShell 5.1's
`Set-Content -Encoding utf8` writes a BOM, which leaked into a commit subject — write
message files with a tool that emits plain UTF-8. And `remember.py` adds the kind
prefix itself, so passing `decision decision-009` creates `decision-decision-009.md`;
the key argument must omit the prefix.
