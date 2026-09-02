---
name: tech-debt
description: >-
  On-demand debt sweep. Use when the owner asks for a cleanup pass, before a
  release or milestone, or when the codebase feels heavier than its feature
  count justifies.
---

# tech-debt

Start with `python3 scripts/dup_check.py --list`: it prints every duplicated
block without failing, the fastest map of where the debt is. Entries in
`.dup-baseline` are debt too; the file should shrink every sweep.

Sweep for: files that outgrew one concept; duplicated logic, markup, or
config (a page repeating another page's shell, values the tokens file owns
inlined); the same convention re-justified in several docstrings (state it
once, link from the rest); dead code and unused deps; docs that drifted from
the code (`docs/features.json` statuses, `docs/SECURITY.md` vs the actual
surfaces, mockups vs shipped screens); tests that no longer test anything.

**Docs are swept like code.** Same question as for a function: what breaks if
this is deleted? Delete on sight: plans for merged features, probes whose
finding is in a fixture, mockups with no live surface, gotchas the code now
makes impossible. A budgeted doc near its cap is a finding, not a pass.

**Check the checkpoint cost.** What a fresh session reads to resume one
feature (`AGENTS.md`, the `iteration` skill, one entry, its plan) is what the
`checkpoint-budget` CI job measures. Over its cap is a finding; the usual
cause is a plan that narrates.

Output: a ranked paydown list (impact vs effort). Fix the cheap high-value
items in the same pass; file the rest as `features.json` todo entries. Do not
refactor beyond the list: a sweep that becomes a rewrite defeats its purpose.
