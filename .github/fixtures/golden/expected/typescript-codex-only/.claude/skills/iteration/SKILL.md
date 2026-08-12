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
the diff fits in one sentence): make the change, run `npm run qa`,
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
- **Batch** (full weight only; only when honestly warranted). Propose
  running 2 features in parallel ONLY when both plans exist and their
  files-to-touch lists do not intersect: each feature gets its own worktree,
  branch, and single writer; merges queue one at a time through the full
  gate; `factory_doctor.sh` must report zero worktrees after. Overlapping
  files, unclear boundaries, or "might be faster" are not reasons. The
  owner approves the batch here, at GRILL, with a cost note.

Now **attack the plan**: strongest objections, failure modes, a simpler
alternative, and the attacker's view. Present to the owner in the
`<communication>` GRILL shape. The owner approves once, here. Write every
decision from the conversation back into the plan file and sync the
feature's `acceptance` -- a decision that lives only in chat does not
exist.

**Size is the test of whether it decided anything.** The finished plan must
let a FRESH session execute the feature alone, and fit the plan cap that the
`docs-budget` job enforces (that job owns the number -- read it there). It is
the largest single thing a restarted session loads, so it is the first place
to look when a restart gets expensive. A plan that does not fit is describing rather than deciding:
cut the restated background, the options you rejected, and anything the code
or `features.json` already says. Decisions, not narrative.

## 2. RED

Branch `feat/<id>-<slug>`. Failing tests first: one per EARS criterion,
plus the threat model's security tests; record each name in the feature's
`tests` array. Confirm each fails for the right reason. Evidence: the
failing run output. Set `status: in-progress`.

## 3. GREEN

Implement in THIS context by default -- no standing implementer subagent. A
`surface: "none"` feature whose RED tests are complete MAY go to a
`standard`-tier fresh agent on a job card (see Dispatch below) -- the tests
are the whole contract. If the owner approved a batch at GRILL: one git
worktree per feature, one writer per branch, the caps below apply per agent. Write the least code that passes, then refactor:
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

`python3 scripts/dup_check.py` measures all three: the same block of source
(comments, strings and numbers normalized away) appearing in two files fails.
The window size lives in that script. Run it
before REVIEW, not after. A finding you are not fixing needs one of two
records, and they are not interchangeable: `.dup-ignore` exempts a path forever
(only for a tree whose repetition is inherent, like tests), while
`--baseline` records today's duplicate blocks by hash so new ones still fail --
including new duplication inside a file already baselined. Prefer the baseline:
a path exemption is permanent, a baseline entry decays the moment anyone edits
the block. Either way it is a reviewable decision, not a silence.

Exit: `npm run qa` green AND `python3 scripts/dup_check.py` green. A red
gate cannot enter REVIEW.
**Stall cap:** 2 consecutive failed test cycles on the same failure -> run
CHECKPOINT (below, and add the failure lesson to the plan), stop, ask the
owner. The recommended recovery is a fresh context: `/clear`, then `go`.

## 4. REVIEW

Dispatch `@reviewer` with a minimal brief: the plan file path, the diff (or
branch name), grep-targeted doc sections, the mockup path if visual.
Never "read the docs". (No subagents in this harness? Run the same pass as
an independent fresh-context session.)
Write the findings into the plan under `## Review findings (open)` before
fixing any of them -- the reviewer's message is conversation, and a clear
between review and fix would otherwise lose the entire list. Strike each line
as it is fixed.
**Caps:** max 2 fix passes after a REQUEST_CHANGES; max 1 re-review, and it
CONTINUES the same reviewer conversation -- never a fresh spawn; max 1
design rework when the design-fidelity lens fails -- then stop and ask the
owner with the named deltas. Any cap hit -> stop and ask the owner in the
`<communication>` cap-hit shape.

## 5. MERGE -- checklist, in order

1. `npm run qa` green; `npm run e2e` green;
   `python3 scripts/features_check.py` green.
2. Merge to main. Delete the feature branch. Remove every worktree this
   feature created; run `bash scripts/factory_doctor.sh` and confirm it
   reports none left.
3. Set `status: done` (its mapped tests exist and pass -- hard rule). Then
   move anything in the plan or ledger that still changes a future decision:
   a lesson to `docs/gotchas.md`, a security delta to `docs/SECURITY.md`,
   owed work to the feature's `notes` or a new todo entry. Carry a status
   VERBATIM or delete it -- never reword an obligation into a claim.
4. `python3 scripts/prune.py` -- deletes this feature's ledger and deviations
   lines, its plan, losing mockups, and uncited probes. No MERGED ledger
   line: the merge commit is the durable record; the ledger holds open
   features only.
5. `python3 scripts/backlog.py` -- regenerates `docs/BACKLOG.md`.
6. If `docs-budget` still flags a judgment doc (gotchas, SECURITY): delete
   whole stale entries until it passes clear of the cap -- never rewrite one.
7. Merge report to the owner: 3 lines (shipped -- in the plan's words,
   evidence, next up in the backlog).

## Dispatch -- job cards and the model ladder

Work leaves this context only on a JOB CARD: the deliverable's shape, the
exact inputs (paths + named sections, never "read the docs"), the model
tier, and the done-check (the command or test that verifies the result). If
a card that small cannot be written, the job is not dispatchable -- keep it.

Tiers are named in `docs/agents.json` (`model_tiers` -- model ids live
there, never in prose; every dispatch states its tier explicitly). A tier
value may carry a harness prefix (`opencode:<model-id>`): send that card
through the harness's non-interactive runner (`opencode run -m <model-id>
"<card>"`), same job-card rules. Route by
one rule: **the cheapest model whose failure the done-check would catch.**

- `mechanical`: chores with a mechanical done-check -- renames, log mining,
  regenerations (`prune.py`/`backlog.py` runs), dep bumps the gate verifies.
- `standard`: GREEN against complete RED tests for a non-UI feature.
- `judgment` (or this context): GRILL, RED, REVIEW, security, mockups --
  anywhere a wrong answer fails silently instead of loudly.

**Escalation:** a card whose done-check fails twice at its tier comes back
one tier up (or into this context) with the failure output attached --
never a third try at the same tier, and never a silent retry. Ledger the
escalation; the GREEN stall cap still applies after it.

Commit before every dispatch (a reviewer once stashed uncommitted work into
oblivion); one writer per branch, no exceptions.

## CHECKPOINT -- run before any clear, and whenever a decision is made

Clearing is safe exactly when nothing live is left in the conversation. This is
how you get there, in under a minute:

1. Any decision, constraint or rejected option agreed in chat since the last
   checkpoint -> into the plan file (or `features.json` `acceptance`). A
   decision that lives only in chat does not exist.
2. Reviewer findings you have not yet fixed -> into the plan under
   `## Review findings (open)`, one line each. They are otherwise lost the
   moment the conversation goes, and `go` would resume a fix round with nothing
   to fix against.
3. Work in progress -> a checkpoint commit (`wip: <feature> <what works so far>`).
   Uncommitted work is not state, it is luck.
4. Append the ledger line for wherever you actually are, including `next:`.
5. `python3 scripts/resume.py` -- if it refuses, the pointers disagree and a
   fresh session would have started from the wrong place. Fix that now.

After this, `/clear` costs nothing and `go` picks up exactly here. Mid-phase is
fine once you have done it -- the stall-cap recovery below is the same move.

**Offering the clear.** One line, inside a report you were already writing, and
only when the next action needs nothing from this conversation. Never a
question, never mid-orchestration, never on a timer. If it is not earned, stay
quiet: an offer the owner learns to ignore is worse than none.

## Ledger format

One PHYSICAL line per state change, appended to `docs/LEDGER.md`. The ledger
holds open features only -- `prune.py` deletes a feature's lines at merge, and
the commit history is the durable record. `prune.py --check` (CI) owns the
length cap: pointers, not prose -- counts, SHAs, paths. The story belongs in
the commit message. End with `next: <the single next action>` -- the one fact
a restart cannot derive from anywhere else; `scripts/resume.py` reads it
straight out:

    F012 | GRILL  | approved      | 2026-08-01 13:40 | agent: main | plan: docs/plans/F012.md, next: write the failing tests for AC1-AC4
    F012 | GREEN  | round 1/2     | 2026-08-01 14:02 | agent: main | gate: 42 passed
    F012 | REVIEW | round 1/1     | 2026-08-01 14:31 | agent: reviewer | APPROVE, 1 optional

## Close (every feature)

Deviations from plan or mockup: conservative choice + one `docs/deviations.md`
entry, capped by `prune.py --check`. Surprises -> `docs/gotchas.md`, one entry
of four short lines. Off-scope ideas -> new `features.json` entries (status
todo), never scope creep -- and never a prose ideas file.

Scaffolding (losing mockups, uncited probes, scratch analyses written to reach
the decision) is deleted by `prune.py` at merge. Nothing is "kept for the
record" -- git already has the record. A probe a test or source comment cites
by path is provenance, not scaffolding; `prune.py` leaves it alone.
