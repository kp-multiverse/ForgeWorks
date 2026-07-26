<!-- FW-BLOCK: project v3.0.0 -->
<project>
Pillarwatch -- A self-hosted status page that shows the up/down history of a small team's own services, no third-party dependency.
Primary user: An on-call engineer at a small team who wants an honest status page without paying for or trusting a SaaS status vendor.. Stack: Go; frontend: yes-minimal; AI features: none. Dev container: no (if yes, commands run inside it).

Where things live:
- `docs/PRODUCT_VISION.md` -- positioning, differentiator, success metrics. Every feature's `serves:` line points back here.
- `docs/features.json` -- the ordered, machine-checked feature list (intent, acceptance criteria, test mapping, status, tier). This is the spec; prose elsewhere is commentary. Array order is priority order.
- `docs/design/DESIGN.md` + `docs/design/mockups/` -- visual direction, tokens, and the aesthetic rubric; a committed, approved mockup is the spec for its surface. (Frontend projects only.)
- `docs/SECURITY.md` -- threat model and red-team checklist.
- `docs/gotchas.md` -- pitfalls this project has already paid for. `docs/deviations.md` -- logged implementation deviations. `docs/plans/` -- approved plans for high-risk work.
- `docs/language-standards.md` -- toolchain conventions. `docs/documentation.md` -- library-doc links; Context7 MCP is wired for live API lookups, so verify unfamiliar or version-sensitive APIs there instead of writing them from memory.

Code style anchor: Pattern-match every file you write or modify to the single-binary, no-frills operational feel of Uptime Kuma. Reference material: https://github.com/louislam/uptime-kuma. 
</project>
<!-- /FW-BLOCK: project -->

<!-- FW-BLOCK: commands v3.0.0 -->
<commands>
- Quality gate (verify-only: lint, format check, types, unit + functional tests): `bash scripts/qa.sh`
- Auto-fix formatting/lint: `bash scripts/fix.sh`
- End-to-end suite (slower; also runs in CI): `bash scripts/e2e.sh`
- Feature-list check (schema + done features cite existing tests): `python3 scripts/features_check.py`
Package manager and install commands: `docs/language-standards.md`. New dependencies go through the manifest and the deps-guard hook (re-run with `DEPS_VETTED=1` once vetted).
</commands>
<!-- /FW-BLOCK: commands -->

<!-- FW-BLOCK: etiquette v3.0.0 -->
<etiquette>
- Conventional Commits (`feat:`, `fix:`, `docs:`, ...). Branch per feature; CI green before merge.
- One writer per branch: when a subagent reports its work complete, the orchestrator owns the branch from that moment, and vice versa.
- Work inside this repo only unless explicitly asked otherwise.
</etiquette>
<!-- /FW-BLOCK: etiquette -->

<!-- FW-BLOCK: hard-rules v3.0.0 -->
<hard-rules>
Few and absolute -- each holds with no exceptions:
- Never weaken, skip, delete, or comment out a failing test to make a gate pass. Changing existing tests, fixtures, or gate config requires a stated reason in the review notes.
- Never commit secrets. Env or a secret store, never source, prompts, or committed config.
- Never set a `features.json` status to `done` unless its mapped tests exist and pass; never delete an entry (set `status: dropped` with the reason in `notes`).
- When work matches the security trigger in the `security-review` skill, that review runs before merge.
</hard-rules>
<!-- /FW-BLOCK: hard-rules -->

<!-- FW-BLOCK: risk-tiers v3.0.0 -->
<risk-tiers>
Pick the tier by judgment against this table; the `slice` skill has the per-tier procedure.

| Tier | Typical work | Ceremony |
|---|---|---|
| light | copy, styling tweaks, small fixes, internal refactors | build it; quality gate green (no `features.json` entry needed) |
| standard | a new feature or behavior change | short plan, tests first (Red -> Green), scoped code review; design review if user-visible |
| high-risk | auth, payments, security-trigger matches, architecture changes | user-approved plan in `docs/plans/` + security review + full test pyramid |

Human approval is needed in exactly two places: the mockup pick for a NEW user-visible surface, and high-risk plans. Everything else proceeds -- deviations get the conservative choice and a `docs/deviations.md` line, and the owner reviews diffs.
</risk-tiers>
<!-- /FW-BLOCK: risk-tiers -->

<!-- FW-BLOCK: learning v3.0.0 -->
<learning>
- When reality surprises you (an API behaves differently than documented, a gate passes but the feature is dead), add the lesson to `docs/gotchas.md`.
- When implementation must deviate from the plan or mockup, take the conservative option, log it in `docs/deviations.md`, and keep going.
</learning>
<!-- /FW-BLOCK: learning -->

<!-- FW-BLOCK: roster v3.0.0 -->
<roster>
Skills (on demand): `slice` (per-feature workflow, tiered), `design-loop` (mockup -> build -> screenshot-verify; frontend projects), `security-review` (the trigger definition + procedure), `tech-debt` (on-demand sweep), `select-agents` (change the agent roster). Upstream: `tdd` (Red -> Green -> Refactor), `grill-me` (plan interrogation for high-risk work).

Subagents: `@implementer` (green-phase work in an isolated context), `@code-reviewer` (correctness + requirements review; its Stop hook re-runs the quality gate), `@security-reviewer` (red-team pass on trigger), `@design-reviewer` (grades shipped screens against the approved mockup + rubric; frontend projects), `@utility` (mechanical chores). Parallel agents only for read-only work; one writer at a time.
Subagents exist when Claude Code drives. On other rosters, run the same reviews as independent fresh-context passes -- the skills above define what each pass checks.
</roster>
<!-- /FW-BLOCK: roster -->

<!--
Project: Pillarwatch
Goal: A self-hosted status page that shows the up/down history of a small team's own services, no third-party dependency.
Primary user: An on-call engineer at a small team who wants an honest status page without paying for or trusting a SaaS status vendor.
Language: Go
Frontend: yes-minimal
AI features: none
Bootstrapped: 2026-07-26
-->
