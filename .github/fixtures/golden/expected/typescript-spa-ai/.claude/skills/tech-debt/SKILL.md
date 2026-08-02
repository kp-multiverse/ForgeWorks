---
name: tech-debt
description: >-
  On-demand debt sweep. Use when the owner asks for a cleanup pass, before a
  release or milestone, or when the codebase starts feeling heavier than its
  feature count justifies.
---

# tech-debt

Sweep for: files that outgrew one concept; real duplication (two+ callers of
the same hand-copied logic -- extract to one home); dead code and unused deps;
docs that drifted from the code (`docs/features.json` statuses,
`docs/design/mockups/` vs shipped screens, `docs/SECURITY.md` vs actual
surfaces); tests that no longer test anything real.

**Docs are swept like code.** Same question as for a function: what breaks if
this is deleted? Delete on sight -- plan files for merged features, probe
files whose finding is in a fixture, mockups with no live surface, scratch
analyses, gotchas the code now makes impossible, `docs/archive/` files nobody
has reopened. A budgeted doc (`AGENTS.md` `<context>`) sitting near its cap
is a finding, not a pass: prune it. Count the live `.md` files in
`docs/` -- if that number is growing faster than the feature count, docs are
the debt.

Output: a ranked paydown list (impact vs effort). Fix the cheap high-value
items in the same pass; file the rest as `features.json` entries or
`docs/deviations.md` notes. Do not refactor beyond the list -- a sweep that
becomes a rewrite defeats its purpose.
