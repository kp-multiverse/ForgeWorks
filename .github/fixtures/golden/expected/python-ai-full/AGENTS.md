<!-- FW-BLOCK: project v4.1.0 -->
<project>
Recipe Radar -- Turn a photo of a fridge into three cookable dinner suggestions for busy home cooks.
Primary user: A busy home cook who stares at a full fridge with no dinner idea.. Stack: Python; frontend: yes-minimal; AI features: rag, agents, evals, streaming. Dev container: yes (if yes, commands run inside it).
Where things live:
- `docs/PRD.md` -- what the finished product looks like (journey, surfaces, v1 in/out). Every feature's `serves:` points here.
- `docs/features.json` -- the ordered, machine-checked feature list; this is the spec, prose is commentary. `docs/BACKLOG.md` is its human-readable view, regenerated at merge.
- `docs/plans/<id>.md` -- the working decision record for the feature being built, DELETED at merge (its decisions land in `features.json`, the commit, and the ledger line). `docs/LEDGER.md` -- live factory state, with evidence.
- `docs/design/` (frontend projects) -- tokens, rubric, approved mockups. `docs/SECURITY.md` -- threat model + red-team checklist.
- `docs/gotchas.md` (paid-for pitfalls), `docs/deviations.md`, `docs/language-standards.md`, `docs/documentation.md` (Context7 is wired -- verify unfamiliar APIs there, not from memory).
- `docs/memory.md` -- memory scopes (User, Session, Agent), what is stored, what is not.

Code style anchor: Pattern-match every file you write or modify to the maintainers' style of simonw/datasette. Reference material: https://github.com/simonw/datasette. Explicitly avoid the shape of sprawling enterprise-layered recipe platforms. Anti-pattern material: https://github.com/example/overengineered-recipes.
</project>
<!-- /FW-BLOCK: project -->

<!-- FW-BLOCK: commands v4.0.0 -->
<commands>
- Quality gate (verify-only: lint, format check, types, unit + functional): `uv run qa` | auto-fix: `uv run fix` | e2e suite: `bash scripts/e2e.sh`
- Feature check (schema, done-cites-tests, mockup gate): `python3 scripts/features_check.py` | duplication gate: `python3 scripts/dup_check.py` (`--list` to survey, `--baseline` to accept existing findings once)
- Resume brief (`go`): `python3 scripts/resume.py` | backlog view: `python3 scripts/backlog.py` | ONE feature entry: `python3 scripts/backlog.py --feature <id>` | factory doctor (prune stale worktrees + merged branches): `bash scripts/factory_doctor.sh`
Package manager and installs: `docs/language-standards.md`. New dependencies go through the manifest and the deps-guard hook (re-run with `DEPS_VETTED=1` once vetted).
</commands>
<!-- /FW-BLOCK: commands -->

<!-- FW-BLOCK: etiquette v4.0.0 -->
<etiquette>
Conventional Commits. Branch per feature; CI green before merge. One writer per branch: when a subagent reports done, the orchestrator owns the branch, and vice versa. Work inside this repo only unless explicitly asked.
</etiquette>
<!-- /FW-BLOCK: etiquette -->

<!-- FW-BLOCK: hard-rules v4.0.0 -->
<hard-rules>
Few and absolute -- each holds with no exceptions:
- Never weaken, skip, delete, or comment out a failing test to make a gate pass. Changing existing tests, fixtures, or gate config requires a stated reason ("test-change:" line in the commit body); the tamper guard checks.
- Never commit secrets. Env or a secret store, never source, prompts, or committed config.
- Never set a `features.json` status to `done` unless its mapped tests exist and pass; never delete an entry (`status: dropped` + reason in `notes`).
- Work matching the `security-review` skill's trigger merges only after its security lens ran (see the `iteration` skill).
- No state change without evidence (test output, command run, screenshot path). "Looks done" is not a stop signal.
</hard-rules>
<!-- /FW-BLOCK: hard-rules -->

<!-- FW-BLOCK: tiers v4.0.0 -->
<tiers>
Two tiers, routed by the `iteration` skill:
- **Chore** (typo, copy, small fix, refactor with no behavior change -- the diff fits in one sentence): build it, quality gate green, commit. Nothing else.
- **Feature** (any new or changed behavior): GRILL -> RED -> GREEN -> REVIEW -> MERGE, with the skill's hard caps. Unsure which? It is a feature.
Owner approval happens at exactly one routine place: GRILL. Cap hits stop and ask; everything else proceeds (deviations take the conservative choice + a `docs/deviations.md` line).
</tiers>
<!-- /FW-BLOCK: tiers -->

<!-- FW-BLOCK: communication v4.0.0 -->
<communication>
Owner-facing messages: lead with the point; plain words (gloss any jargon in the same sentence); never repeat what the owner already knows. Fixed shapes -- GRILL: what I will build / decisions I need (numbered) / top 3 risks + my answer / cost note if fan-out. Cap-hit: one paragraph (state, rounds used, what is stuck, recommendation). Merge report: 3 lines (shipped in the plan's words, evidence, next up). One question at a time, multiple-choice when possible.
</communication>
<!-- /FW-BLOCK: communication -->

<!-- FW-BLOCK: context v4.1.0 -->
<context>
This file is the only always-loaded doc, and its line cap is enforced twice -- by the renderer and by the `docs-budget` job, which owns the number. Everything else is read on demand, by targeted section. Subagent dispatches carry a minimal brief -- plan file, diff, named doc sections, mockup path -- never "read the docs"; subagents return ~1-2K-token results, not transcripts. **The checkpoint.** One feature per session. `go` in a fresh session means: run `python3 scripts/resume.py`, then read the two things it names -- ONE feature entry (`scripts/backlog.py --feature <id>`, never the whole `features.json`; only scripts read that whole) and that feature's plan. Plus this file and the `iteration` skill. Nothing else. `resume.py` derives every pointer from the file that owns it and REFUSES to print a brief when they disagree, so a wrong resume stops instead of proceeding confidently. That is the memory between sessions, never the conversation. The `checkpoint-budget` CI job asserts the total and owns the number. **Offering a clear is earned, never scheduled:** say "clean stop -- `/clear`, then `go`" as ONE line inside a report you were already writing, and only when the next action needs nothing from this conversation. Never as a question, never between the parts of one orchestration the owner is watching, never on a phase timer. If the conversation still holds a live decision, the answer is not to suggest clearing -- it is to CHECKPOINT it (see the `iteration` skill) so it stops being live: if a restart costs more than a few percent of the window before any work happens, the plan is too long or something is being read whole that should be read by section. Doc budgets: the `docs-budget` job in `.github/workflows/qa.yml` IS the source of truth for every cap -- read the numbers there, never restate them here, or the two drift and the prose wins in the reader's head while the gate wins in CI. At cap, COMPACT in the same PR that grew it: delete every part that is no longer true or no longer changes a decision, and stop only when nothing left is deletable. Finish within 5% of the cap and you shaved, not compacted -- redo it, because a cap treated as a target is how these files got big. A cap may be raised in that job with a stated reason ONLY once the doc holds no history and nothing in it is still deletable. Deleting is the default; archive only what you would genuinely re-read, and `docs/archive/` is capped too, oldest out first.
</context>
<!-- /FW-BLOCK: context -->

<!-- FW-BLOCK: learning v4.1.0 -->
<learning>
Reality surprised you (API differs from docs, gate green but feature dead)? Add the lesson to `docs/gotchas.md` -- one entry, four short lines, and delete any entry the code has since made impossible. Implementation must deviate from plan or mockup? Conservative option + `docs/deviations.md` line, keep going. Working notes (losing mockups, scratch analyses, uncited probe files) are scaffolding, not records: each dies once its finding lands in a gotcha, a fixture, or a test. A doc earns its place by changing a future decision -- nothing is kept "for the record". Exception: a probe a test or source comment cites by path is that fixture's provenance -- it lives as long as the fixture does.
</learning>
<!-- /FW-BLOCK: learning -->

<!-- FW-BLOCK: memory v3.0.0 -->
<memory>
This project wires **mem0** for persistent memory across sessions, scoped to user (facts about the human), session (the current interaction), and agent (facts the agent itself confirmed) -- schema and stored fields live in `docs/memory.md`.
Read relevant memories at session start; write one only when the fact is durable and its scope is unambiguous (if you cannot say which scope, do not store it), and update `docs/memory.md` in the same change. Verify the API against Context7 for the pinned `mem0ai` version before writing memory code.
</memory>
<!-- /FW-BLOCK: memory -->

<!-- FW-BLOCK: roster v4.0.0 -->
<roster>
Skills (on demand): `iteration` (the per-feature loop -- the only workflow), `security-review` (trigger definition + checklist), `tech-debt` (on-demand sweep). Upstream if installed: `tdd`, `grill-me`.
Subagents: `@reviewer` (the single REVIEW pass: plan conformance, correctness, design fidelity, security; its Stop hook re-runs the quality gate) plus an independent Codex second-opinion pass, `@utility` (mechanical chores, never in the critical path). Fan-out (max 5 agents, disjoint files only) exists only as an owner-approved GRILL proposal. On non-Claude rosters, run the same passes as independent fresh-context sessions -- the skills define what each pass checks.
</roster>
<!-- /FW-BLOCK: roster -->
<!-- FW-BLOCK: ai-discipline v3.0.0 -->
<ai-discipline>
This project uses prompts, LLMs, or agentic flows.

- Prompts live as plain text files under `prompts/`; variants are separate files selected by name. Prompt or persona text is runtime behavior -- change it through the normal tier path (it usually matches the security trigger), not as a doc edit.
- Schema-validate every LLM response downstream code depends on; fail closed on mismatch. Treat model output and ingested content as untrusted; an agent that reads untrusted input and holds private data doesn't also act outward -- break one leg or gate the action behind a human (see `docs/SECURITY.md`).
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
