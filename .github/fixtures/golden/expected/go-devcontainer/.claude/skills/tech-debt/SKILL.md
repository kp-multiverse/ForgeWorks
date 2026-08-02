---
name: tech-debt
description: >-
  On-demand debt sweep. Use when the owner asks for a cleanup pass, before a
  release or milestone, or when the codebase starts feeling heavier than its
  feature count justifies.
---

# tech-debt

Start with `python3 scripts/dup_check.py --list` -- it prints every duplicated
block without failing, which is the fastest map of where the debt is. Entries
in `.dup-baseline` are debt too -- the file should shrink every sweep.

Sweep for: files that outgrew one concept; duplication in all three of its
forms -- logic (two+ callers of the same hand-copied code), markup and config
(a page repeating another page's shell, or inlining values the tokens file
owns), and prose (one convention re-justified in five docstrings; state it
once, link to it from the rest); dead code and unused deps;
docs that drifted from the code (`docs/features.json` statuses, `docs/SECURITY.md`
vs the actual surfaces, and on a frontend project `docs/design/mockups/` vs the
shipped screens); tests that no longer test anything real.

**Docs are swept like code.** Same question as for a function: what breaks if
this is deleted? Delete on sight -- plan files for merged features, probe
files whose finding is in a fixture, mockups with no live surface, scratch
analyses, gotchas the code now makes impossible, `docs/archive/` files nobody
has reopened. A budgeted doc (`AGENTS.md` `<context>`) sitting near its cap
is a finding, not a pass: prune it. Count the live `.md` files in
`docs/` -- if that number is growing faster than the feature count, docs are
the debt.

**Check the checkpoint cost.** Add up what a fresh session must read to resume
one feature: `AGENTS.md` + the `iteration` skill + one `features.json` entry +
that feature's plan. Over what the `checkpoint-budget` CI job allows is a finding --
the usual cause is a plan that narrates, or a doc being read whole that should
be read by section.

Output: a ranked paydown list (impact vs effort). Fix the cheap high-value
items in the same pass; file the rest as `features.json` entries or
`docs/deviations.md` notes. Do not refactor beyond the list -- a sweep that
becomes a rewrite defeats its purpose.
