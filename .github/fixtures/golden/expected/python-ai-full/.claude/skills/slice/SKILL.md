---
name: slice
description: >-
  The per-feature workflow for this project. Use when starting any feature,
  change, or fix -- "build F003", "next feature", "add X", "fix Y". Reads the
  feature's entry in docs/features.json, picks the risk tier, and runs the
  tier's procedure.
---

# slice -- build one feature at the right ceremony level

## 1. Anchor

`docs/features.json` entries are for user-observable features and meaningful
behavior changes. Light-tier chores (typos, copy tweaks, pure refactors, small
fixes with no new behavior) need no entry -- quality gate green is their
whole lifecycle; skip straight to step 3's light procedure. Otherwise, read
the feature's entry in `docs/features.json` (id, intent, `serves:`,
acceptance, tier). If the work has no entry yet, add one first (next free id,
`status: todo`, `tests: []`) -- the array is priority-ordered, and user-visible
journey features lead unless the owner reorders; hardening and infra queue
behind the first shippable surface. The `serves:` line is the tether to
`docs/PRODUCT_VISION.md` -- if you cannot write one, question the feature.

## 2. Pick the tier

Judge against the table in `AGENTS.md` `<risk-tiers>`. When genuinely unsure
between standard and high-risk, ask the owner -- that is cheaper than either
mistake.

## 3. Run the tier

**light** -- make the change; run the quality gate; done.

**standard** --
1. Plan briefly, free form: approach, the riskiest bit, data shapes at
   boundaries, test list (unit / functional / e2e for the acceptance criteria).
   Put it in the PR description or a short note; no fixed headings. For an
   external collaborator that is flaky or under-documented, record one real
   probe (request + response) in `docs/probes/` and build fixtures from it;
   stable, well-documented APIs may be coded against their docs (verify
   signatures via Context7).
2. New user-visible surface? Run the `design-loop` skill first (that is where
   the one mockup approval lives). Changing an existing surface? Re-read its
   mockup; drift is a deviation to log.
3. Red -> Green with the `tdd` skill: failing tests first (mapped to the
   acceptance criteria), then minimal code, then refactor. Update the feature's
   `tests` array as you name them.
4. Review: dispatch `@code-reviewer` (correctness + requirements only; when
   subagents aren't available in your harness, run the equivalent
   independent pass in a fresh context instead). If the feature is
   user-visible, dispatch `@design-reviewer` after green. If the work
   matches the `security-review` skill's trigger, run that too.
5. Set `status: done` only when mapped tests pass and reviews are resolved;
   run `python3 scripts/features_check.py` and the quality gate.

**high-risk** -- everything in standard, plus: write the plan to
`docs/plans/<feature-id>.md` and get the owner's approval BEFORE implementation
(use `grill-me` on the plan if installed); `@security-reviewer` runs; the full
pyramid (unit + functional + e2e + security tests) is named at Red.

## 4. Architecture defaults (all tiers)

Two layers by default (domain/IO vs UI); small files, one concept each; no
abstraction before two real callers; functions over classes; match the code
style anchor in `AGENTS.md` `<project>`.

## 5. Close

Log any deviation from plan or mockup in `docs/deviations.md` (conservative
choice + one line). Surprises go to `docs/gotchas.md`. Off-scope ideas become
new `features.json` entries (status todo) instead of scope creep.
