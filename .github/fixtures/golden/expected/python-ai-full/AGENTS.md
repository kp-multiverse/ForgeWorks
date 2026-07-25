<!-- FW-BLOCK: project v3.0.0 -->
<project>
Recipe Radar -- Turn a photo of a fridge into three cookable dinner suggestions for busy home cooks.
Primary user: A busy home cook who stares at a full fridge with no dinner idea.. Stack: Python; frontend: yes-minimal; AI features: rag, agents, evals, streaming. Dev container: yes (if yes, commands run inside it).

Where things live:
- `docs/PRODUCT_VISION.md` -- positioning, differentiator, success metrics. Every feature's `serves:` line points back here.
- `docs/features.json` -- the ordered, machine-checked feature list (intent, acceptance criteria, test mapping, status, tier). This is the spec; prose elsewhere is commentary. Array order is priority order.
- `docs/design/DESIGN.md` + `docs/design/mockups/` -- visual direction, tokens, and the aesthetic rubric; a committed, approved mockup is the spec for its surface. (Frontend projects only.)
- `docs/SECURITY.md` -- threat model and red-team checklist.
- `docs/gotchas.md` -- pitfalls this project has already paid for. `docs/deviations.md` -- logged implementation deviations. `docs/plans/` -- approved plans for high-risk work.
- `docs/language-standards.md` -- toolchain conventions. `docs/documentation.md` -- library-doc links; Context7 MCP is wired for live API lookups, so verify unfamiliar or version-sensitive APIs there instead of writing them from memory.
- `docs/memory.md` -- memory scopes (User, Session, Agent), what is stored, what is not.

Code style anchor: Pattern-match every file you write or modify to the maintainers' style of simonw/datasette. Reference material: https://github.com/simonw/datasette. Explicitly avoid the shape of sprawling enterprise-layered recipe platforms. Anti-pattern material: https://github.com/example/overengineered-recipes.
</project>
<!-- /FW-BLOCK: project -->

<!-- FW-BLOCK: commands v3.0.0 -->
<commands>
- Quality gate (verify-only: lint, format check, types, unit + functional tests): `uv run qa`
- Auto-fix formatting/lint: `uv run fix`
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
| light | copy, styling tweaks, small fixes, internal refactors | build it; quality gate green |
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

<!-- FW-BLOCK: memory v3.0.0 -->
<memory>
This project uses **mem0** for persistent memory across sessions.

**Scopes:**
- User: facts about the human (preferences, profile, history).
- Session: facts about the current interaction.
- Agent: facts the agent itself has confirmed during work.

**Before writing memory code:**
- Decide which scope a piece of data belongs in. If you cannot say, do not store it.
- Update `docs/memory.md` with the new schema entry.
- Verify the API against Context7 for the pinned `mem0ai` version.

**Library docs:** https://docs.mem0.ai/
</memory>
<!-- /FW-BLOCK: memory -->

<!-- FW-BLOCK: roster v3.0.0 -->
<roster>
Skills (on demand): `slice` (per-feature workflow, tiered), `design-loop` (mockup -> build -> screenshot-verify; frontend projects), `security-review` (the trigger definition + procedure), `tech-debt` (on-demand sweep), `select-agents` (change the agent roster). Upstream: `tdd` (Red -> Green -> Refactor), `grill-me` (plan interrogation for high-risk work).

Subagents: `@implementer` (green-phase work in an isolated context), `@code-reviewer` (correctness + requirements review; its Stop hook re-runs the quality gate) plus an independent Codex second-opinion pass, `@security-reviewer` (red-team pass on trigger), `@design-reviewer` (grades shipped screens against the approved mockup + rubric; frontend projects), `@utility` (mechanical chores). Parallel agents only for read-only work; one writer at a time.
</roster>
<!-- /FW-BLOCK: roster -->
<!-- FW-BLOCK: ai-discipline v3.0.0 -->
<ai-discipline>
This project uses prompts, LLMs, or agentic flows.

- Prompts live as plain text files under `prompts/`; variants are separate files selected by name. Prompt or persona text is runtime behavior -- change it through the normal tier path (it usually matches the security trigger), not as a doc edit.
- Schema-validate every LLM response downstream code depends on; fail closed on mismatch. Treat model output and ingested content as untrusted; never give one agent untrusted input + private data + outward actions (break one trifecta leg -- see `docs/SECURITY.md`).
- In tests, key LLM fakes off rendered state, not call ordinal. Bound every model loop or retry with a spend cap.
</ai-discipline>
<!-- /FW-BLOCK: ai-discipline -->
<!--
Project: Recipe Radar
Goal: Turn a photo of a fridge into three cookable dinner suggestions for busy home cooks.
Primary user: A busy home cook who stares at a full fridge with no dinner idea.
Language: Python
Frontend: yes-minimal
AI features: rag, agents, evals, streaming
Bootstrapped: 2026-07-12
-->
