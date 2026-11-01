---
id: decision-014
date: 2026-11-01
status: active
title: Runtime requirements are met portably inside trials, never system-wide
decided_by: brad
---

# Decision-014: Runtime requirements are met portably inside trials, never system-wide

**Ruled by Brad on 2026-11-01**, when SimpleLauncher 5.8.4 turned out to require
.NET 10 and the choice was to install that runtime on the machine or carry a portable
one inside the trial. He chose the portable runtime.

## The rule

1. **A trial app's runtime lives inside `F:\Lab\trials\`.** SimpleLauncher runs from
   `F:\Lab\trials\dotnet10` (.NET 10.0.2) with `DOTNET_ROOT` pointed at that folder;
   nothing is added to the machine-wide runtime store, PATH, or registry.
2. **Deleting `trials\` deletes the dependency.** A trial must be removable as one
   directory, with no uninstall step and no leftover runtime.
3. **The same rule covers drivers and emulators**, per Decision-012
   (`F:\Lab\org\decisions\2026-10-31-trial-reuses-existing-retroarch.md`): if
   something already exists on the system, use it read-only; if it does not, carry it
   inside the trial rather than install it.

## Why

The trial is temporary evidence. A system-wide runtime would outlive the verdict,
could change how other apps behave, and would leave Brad cleaning up after an
experiment he only agreed to as an experiment.

## Consequence

- SimpleLauncher's measured results in
  `F:\Lab\org\notes\retro-game-library-options.md` were produced under a portable
  runtime, so adopting it later means adopting .NET 10 for real — that is an adoption
  cost, stated in the note, not a hidden one.
- Any future trial app gets the same treatment: check the runtime it needs before
  promising a result, and budget a portable copy of it inside `trials\`.
