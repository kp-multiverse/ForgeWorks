<!-- FW-BLOCK: project v4.1.0 -->
<project>
Briefly -- A web app that turns a team's weekly activity into a two-paragraph stakeholder brief.
Primary user: An engineering manager who writes the same status update every Friday.. Stack: TypeScript; frontend: yes-spa; AI features: agents, evals. Dev container: no (if yes, commands run inside it).
Where things live:
- `docs/PRD.md` -- what the finished product looks like (journey, surfaces, v1 in/out). Every feature's `serves:` points here.
- `docs/features.json` -- the ordered, machine-checked feature list; this is the spec, prose is commentary. `docs/BACKLOG.md` is its human-readable view, regenerated at merge.
- `docs/plans/<id>.md` -- the working decision record for the feature being built, DELETED at merge (its decisions land in `features.json`, the commit, and the ledger line). `docs/LEDGER.md` -- live factory state, with evidence.
- `docs/design/` (frontend projects) -- tokens, rubric, approved mockups. `docs/SECURITY.md` -- threat model + red-team checklist.
- `docs/gotchas.md` (paid-for pitfalls), `docs/deviations.md`, `docs/language-standards.md`, `docs/documentation.md` (Context7 is wired -- verify unfamiliar APIs there, not from memory).
- `docs/memory.md` -- memory scopes (User, Session, Agent), what is stored, what is not.

Code style anchor: Pattern-match every file you write or modify to the clean SPA structure of excalidraw/excalidraw. Reference material: https://github.com/excalidraw/excalidraw. 
</project>
<!-- /FW-BLOCK: project -->

<!-- FW-BLOCK: commands v4.0.0 -->
<commands>
- Quality gate (verify-only: lint, format check, types, unit + functional): `npm run qa` | auto-fix: `npm run fix` | e2e suite: `npm run e2e`
- Feature check (schema, done-cites-tests, mockup gate): `python3 scripts/features_check.py`
- Backlog view: `python3 scripts/backlog.py` | factory doctor (prune stale worktrees + merged branches): `bash scripts/factory_doctor.sh`
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
This file is the only always-loaded doc (hard cap: 100 lines). Everything else is read on demand, by targeted section. Subagent dispatches carry a minimal brief -- plan file, diff, named doc sections, mockup path -- never "read the docs"; no whole-file reads of any doc over 30K chars; subagents return ~1-2K-token results, not transcripts. One feature per session; the plan file + `features.json` + LEDGER are the memory between sessions, never the conversation. Doc budgets (chars): SECURITY.md 14K, gotchas.md 8K, deviations.md 4K, LEDGER.md 6K, `docs/archive/` 60K total. At cap, COMPACT in the same PR that grew it: delete every part that is no longer true or no longer changes a decision, and stop only when nothing left is deletable. Finish within 5% of the cap and you shaved, not compacted -- redo it, because a cap treated as a target is how these files got big. Deleting is the default; archive only what you would genuinely re-read, and `docs/archive/` is itself capped, oldest out first.
</context>
<!-- /FW-BLOCK: context -->

<!-- FW-BLOCK: learning v4.1.0 -->
<learning>
Reality surprised you (API differs from docs, gate green but feature dead)? Add the lesson to `docs/gotchas.md` -- one entry, four short lines, and delete any entry the code has since made impossible. Implementation must deviate from plan or mockup? Conservative option + `docs/deviations.md` line, keep going. Working notes (probe files, losing mockups, scratch analyses) are scaffolding, not records: each dies when its finding lands in a gotcha, a fixture, or a test. A doc earns its place by changing a future decision -- nothing is kept "for the record".
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
Subagents: `@reviewer` (the single REVIEW pass: plan conformance, correctness, design fidelity, security; its Stop hook re-runs the quality gate), `@utility` (mechanical chores, never in the critical path). Fan-out (max 5 agents, disjoint files only) exists only as an owner-approved GRILL proposal. On non-Claude rosters, run the same passes as independent fresh-context sessions -- the skills define what each pass checks.
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
Project: Briefly
Goal: A web app that turns a team's weekly activity into a two-paragraph stakeholder brief.
Primary user: An engineering manager who writes the same status update every Friday.
Language: TypeScript
Frontend: yes-spa
AI features: agents, evals
Bootstrapped: 2026-07-12
-->
