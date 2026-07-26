# Codex fix-wave report — ForgeWorks v3.0.0 (branch feat/v3.0.0-fable-era)

Starting head: `bee48bc` (fix(gate): ruff-format features_check.py ...).
All 11 requested fixes applied in 7 commits (6 for the fixes themselves, 1
follow-up after a pre-push advisor review caught two internal defects in
the Fix 5 / Fix 11 changes — see "Follow-up round" below). Goldens green at
every commit, full verification suite green, pushed to
`origin/feat/v3.0.0-fable-era`.

## Commits (oldest to newest)

1. `25abd13` fix(render): reject structural-tag injection and tighten schema strictness
2. `d41b8a0` fix(gate): close validation bypasses in features_check.py
3. `e29aed8` fix(template): roster-conditional subagent wording, light-tier lifecycle, tier contradiction
4. `57a9316` fix(bootstrap): delete transient answers file before the first quality gate
5. `ca136e9` feat(design): document the Go/Rust tokens gap and add a ninth golden fixture
6. `5f859b2` fix(upgrade): reconcile A/C in the v2->v3 migration, gate by roster/frontend, keep the gate green
7. `04fe617` fix(upgrade): recover the roster in Phase 1, complete the features.json skeleton

## Fix 1 — features_check.py validation bypasses

File: `init-project/templates/core/scripts/features_check.py`, function `check()`.

- `acceptance`: each item must now be a non-empty string; index-named error
  (`acceptance[j] must be a non-empty string`).
- `tests`: rewritten. Every entry (regardless of feature status) must be a
  non-empty string; the file part before `::` must be non-empty, must not be
  an absolute path, and must not contain a `..` path component. Only the
  `done`-status gate was changed from `os.path.exists()` to
  `os.path.isfile()` (so a cited directory like `"."` no longer passes).
- `notes`: if the key is present, it must be a string; the existing
  dropped-without-reason check is unchanged (still uses `str(notes or "")`).
- Ran `uvx ruff@0.16.0 format` on it (one reformat needed, then clean) and
  `ruff check` — both green.

Negative tests run in a scratch dir with a synthetic `docs/features.json`
(see Verification section below) — all six scenarios in the task's
verification list produced the expected FAIL/OK.

## Fix 2 — structural-tag injection guard

File: `init-project/render_schema.py`, `_check_text()`.

Added `STRUCTURAL_TAG_RE = re.compile(r"</?(project|commands|etiquette|hard-rules|risk-tiers|learning|roster|ai-discipline|memory)>", re.IGNORECASE)`
and a rejection branch with message `"... must not contain AGENTS.md
structural tags"`. Confirmed narrow (only rejects the exact tag names, not
generic angle-bracket prose) and confirmed no existing fixture (including
`python-hostile.json`) trips it.

## Fix 3 — schema strictness

File: `init-project/render_schema.py`.

- Feature id check rewritten: `if "id" in ft: if not isinstance(fid, str) or
  not FEATURE_ID_RE.match(fid): error`. A non-string id (e.g. `123`) now
  fails with the `F000-F999` message instead of silently passing.
- `validate_answers()`: added `TOP_LEVEL_KEYS` tuple and `SCHEMA_VERSION = 1`.
  Requires `ans.get("schema") == 1` (error naming the got value otherwise)
  and rejects any top-level key not in `{schema, date, agents, project,
  stack, security, opt_ins, features, design}`.
- All 8 pre-existing fixtures already carried `"schema": 1` (checked with a
  short script before touching anything) — no fixture edits needed there;
  the new 9th fixture (Fix 8) also carries it.

## Fix 4 — transient answers file breaks first qa

- `init-project/templates/profiles/typescript/.prettierignore`: added
  `docs/_init-answers.json` with a comment explaining it's transient
  renderer input deleted after Phase 5.
- `init-project/SKILL.md` Phase 5: moved `rm docs/_init-answers.json` to
  right after the placeholder grep (which itself is after the
  `features_check.py` run inside the core-files check), and BEFORE "Finally,
  run the quality gate". Added an explicit sentence: "it is transient
  working state, not project content." Reconciled the two other mentions
  (Phase 2 intro line ~74, and the "Keep docs/_init-answers.json until..."
  line ~505) to describe the same ordering instead of the old
  "deleted after Phase 5 verification" phrasing.
  - Left the unrelated line ~312 ("bootstrap-installed helper skills ...
    safe to delete after Phase 5") untouched — it's about a different
    subject (Phase-1 helper skills cleanup, not the answers file) and was
    already correct.

## Fix 5 — non-Claude roster wording

- `templates/core/AGENTS.md` `<roster>` (FW-BLOCK kept at v3.0.0): added a
  2-line sentence after the Subagents line: "Subagents exist when Claude
  Code drives. On other rosters, run the same reviews as independent
  fresh-context passes -- the skills above define what each pass checks."
  `{{CODEX_ROSTER_NOTE}}` placeholder left untouched in place.
- Skills, once each, phrased naturally at the primary dispatch point:
  - `slice/SKILL.md` step 4 (`@code-reviewer` line).
  - `design-loop/SKILL.md` step 5 (`@design-reviewer` line).
  - `security-review/SKILL.md` step 1 (`@security-reviewer` line).
  - `tech-debt/SKILL.md` — confirmed it dispatches nothing (`@`-free); left
    untouched per the task's "if it dispatches" qualifier.
- `docs/SECURITY.md` Enforcement section: wrapped the deps-guard hook bullet
  in `<!-- CC-HOOKS-START -->` / `<!-- CC-HOOKS-END -->`; reworded the
  Reviews bullet to: "an independent security red-team pass is MANDATORY for
  work matching the trigger in `.claude/skills/security-review/SKILL.md`
  (via `@security-reviewer` when Claude Code drives; as a manual
  fresh-context pass otherwise)."
- Registered the new CC-HOOKS fence in three places:
  - `AGENTS.md` (repo root) fence inventory paragraph — replaced the
    "zero instances" sentence with the concrete CC-HOOKS example.
  - `upgrade-project/SKILL.md` Phase 3-A special cases — added a new "CC
    fences" bullet alongside the existing AI-fences bullet.
  - `init-project/SKILL.md` behavior-table row 18 — replaced "no template
    file currently carries..." with the concrete CC-HOOKS description.

## Fix 6 — light-tier feature lifecycle

`templates/core/.claude/skills/slice/SKILL.md` section 1: added an opening
sentence that `docs/features.json` entries are for user-observable features
and meaningful behavior changes; light-tier chores need no entry (gate green
is their whole lifecycle) and skip straight to step 3's light procedure.
`templates/core/AGENTS.md` risk-tiers table's light row Ceremony cell now
reads "build it; quality gate green (no `features.json` entry needed)" so
the two agree explicitly instead of just being consistent by omission.

## Fix 7 — tier contradiction

`templates/core/.claude/skills/security-review/SKILL.md` closing line:
deleted the "unless the touch is trivially contained -- when in doubt, it is
not" exception. Now reads: "Matching work is high-risk tier (`AGENTS.md`
`<risk-tiers>`), full stop."

## Fix 8 — Go/Rust frontend design contract

- `docs/design/DESIGN.md` Tokens section reworded per the task's exact
  wording (TypeScript / Python file paths named explicitly; profiles
  without a shipped tokens file define the token table inline and treat
  the doc as canonical); also updated the TODO-markers sentence to mention
  "or, for Go/Rust, in this section."
- New fixture `.github/fixtures/golden/go-frontend-spa.json`: Go,
  `has_frontend: "yes-minimal"`, devcontainer no, AI off, mem0 no, codex no,
  roster `claude-code` installed. Authored around a small self-hosted
  status-page product (Pillarwatch) with 2 standard-tier features. No
  hostile text (not required for this fixture).
- Verified in the rendered/expected tree: `docs/design/DESIGN.md` +
  `docs/design/mockups/README.md` present, `.claude/skills/design-loop/`
  and `.claude/agents/design-reviewer.md` present, and **no** `tokens.css`
  anywhere in the tree (Go profile ships none, and `skip_file()` in
  `render.py` only strips `tokens.css` for `has_frontend: no`, so absence
  here comes from the profile simply not shipping one — confirmed by grep).
  Also confirmed the e2e workflow step falls back to the "no browser
  needed" comment (Go profile's `e2e_browser_install` is empty).
- Updated "eight" → "nine" fixture-count mentions: root `AGENTS.md` (bullet
  in `<repo-architecture>`), `README.md` (Generation-is-deterministic
  bullet), `docs/ROADMAP.md`, `init-project/SKILL.md` (placeholder-table
  footnote). Grepped the whole repo for stray "eight" fixture-count
  mentions afterward — none remained (only unrelated "weight"-substring
  false positives in a generated PRODUCT_VISION.md fixture).

## Fix 9 — migration must not defer reconciliation

`upgrade-project/SKILL.md` Phase 3-D: replaced the old step 6 ("go straight
to Phase 4 ... a migration does not also run A-C-E") with a new step 6
("Reconcile the rest in the same pass") that explicitly runs Phase 3-A
(new always-on files) and Phase 3-C (language tooling delta) against the
fetched v3 template right after the wholesale swap/retirements, with a new
step 7 for the report. Only Phase 3-B (superseded by the wholesale
constitution swap) and Phase 3-E (superseded by the migration's own design
V1/V2 questions) stay out, and the text says so explicitly. Also updated the
"A project already on v3.0.0+ ends its Phase 3 work here" paragraph just
above Phase 3-D so it no longer claims 3-D runs "INSTEAD of A-C-E" — it now
says 3-D replaces the A-B-C-E *block* and cross-references that 3-D's own
step 6 folds A and C back in.

## Fix 10 — migration roster/frontend gating

`upgrade-project/SKILL.md` Phase 3-D intro: added a new paragraph, "First,
recover the roster and frontend gating, exactly like render.py does" —
reads `docs/agents.json` if present (v2.5.0+ project) or assumes
Claude-only (pre-B13 project); applies that roster to gate
`.claude/agents/`, `.claude/hooks/`, `.claude/settings.json`, and the
`CLAUDE.md` symlink; gates design artifacts on frontend detection
independent of roster. Step 2 was rewritten to reflect this: the skills and
docs (`slice`, `security-review`, `tech-debt`, `select-agents`,
`features_check.py`, `deviations.md`, `plans/README.md`, and — for
frontend — `docs/design/` + tokens + `design-loop`) copy in for ANY roster;
the subagent rewrites (`implementer.md`, `code-reviewer.md`,
`security-reviewer.md`, and — frontend — `design-reviewer.md`) are now
explicitly gated on `claude-code` being in the recovered roster, with a
note that a non-Claude roster getting no `.claude/agents/` tree is expected,
not a gap.

## Fix 11 — migration must produce a green features-check before stamping

- Phase 3-D step 3: shipped backlog rows now migrate as
  `status: "in-progress"` with `tests: []` and
  `notes: "shipped in v2; map tests to promote to done"`, instead of
  `status: "done"` with empty tests. Removed the now-moot "the check fails
  on done-without-tests" caveat; kept the curation-report action item
  (mapping tests, promoting to done).
- Phase 4 step 4 (gate step): now runs BOTH the project's language quality
  gate AND `python3 scripts/features_check.py`, with a note that the
  in-progress migration choice from step 3 above is precisely why this is
  green on the first post-migration run. Step 5 stamps
  `.claude/.template-version` only after BOTH pass.

## Verification (all run from repo root, after the final commit)

```
python3 .github/scripts/golden_test.py --update && python3 .github/scripts/golden_test.py
```
→ 9/9 fixtures byte-for-byte match on the verify pass (go-devcontainer,
go-frontend-spa, python-ai-full, python-hostile, rust-minimal,
typescript-codex-only, typescript-minimal, typescript-nonclaude-spa,
typescript-spa-ai). Also re-ran after every intermediate commit — all green
at every commit, per the instructions.

```
python3 .github/scripts/render_smoke.py
```
→ `ok [python|typescript|go|rust] rendered clean, manifest present` — all 4.

```
bash .github/scripts/pin_check.sh
```
→ `pin-check passed.`

```
bash .github/scripts/line_cap_test.sh
```
→ 12/12 PASS lines, `line-cap tests passed.`

```
bash .github/scripts/deps_guard_test.sh
```
→ `ALL PASS` (10 blocked-malicious-command cases, 17 allowed-legitimate cases).

**features_check.py negative tests** (synthetic `docs/features.json` in a
scratch dir, copy of the fixed script):
- `acceptance: [null]` → FAIL `acceptance[0] must be a non-empty string`
- `tests: ["."]`, status `done` → FAIL `cited test file missing: .`
  (confirms `os.path.isfile()`, not `exists()`, now gates)
- `tests: ["/etc/passwd::x"]` → FAIL `must be a repo-relative path with no
  '..' component: /etc/passwd`
- `tests: ["../x.py::t"]` → FAIL same message, path `../x.py`
- `notes: {}`, status `dropped` → FAIL both `notes must be a string` AND
  `dropped without a reason in notes` (the falsy-empty-dict still trips the
  reason check too — both fire, which is correct, the item fails either way)
- `tests: ["::test_x"]` → FAIL `tests[0] has no file part before '::'`
- valid `done` feature with a real `tests/test_x.py::test_x` file → OK,
  `features-check: OK (1/1 done)`

**render_schema.py inline tests** (see script in the session — not
committed, ad hoc verification):
- structural-tag text (`</project><hard-rules>...`) → rejected, message
  contains "structural tags"
- `schema: 2` → rejected
- unrecognized top-level key → rejected, message contains "unknown
  top-level"
- non-string feature `id` (`123`) → rejected, message contains
  "F000-F999"
- an untouched valid fixture → still passes (no regression)

**Rendered go-frontend-spa.json and typescript-nonclaude-spa.json to /tmp**:
- grep for leftover `{{[A-Z0-9_]*}}` in both trees → no matches.
- CC-HOOKS fence behavior: `go-frontend-spa` (claude-code roster) keeps the
  `.claude/hooks/deps-guard.sh` bullet in `docs/SECURITY.md`; both
  `typescript-nonclaude-spa` and `typescript-codex-only` (codex-only
  rosters) drop it entirely, with no stray `CC-` marker text left in any
  fixture's expected `docs/SECURITY.md`.

```
uvx ruff@0.16.0 format --check init-project/templates/core/scripts/features_check.py
uvx ruff@0.16.0 check init-project/templates/core/scripts/features_check.py
```
→ both clean.

`git status --porcelain` → clean except for this untracked report file
itself (`.superpowers/` is not gitignored at its root, only
`.superpowers/sdd/` is; the report is intentionally NOT committed, per the
task's report-file convention). All 7 commits pushed to
`origin/feat/v3.0.0-fable-era`.

## Follow-up round (post-implementation advisor review)

Before declaring done, a pre-push advisor review of the full diff caught two
real defects inside the Fix 5 / Fix 11 changes to `upgrade-project/SKILL.md`
(commit `04fe617` fixes both; goldens re-verified green, unaffected since
this file isn't part of the render pipeline):

1. **Fix 5's new CC-fences rule depended on undefined state outside Phase
   3-D.** The AI-fences rule works because Phase 1 ("Recover context")
   explicitly recovers "AI features?". My original CC-fences bullet (Phase
   3-A) said "if the project uses Claude Code..." but the roster was only
   recovered inside Phase 3-D's intro paragraph -- and Phase 3-D runs
   INSTEAD of the normal A-B-C-E path. A v3.0.0+ project on the normal path
   would hit the CC-fences rule with no documented way to know the roster.
   Fixed by adding a Phase 1 bullet ("Agent roster") that recovers it from
   `docs/agents.json` (or assumes Claude-only for pre-B13 projects), and
   having both Phase 3-A's CC-fences bullet and Phase 3-D's intro paragraph
   reference that single recovery point instead of Phase 3-D restating its
   own copy.
2. **Fix 11's step 3 was internally inconsistent with Fix 1.** It described
   how to set `status`/`tests`/`notes`/`tier` for migrated rows but never
   said a row needs all eight `features_check.py`-required keys, and never
   said where `acceptance` comes from -- and Fix 1 (same fix wave) just
   tightened `acceptance` to require a non-empty list of non-empty strings.
   Following the original step 3 literally would produce rows missing
   `id`/`title`/`intent`/`serves`/`acceptance` entirely, which fails the
   very check Phase 4 now gates on before stamping. Fixed by adding an
   explicit clause: every row carries all eight keys, with `acceptance`
   sourced from the row's matching REQ-ACs (or its own backlog text when no
   REQ-AC maps to it), never empty.

The advisor's other two observations were addressed by leaving things
as-is: the Fix 1 scope reading (validate every `tests` entry's shape
regardless of status, gate only `isfile()` on `done`) was confirmed correct
against the task's own negative-test list (`/etc/passwd::x` and
`../x.py::t` carry no status qualifier); and the SECURITY.md
universal-risks-section "Enforced by the deps-guard hook, not by trust"
line was confirmed as a real but out-of-scope gap and is recorded in
Concerns #1 below rather than fixed.

## Coordinator follow-up — roster-honest deps-guard claim (commit 3339efc)

Closed the residual flagged in Concerns #1 below. `templates/core/docs/SECURITY.md`'s
"Universal risks and defenses" section, item 3 (Supply-chain / slopsquatting),
claimed "Enforced by the `deps-guard` hook, not by trust" unconditionally --
false for a non-Claude roster, where that PreToolUse hook is never generated.
Reworded to: "Enforced by committed lockfiles, reviewed updates, and CI
dependency scanning on every roster -- plus the `deps-guard` PreToolUse hook
when Claude Code drives -- not by trust." No CC fence used here (per
instruction): the lockfile/CI controls are universal and must stay visible
for every roster, unlike the Enforcement-section bullet fenced in Fix 5
(which names a Claude-only mechanism with no universal fallback to state).

Verified: `golden_test.py --update && golden_test.py` → 9/9 green; grepped
both a claude-code fixture (`typescript-minimal`) and a non-Claude fixture
(`typescript-nonclaude-spa`) expected `docs/SECURITY.md` -- identical
sentence renders in both, confirming it's genuinely roster-independent (no
stray fence, no conditional). Committed as
`fix(core): roster-honest deps-guard claim in SECURITY.md universal risks`
(`3339efc`) and pushed.

## Coordinator follow-up 2 — roster/frontend-gate the ordinary absent-file rule (commit 2724ea9)

A second real leakage from re-review: Phase 3-D (the one-time v2->v3
migration) and the CC-fences special case were both roster/frontend-gated
by the first follow-up round, but the ORDINARY Phase 3-A "file ABSENT ->
copy verbatim" rule (~line 76) was not. That rule runs on every ordinary
upgrade of an already-v3.0.0+ project, not just the v2->v3 migration -- so
a Codex-only v3 project running a later upgrade, after a future template
release added some new file under `.claude/agents/`, `.claude/hooks/`, or
alongside `.claude/settings.json`, would have had that Claude-only file
copied back in even though the project deliberately has no Claude Code
mechanics. Symmetrically, a no-frontend v3 project could have had
`docs/design/`, a tokens file, `design-loop`, or `design-reviewer.md`
resurrected the same way.

Fixed by prefixing the Phase 3-A absent-file rule with the same Phase
1-recovered gating `render.py` and Phase 3-D use: any file under
`.claude/agents/`, `.claude/hooks/`, `.claude/settings.json`, or the
`CLAUDE.md` symlink is absent-but-NOT-additive unless `claude-code` is in
the roster; `docs/design/`, a profile's tokens file,
`.claude/skills/design-loop/`, and `.claude/agents/design-reviewer.md` are
absent-but-NOT-additive unless the project has a frontend. Annotated the
rule's own example file list (`security-reviewer.md`,
`design-reviewer.md`, `deps-guard.sh`) with which gate each one is subject
to, so the example doesn't contradict the new caveat.

Verified: `python3 .github/scripts/golden_test.py` alone (no `--update`
needed, confirmed unaffected since `upgrade-project/SKILL.md` isn't part
of the render pipeline) -- 9/9 fixtures still byte-for-byte green.
Committed as `fix(upgrade): roster/frontend-gate the ordinary absent-file
copy rule` (`2724ea9`) and pushed.

## Concerns (not fixed — outside the stated scope)

1. ~~**`docs/SECURITY.md` universal-risk item 3**~~ -- **RESOLVED**, see
   "Coordinator follow-up" above (commit `3339efc`). Was: unconditionally
   claimed "Enforced by the `deps-guard` hook, not by trust" in the
   un-fenced "Universal risks and defenses" section, false for a non-Claude
   roster where the hook is never generated. Originally left as an
   out-of-scope concern since Fix 5 scoped only the Enforcement-section
   bullet; the coordinator asked for it explicitly as a follow-up and it is
   now fixed.
2. **Fix 1's scope reading.** The task's wording for the `tests` field could
   be read either as "these checks apply only to `done` features" or "these
   checks apply to every tests entry, only `isfile()` is gated on `done`". I
   implemented the latter (broader) reading, matching the task's explicit
   negative-test list, which includes `tests: ["/etc/passwd::x"]` and
   `tests: ["../x.py::t"]` failing without specifying `status: done`. If the
   intent was actually the narrower reading, `todo`/`in-progress` features
   with malformed (but currently harmless, since unused) test-path strings
   will now also fail the check — flagging this in case it's a surprise.
3. **No golden fixture exercises the CC-HOOKS-absent + AI-features-on
   combination simultaneously**, though the two fence families are
   independent and each is exercised separately across the 9 fixtures.
