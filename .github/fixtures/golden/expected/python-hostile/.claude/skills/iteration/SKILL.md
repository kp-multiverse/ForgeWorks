---
name: iteration
description: >-
  The per-feature workflow -- the only one. Use when starting any feature,
  change, or fix: "build F003", "next feature", "add X", "fix Y". Routes
  chores straight to build; features through GRILL -> RED -> GREEN ->
  REVIEW -> MERGE with hard caps.
---

# iteration -- one bounded loop per feature

Append a line to `docs/LEDGER.md` at every state change (format at the
bottom). Evidence rule: no state advances without proof -- test output, the
command run, or a screenshot path in the ledger line.

## 0. Route

**Chore** (typo, copy tweak, small fix, refactor with no behavior change --
the diff fits in one sentence): make the change, run `uv run qa`,
commit. Done. No feature entry, no review, no ledger line.

Anything else is a **feature**. No `docs/features.json` entry yet? Add one:
next free id, `status: todo`, `tests: []`, `surface:` the screen/page it
touches or `"none"`, `serves:` pointing at `docs/PRD.md` (cannot write that
line? question the feature). Unsure which tier? It is a feature.

## 1. GRILL -- design, then the one owner gate

Draft the plan into `docs/plans/<id>.md` with these sections:

- **Ask.** What the owner asked, in their words. Decisions already made,
  including explicit "owner said no to X" lines.
- **Approach.** The approach, the riskiest bit, data shapes at the
  boundaries, out-of-scope lines, files to touch.
- **Acceptance (EARS).** One line per criterion:
  `WHEN <condition> THE SYSTEM SHALL <behavior>`. Copy these into the
  feature's `acceptance` array -- each becomes a named test in RED.
- **Security.** Does the work touch the `security-review` skill's trigger?
  If yes, add a threat model: the new attack surface, who can send what
  through it, the validation point per input (allowlist at the boundary,
  fail closed), behavior when the outside world misbehaves, what an
  attacker tries first. Rule of Two: if the feature combines untrusted
  input + sensitive data + external write/egress, drop one leg or put
  owner approval on the action. Name the security tests here.
  The threat model lives in THIS plan file and dies with it. What lands in
  `docs/SECURITY.md` is only the delta: new rows in the attack-surface
  table, and edits to the EXISTING red-team checklist categories. Never
  append a per-feature section there -- that is how a threat model turns
  into a changelog.
- **Mockup** (only if `surface` is not "none"). Build 3-4 genuinely
  different throwaway HTML mockups -- different layouts, not recolors; real
  content; respect the tokens file. The owner picks; commit the winner to
  `docs/design/mockups/<id>-<name>.html` and write that path into the
  feature entry's `mockup` field. `features_check.py` blocks a surface
  feature from leaving `todo` without it. Changing an existing surface?
  Update its mockup in the same branch.
- **Fan-out** (only when honestly warranted). Propose it only if the work
  splits into 2+ pieces touching disjoint files with no ordering: the
  pieces, agent count (max 5), expected benefit, cost note ("~Nx tokens of
  a solo build"). Overlapping files, unclear boundaries, or "might be
  faster" are not reasons.

Now **attack the plan**: strongest objections, failure modes, a simpler
alternative, and the attacker's view. Present to the owner in the
`<communication>` GRILL shape. The owner approves once, here. Write every
decision from the conversation back into the plan file and sync the
feature's `acceptance` -- a decision that lives only in chat does not
exist.

**Size is the test of whether it decided anything.** The finished plan must
let a FRESH session execute the feature alone, in **under 8000 characters** --
the `docs-budget` job fails the branch above that. That is roughly 2K tokens,
and it is the largest single thing a restarted session loads (see `AGENTS.md`
`<context>`). A plan that does not fit is describing rather than deciding:
cut the restated background, the options you rejected, and anything the code
or `features.json` already says. Decisions, not narrative.

## 2. RED

Branch `feat/<id>-<slug>`. Failing tests first: one per EARS criterion,
plus the threat model's security tests; record each name in the feature's
`tests` array. Confirm each fails for the right reason. Evidence: the
failing run output. Set `status: in-progress`.

## 3. GREEN

Implement in THIS context -- no implementer subagent. If the owner approved
fan-out at GRILL: one git worktree per piece, one writer per branch, the
caps below apply per agent. Write the least code that passes, then refactor:
remove dead code, one concept per file. Visual surfaces are BUILT AGAINST the
approved mockup, visual values from the tokens file.

**Say it once.** Duplication is not only logic. Three kinds, all real:

- **Logic** -- extract at two real callers, not before.
- **Markup and config** -- a page that hand-repeats another page's shell, or
  inlines values that live in the tokens file, is a component waiting to be
  extracted. This is the most common one on a frontend.
- **Prose** -- the same convention re-justified in five docstrings. Explain it
  ONCE where it lives; every other site links there in a clause. A comment
  says WHY, and only where the why is not already written down.

`python3 scripts/dup_check.py` measures all three: the same 6-line block
(comments, strings and numbers normalized away) in two files fails. Run it
before REVIEW, not after. A finding you are not fixing needs one of two
records, and they are not interchangeable: `.dup-ignore` exempts a path forever
(only for a tree whose repetition is inherent, like tests), while
`--baseline` records today's duplicate blocks by hash so new ones still fail --
including new duplication inside a file already baselined. Prefer the baseline:
a path exemption is permanent, a baseline entry decays the moment anyone edits
the block. Either way it is a reviewable decision, not a silence.

Exit: `uv run qa` green AND `python3 scripts/dup_check.py` green. A red
gate cannot enter REVIEW.
**Stall cap:** 2 consecutive failed test cycles on the same failure ->
checkpoint commit, stop, ask the owner (recommended recovery: a fresh
context re-primed from the plan file with the failure lesson added).

## 4. REVIEW

Dispatch `@reviewer` with a minimal brief: the plan file path, the diff (or
branch name), grep-targeted doc sections, the mockup path if visual.
Never "read the docs". (No subagents in this harness? Run the same pass as
an independent fresh-context session.)
**Caps:** max 2 fix passes after a REQUEST_CHANGES; max 1 re-review, and it
CONTINUES the same reviewer conversation -- never a fresh spawn; max 1
design rework when the design-fidelity lens fails -- then stop and ask the
owner with the named deltas. Any cap hit -> stop and ask the owner in the
`<communication>` cap-hit shape.

## 5. MERGE -- checklist, in order

1. `uv run qa` green; `bash scripts/e2e.sh` green;
   `python3 scripts/features_check.py` green.
2. Merge to main. Delete the feature branch. Remove every worktree this
   feature created; run `bash scripts/factory_doctor.sh` and confirm it
   reports none left.
3. Set `status: done` (its mapped tests exist and pass -- hard rule).
4. Delete `docs/plans/<id>.md`. Its decisions already live in the feature's
   `acceptance` array, the commit history, and the ledger line. Anything in
   the plan that is NOT captured in one of those and still changes a future
   decision goes there FIRST (a gotcha, a `SECURITY.md` row, a test name) --
   then delete the file. Never keep the plan just to hold it.
5. Doc budgets (`<context>` block): any budgeted doc over its cap -> compact
   it in this same merge. Compacting means deleting every entry that is no
   longer true or no longer changes a decision, until nothing left is
   deletable. Landing within 5% of the cap means you shaved to just under the
   line instead -- redo it. A doc parked at 99% of its budget release after
   release is the exact failure this rule exists to prevent. Move to
   `docs/archive/` only what you would genuinely re-read; if `docs/archive/`
   is over ITS cap, delete oldest files until it is under.
6. Run `python3 scripts/backlog.py` -- regenerates `docs/BACKLOG.md`.
7. Ledger: `<id> | MERGED | - | <time> | agent: main | worktrees: 0
   remaining, e2e: N passed`.
8. Merge report to the owner: 3 lines (shipped -- in the plan's words,
   evidence, next up in the backlog).

## Ledger format

One line per state change, appended to `docs/LEDGER.md`:

    F012 | GRILL  | approved      | 2026-08-01 13:40 | agent: main | plan: docs/plans/F012.md
    F012 | GREEN  | round 1/2     | 2026-08-01 14:02 | agent: main | gate: 42 passed
    F012 | REVIEW | round 1/1     | 2026-08-01 14:31 | agent: reviewer | APPROVE, 1 optional
    F012 | MERGED | -             | 2026-08-01 14:58 | agent: main | worktrees: 0 remaining, e2e: 7 passed

When the live file passes its 6K cap, drop merged features' lines entirely --
the commit history is the durable record. Archive a year's lines to
`docs/archive/LEDGER-<year>.md` only if you actually re-read them.

## Close (every feature)

Deviations from plan or mockup: conservative choice + one
`docs/deviations.md` line. Surprises -> `docs/gotchas.md`, one entry of four
short lines. Off-scope ideas -> new `features.json` entries (status todo),
never scope creep.

Then delete this feature's scaffolding, in the merge commit:

- Any `docs/probes/` file nothing cites. `grep -r "docs/probes/<name>" .`
  first: a probe named by a test or a source comment is that fixture's
  provenance and stays as long as the fixture does. An uncited one is
  scaffolding.
- Every mockup except the approved winner for a surface that still exists.
- Any scratch analysis, comparison, or research note written to reach the
  decision. The decision is in the code and the feature entry.

Nothing here is "kept for the record" -- git already has the record.
