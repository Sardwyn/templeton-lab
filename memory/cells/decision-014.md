---
id: decision-014
kind: decision
key: 014
updated: 2026-11-01T04:05
supersedes: []
confidence: high
---

Brad ruled on 2026-11-01: a trial app's runtime requirement is satisfied by a portable copy inside F:\Lab\trials\, never a system-wide install. SimpleLauncher 5.8.4 needed .NET 10, so F:\Lab\trials\dotnet10 (10.0.2) runs it via DOTNET_ROOT and deleting trials\ removes the dependency. Corollary: check the runtime a candidate needs before promising a result, and budget a portable copy of it.
