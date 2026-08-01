---
name: init-project
description: Bootstrap a new project through a short conversation (at most 5 questions -- the agent infers everything else and states its defaults) that ends in an owner-approved one-page PRD, then generates two focused subagents (reviewer, utility), the `iteration` skill (the one per-feature workflow: chores build straight through, features run GRILL -> RED -> GREEN -> REVIEW -> MERGE), a machine-checked feature list (docs/features.json: two tiers chore/feature, a surface + mockup field, enforced in CI), docs/PRD.md, docs/LEDGER.md, docs/BACKLOG.md, a static+test quality-gate hook, a tamper guard, a supply-chain guard hook, Context7 MCP, CI (a fast gate, a separate end-to-end job, and a features-check job), PR template, pre-commit config, dev container, a threat-model doc, and structured documentation. Stack-agnostic at its core: language and tooling choices live in this skill's interview, not in the template files. Use this skill whenever a project is uninitialized (no docs/features.json or .claude/agents/), when the user says "init", "bootstrap", "set up this project", "/init-project", or describes wanting to start a new AI engineering project. Generates AGENTS.md, .claude/ (the reviewer/utility agents, hooks, and the iteration/security-review/tech-debt skills), .mcp.json, docs/ (including features.json and, for frontend projects, docs/design/), .github/, .devcontainer/, scripts/ (features_check.py, backlog.py, tamper_check.py, factory_doctor.sh), and a manifest tailored to the chosen language. Pairs with the upstream `tdd` and `grill-me` skills from mattpocock/skills, installed during bootstrap.
---

# init-project

This skill bootstraps a new project with a structured, agent-driven workflow. The template's contents are stack-agnostic; all language and tooling choices are made through this skill's interview, then substituted into placeholders at generation time.

## When this skill runs

- The current directory is empty or contains only a bootstrap `AGENTS.md`.
- The user says: "bootstrap", "init", "set up the project", "/init-project", or similar.
- The user describes wanting to start a new project.

## What this skill produces

A fully structured project with:

- `AGENTS.md` and `CLAUDE.md` (symlinked): the constitution, stack-agnostic core, hard-capped at 100 lines
- `.claude/agents/`: `reviewer` (the single REVIEW pass: plan conformance, correctness, design fidelity, security) and `utility` (mechanical chores)
- `.claude/skills/`: the generated skills `iteration` (the one per-feature workflow: chore or GRILL -> RED -> GREEN -> REVIEW -> MERGE), `security-review`, and `tech-debt`
- `.claude/hooks/quality-gate.sh`: deterministic static+test gate triggered by the reviewer's Stop hook
- `.claude/hooks/deps-guard.sh` + `.claude/settings.json`: best-effort supply-chain guard (PreToolUse hook)
- `.mcp.json`: Context7 MCP server for live library docs
- `.github/workflows/qa.yml`: CI running the quality gate (fast), a separate end-to-end job, and a `features-check` job that validates `docs/features.json`, on pull requests and pushes to main
- `.github/pull_request_template.md`: short PR checklist
- `.pre-commit-config.yaml`: local pre-commit hooks (language-specific portion populated from your profile)
- `docs/`: living documentation -- `PRD.md` (the owner-approved one-page product picture: journey, surfaces, v1 in/out -- every feature's `serves:` line cites it), `features.json` (the machine-checked spec: intent, acceptance, tests, status, tier [`chore`/`feature`], surface, mockup), `BACKLOG.md` (the generated human-readable view of `features.json`), `LEDGER.md` (live factory state, evidence per line), `SECURITY.md`, `language-standards.md`, `documentation.md`, `gotchas.md`, `proposals-ideas.md`, `deviations.md`, `plans/` (+ `plans/archive/` for merged features), `archive/` (overflow when a budgeted doc grows past its cap), `probes/`, `agents.md` + `agents.json`, and -- for frontend projects -- `design/` (`DESIGN.md` + `mockups/`)
- `scripts/features_check.py`: validates `docs/features.json` against its schema; also runs as the CI `features-check` job
- `scripts/backlog.py`: regenerates `docs/BACKLOG.md` from `docs/features.json`
- `scripts/tamper_check.py`: flags an unexplained change to a test, fixture, or gate config (the hard-rules tamper guard)
- `scripts/factory_doctor.sh`: prunes stale git worktrees and merged feature branches
- `.devcontainer/`: portable development environment (if chosen)
- `README.md` + `.env.example`: project readme (commands, flow) and a documented, secret-free env template
- A minimal green scaffold for the chosen language (a placeholder module + a passing test) so the quality gate passes on the first run
- The chosen language's runners: a non-mutating quality gate (`qa`), a local auto-fix (`fix`), and a separate end-to-end runner (shell scripts for Python/Go/Rust, npm scripts for TypeScript)
- `{{MANIFEST_FILE}}`: dependency + tool config + bundled scripts entry
- A working venv / node_modules / equivalent via the chosen package manager (skipped if dev container is chosen; deps install inside the container instead)

The TDD methodology is provided by the upstream `tdd` skill from `mattpocock/skills`, installed during this skill's Phase 1. The `iteration` skill is the only per-feature workflow: chores build straight through the quality gate; features run GRILL -> RED -> GREEN -> REVIEW -> MERGE with hard caps. Main context drives GRILL and GREEN itself -- there is no implementer subagent; `@reviewer` is the escape hatch for the single REVIEW pass (fresh context, evidence required, four lenses: plan conformance, correctness, design fidelity, security), and `@utility` handles mechanical chores off the critical path.

---

## Workflow

### Phase 0: Confirm intent

Before doing anything, confirm with the user:

> "I'm going to bootstrap this project. I'll ask you a few questions about scope and stack, then generate the full structure. Continue?"

Wait for explicit confirmation.

### Phase 1: Install supporting skills (REQUIRED)

The core loop uses **`mattpocock/skills`** -- specifically `tdd` and `grill-me`. This is a deliberate choice: in practice these gave a better experience than the broader `superpowers` pack, so use `mattpocock/skills` as the default and do not substitute another pack for the core loop.

**Always pull the latest.** Skill packs evolve; run the install (which resolves `@latest`) every bootstrap, even if some skills look already present, so the project starts on current versions:

```bash
npx skills@latest add mattpocock/skills
```

Required skills (must be installed): `tdd`, `grill-me`, `to-prd`, `caveman`, `write-a-skill`, `handoff`.

After the user picks them in the skills picker, verify `tdd` and `grill-me` are present before proceeding. `grill-me` is what powers the planning pass (Phase 2's conversation, and the `iteration` skill's GRILL step for every feature); do not skip it. If the user refuses or skips, stop and explain why bootstrap cannot continue without `tdd` and `grill-me`.

### Phase 2 -- the conversation (at most 5 questions)

This is a conversation, not a form: run the `grill-me` skill (from
mattpocock/skills) to drive it; if unavailable, mirror its style -- probe
assumptions, surface trade-offs, ask the follow-up. Collect answers directly
into `docs/_init-answers.json` as you go -- the renderer input whose schema is
defined in Phase 4 (deleted partway through Phase 5, before the quality-gate
run -- see Phase 5). Rule zero: **nothing this conversation can elicit ships
as a TODO in the generated docs.** When an answer is vague, grill it: "How
would you verify that?", "What breaks first?", "Give me a real example input
and output."

Open with ONE prompt: "Describe the product you want -- what it does, for
whom, and anything you already know you want technically." Then infer
everything possible from the answer and ask ONLY what is missing from this
list, one question at a time, multiple-choice where possible:

1. **What & for whom** -- only if the description left the product or its
   primary user unclear.
2. **Language** -- only if not inferable (menu: Python / TypeScript / Go /
   Rust; "Other" is not built). "A CLI in Rust" needs no question.
3. **Frontend?** -- infer from the product type when obvious. If yes, ONE
   follow-up: "Name a product whose look you like, and one you hate"
   (feeds the design tokens and anti-reference). If the language is Go or
   Rust, say so honestly: those profiles ship no `tokens.css` yet --
   `docs/design/DESIGN.md` still renders with its tokens section, but there
   is no starter tokens file to edit until one is added to the profile.
4. **Security-sensitive?** -- "Will this hold real user data, payments,
   auth, take input from strangers, or send data out to external systems?"
   Shapes the SECURITY.md defaults and the AI-security fences (the
   outbound leg answers `acts_outward` directly, instead of guessing it).
5. **Which agents drive** -- the roster question, asked as one question.
   PROBE first, do not guess: check which agent CLIs are installed
   (`command -v codex`, `command -v cursor`, `command -v agy || command -v
   antigravity`, `command -v gemini`, plus any the user names). Claude Code
   counts as installed when this interview runs inside it. Options:
   claude-code / codex / antigravity / cursor / other (multi-select; default
   `claude-code` alone; at least one required; a selected-but-not-installed
   agent is recorded with `"status": "planned"`). If `claude-code` is NOT
   selected, warn that the Claude-specific enforcement stack (subagents,
   hooks, settings, the `CLAUDE.md` symlink) will not be generated, but
   `.claude/skills/` (`iteration`, `security-review`, `tech-debt`) still
   ships as plain-markdown procedures for the driving agent to read and
   follow manually.

Everything else takes the documented default (Phase 4 table): devcontainer
yes, explanations no, gotchas seed yes, mem0 no, codex reviewer only if
codex is in the roster. Say which defaults were applied; each is one answer
-file line to change later.

Derive and confirm: project name/slug, goal, primary user, core problem,
core journey, surfaces list (screens/pages; empty for API/CLI), in-scope
list, non-goals, success metrics, differentiator, current alternative --
these fill `docs/PRD.md`. Close Phase 2 by showing the owner the drafted
one-page PRD content and the five-line summary
("<language> <product-type>, frontend: <y/n>, security-sensitive: <y/n>,
agents: <list>, defaults applied: <n>") and getting an explicit OK -- the
PRD is owner-approved BEFORE the render.

### Phase 3: Confirm the plan

Phase 2 already showed the owner the drafted `docs/PRD.md` content and the
five-line summary, and got an explicit OK before this point -- do not
re-litigate it here. Apply any last corrections the owner raised at the end
of Phase 2, state the file count this will create (roughly N files), and move
to Phase 4. If the owner has not yet given an explicit OK, stay in Phase 2;
Phase 4 never runs on an implied yes.

### Phase 4: Generate the scaffold (deterministic render)

Generation is executed by the bundled renderer, **`render.py`**, never by hand.
Your whole job in this phase is to produce a correct answers file; the renderer
guarantees that the same answers always produce the same bytes (the template
repo's CI proves this against committed golden fixtures).

A generated project is **the universal core plus exactly one language profile**
-- nothing from any other language is ever copied in. Three source folders feed
the renderer:

- `templates/core/` -- language-free files every project gets (AGENTS.md, docs/, `.mcp.json`, the CI workflow shape, PR template, README, .env.example, `.claude/`).
- `templates/profiles/<language>/` -- the chosen language's files (manifest, toolchain config, `scripts/` or package scripts, the green scaffold, `.gitignore`, dev container, and -- Python only -- a pre-commit config), plus `profile.json`: the machine-readable toolchain values the renderer substitutes. `profile.json` is renderer input only and never lands in the generated project. Keep it in sync with the YAML block in `<language-profiles>` below (CI cross-checks the load-bearing values).
- `templates/conditional/` -- the canonical texts of the conditional blocks: `ai-discipline.md`, `memory-block.md`, `memory-doc-line.md`, `codex-review-step.md`, `codex-roster-note.md`, `gotchas-seed.md`, the per-agent roster snippets under `agents/`, and the roster-wide `agents/no-claude-note.md` (rendered when `claude-code` is absent). Edit them THERE; this file only points at them.

**Step 1 -- write the answers file** at `docs/_init-answers.json`, exactly in
this schema. All top-level keys (`schema`, `date`, `agents`, `project`,
`stack`, `security`, `opt_ins`, `features`, `design`) and every key within the
four object sections are required; yes/no fields are the literal strings
`"yes"`/`"no"`; multi-line values use `\n`. Example (values abbreviated --
yours carry the real interview content):

```json
{
  "schema": 1,
  "date": "2026-07-12",
  "agents": [{"name": "claude-code", "status": "installed"}],
  "project": {
    "name": "Recipe Radar",
    "slug": "recipe-radar",
    "goal": "Turn a photo of a fridge into three cookable dinner suggestions.",
    "primary_user": "A busy home cook ...",
    "core_problem": "...",
    "core_journey": "1. ...\n2. ...\n3. ...",
    "success_measure": "...",
    "success_metrics": "- metric -- target",
    "riskiest_assumption": "...",
    "req_ac_list": "- [ ] **REQ-AC1:** ...\n- [ ] **REQ-AC2:** ...",
    "non_goals": "- ...",
    "other_users": "- none identified yet",
    "constraint_time": "...",
    "constraint_cost": "...",
    "constraint_data": "...",
    "first_milestone": "2026-08-09 (or: none set)",
    "deployment_target": "...",
    "scale_expectations": "...",
    "integrations": "- none",
    "in_scope_list": "- ...",
    "pain_point": "...",
    "product_category": "...",
    "current_alternative": "...",
    "key_benefit": "...",
    "key_differentiator": "...",
    "positive_reference": {"ref": "simonw/datasette", "location": "https://github.com/simonw/datasette"},
    "negative_reference": null,
    "surfaces": ["Fridge photo upload", "Ingredient review", "Recipe results"]
  },
  "stack": {
    "language": "python",
    "has_frontend": "yes-minimal",
    "backend_framework": "FastAPI",
    "ai_features": ["rag", "agents"],
    "vector_db": "Chroma",
    "llm_provider": "OpenAI",
    "embeddings_model": "text-embedding-3-small",
    "database": "SQLite",
    "uses_devcontainer": "yes"
  },
  "security": {
    "reads_untrusted": "yes",
    "holds_private_data": "yes",
    "acts_outward": "no"
  },
  "opt_ins": {
    "explanations": "no",
    "seed_gotchas": "yes",
    "mem0": "no",
    "codex_reviewer": "no"
  },
  "features": [
    {
      "id": "F001",
      "title": "Extract an editable ingredient list from a fridge photo",
      "intent": "Uploading a clear fridge photo yields an editable ingredient list within 15 seconds.",
      "serves": "journey step 2: the app extracts an ingredient list and shows it for one-tap correction",
      "acceptance": ["Uploading a clear fridge photo produces an editable ingredient list within 15 seconds."],
      "tests": [],
      "status": "todo",
      "tier": "feature",
      "surface": "Ingredient review"
    },
    {
      "id": "F002",
      "title": "Suggest three cookable recipes",
      "intent": "Confirming the list yields exactly three recipe suggestions, each cookable with the confirmed ingredients plus pantry staples.",
      "serves": "journey step 3: the app retrieves three matching recipes and adapts each to the confirmed inventory",
      "acceptance": ["Confirming an ingredient list returns exactly three recipes, each cookable with those ingredients plus pantry staples."],
      "tests": [],
      "status": "todo",
      "tier": "feature",
      "surface": "Recipe results"
    }
  ],
  "design": {
    "references": "- datasette.io -- plain, content-first layout that gets out of the way\n- a well-lit recipe card: one photo, short ingredient list, numbered steps",
    "tone": "warm, uncluttered, mobile-first",
    "anti_reference": "cluttered recipe blogs: ad blocks, autoplay video, ingredient list buried under a life story"
  }
}
```

Every field in this schema is still required, even though Phase 2 asks at
most 5 questions for it -- inference is the interviewer's job, not a reason
to relax the renderer's contract. Fields Phase 2 does not name explicitly
(riskiest assumption, acceptance criteria, constraints, first milestone,
deployment target, scale, integrations, other user segments, the
codebase-shape reference) still need a value: derive one from the
conversation, or record `TODO(interview-skipped)` per rule zero if the owner
explicitly declined to go further.

Field rules the renderer enforces (it fails closed with a precise message):

- `slug`: lowercase ASCII words joined by hyphens (`my-project`) -- it becomes the package/module identifier.
- `language`: one of `python` / `typescript` / `go` / `rust`. `has_frontend`: `yes-spa` / `yes-minimal` / `no`. `ai_features`: any subset of `["rag", "agents", "evals", "streaming"]`; `[]` means no AI features.
- `surfaces`: a list of strings (`[]` for an API/CLI product with no screens); each named surface is available for a feature's `surface` field and for the `docs/PRD.md` Surfaces section.
- Free-text answers land verbatim in prose files (and escaped in JSON/TOML), so any characters are fine EXCEPT HTML comment markers (`<!--`/`-->`) and `{{UPPER_SNAKE}}`-shaped text, which the renderer rejects.
- Free-text fields that land in `AGENTS.md` (`goal`, `primary_user`, the style references) must be single-line -- the renderer hard-fails if the rendered `AGENTS.md` exceeds 100 lines (rule 22), and a wrapped multi-line answer is the easiest way to blow that cap.
- Rule zero still holds: no bare `TODO` in any answer. The only allowed form is `TODO(interview-skipped)` when the user explicitly refused a question. `date` is today, ISO format.
- `vector_db`, `llm_provider`, `embeddings_model`, `database`, `backend_framework`: write `none` (or `none (CLI/library)` for the framework) when not applicable.
- `agents` (top-level): non-empty list of `{"name", "status"}`; `name` one of `claude-code` / `codex` / `antigravity` / `cursor` / `other` (no duplicates), `status` `installed` or `planned`. `codex_reviewer: "yes"` requires `codex` in the roster.
- `features` (top-level, required, non-empty): each entry needs `id` (`F000`-`F999`, unique), `title`, `intent`, `serves` (names the `docs/PRD.md` section it serves -- e.g. "journey step 2" or "differentiator: <the key differentiator>"; if a feature cannot say which part of the PRD it serves, question the feature), `acceptance` (non-empty list of strings), `tests` (list of strings -- `[]` at bootstrap, filled in as the test files are named), `status` (all `"todo"` at bootstrap; `in-progress` / `done` / `dropped` only apply later), `tier` (`chore` or `feature` -- routes the `iteration` skill: a chore builds straight through the gate, a feature runs GRILL -> RED -> GREEN -> REVIEW -> MERGE), and `surface` (the entry from `project.surfaces` this feature touches, or `"none"` for API/CLI-only work). A feature whose `surface` is not `"none"` needs a `mockup` field (a `docs/design/mockups/...` path) before it can leave `todo` -- `scripts/features_check.py` enforces this; bootstrap-time features normally have none yet, so leave `mockup` unset. An optional key, `notes`, is unused at bootstrap (every feature starts `todo`) but becomes required later -- `scripts/features_check.py` fails a `dropped` feature that has no reason recorded in `notes`. Derive 3-7 features from the core journey, using the acceptance criteria drawn out in conversation as the source for each feature's `acceptance` array -- order them user-visible-journey-first (hardening and infra queue behind the first shippable surface).
- `design` (top-level): an object with `references`, `tone`, `anti_reference` -- collected from the frontend visual-reference follow-up in Phase 2 -- when `stack.has_frontend` is not `"no"`; `null` when it is `"no"`.

**Step 2 -- run the renderer** from the project root:

```bash
python3 .claude/skills/init-project/render.py \
  --answers docs/_init-answers.json \
  --core .claude/skills/init-project/templates/core \
  --profile .claude/skills/init-project/templates/profiles/<language> \
  --out .
```

If it fails, fix the answers file (or report the template bug) and re-run. Do
NOT hand-patch the generated tree around a renderer error and do NOT perform
any substitution manually -- that reintroduces exactly the nondeterminism this
renderer removed.

**What the renderer does.** Documentation of behavior, not manual steps -- the
canonical implementation is `render.py`, locked byte-for-byte by the golden
fixtures in the template repo CI:

| # | Rule (from the answers) |
|---|---|
| 1 | Substitutes every placeholder in the tables below (core + the chosen profile only), re-indenting multi-line values to the placeholder's own column so YAML stays valid. |
| 2 | Escapes free-text answers per target format: JSON-escaped in `.json`, TOML-escaped in `.toml`, verbatim in Markdown/text -- hostile quotes/newlines/braces land as text, never as structure. Free text in any other file type is a hard error. |
| 3 | AI features selected -> renders `{{AI_DISCIPLINE_BLOCK}}` from `templates/conditional/ai-discipline.md`; none -> empty. |
| 4 | AI fences: AI on -> strips only the marker lines and keeps the content; AI off -> deletes the whole fenced blocks in `docs/SECURITY.md` (AI-SECURITY, AI-REDTEAM), `.claude/agents/reviewer.md` (AI-REVIEW). |
| 5 | Style references: renders the positive/negative codebase-shape reference lines, or the "no positive reference yet" comment / empty string. |
| 6 | `opt_ins.explanations: no` -> `docs/explanations/` is not generated. |
| 7 | `opt_ins.seed_gotchas: yes` -> inserts the three starter entries from `templates/conditional/gotchas-seed.md` into `docs/gotchas.md`. |
| 8 | `opt_ins.mem0: yes` -> keeps `docs/memory.md`, renders `{{MEMORY_DOC_LINE}}` in `AGENTS.md`'s `<project>` block, and inserts the `<memory>` block (from `templates/conditional/memory-block.md`, see rule 21 for the anchor); `no` -> none of those. The `mem0ai` dependency itself is added in Phase 4.5. |
| 9 | `opt_ins.codex_reviewer: yes` -> renders `{{CODEX_REVIEW_STEP}}` and `{{CODEX_ROSTER_NOTE}}` from `templates/conditional/codex-*.md`; `no` -> both empty. |
| 10 | Seeds the security-profile line into `docs/SECURITY.md` from the `security` answers; if all three are `yes` AND AI features are on, appends the lethal-trifecta-PRESENT note to that same insertion. |
| 11 | `stack.uses_devcontainer: no` -> `.devcontainer/` is not generated. |
| 12 | `stack.has_frontend` + profile: renders `{{E2E_BROWSER_INSTALL_STEP}}` as the browser-install step (UI project with a profile `e2e_browser_install`) or the "no browser needed" comment. |
| 13 | Renames profile manifests shipped with an `.example` suffix (`pyproject.toml.example` -> `pyproject.toml`). Core files are never renamed (`.env.example` stays). |
| 14 | Creates the `CLAUDE.md` -> `AGENTS.md` symlink (a one-line pointer file where symlinks are unavailable), `chmod +x` on `.claude/hooks/*.sh` and `scripts/*.sh`, and stamps `.claude/.template-version` (with this release's version) if the bootstrap `install.sh` did not already write it. |
| 15 | Fails closed if any `{{...}}` placeholder survives anywhere in the output. |
| 16 | When `claude-code` is NOT in `agents`, `.claude/agents/`, `.claude/hooks/`, `.claude/settings.json`, and the `CLAUDE.md` symlink are not generated -- these are the Claude-specific enforcement mechanics (subagents, hooks, settings). `.claude/skills/` (`iteration`, `security-review`, `tech-debt`) ships regardless of roster: they are plain-markdown procedures any driving agent can read and follow, not Claude Code slash commands. `.claude/.template-version` is likewise always written by post-processing (rule 14) regardless of roster. A `claude-code` entry with `"status": "planned"` still counts as selected for this rule -- the agents/hooks/settings tree is still generated; `status` only affects `docs/agents.json` and the matrix status note (rule 17). |
| 17 | Renders `{{AGENT_MATRIX}}` in `docs/agents.md` from `templates/conditional/agents/<name>.md` (planned agents get a status note) and writes the machine-readable roster `docs/agents.json` (name, status, offload roles). When `claude-code` is NOT in `agents`, an honest-omission note (`templates/conditional/agents/no-claude-note.md`) is appended as the final section of `docs/agents.md`, spelling out what was skipped and that `docs/SECURITY.md` / `docs/language-standards.md` mandates -- and keeping `docs/features.json` current -- fall to the driving agent manually. |
| 18 | CC fences (same mechanic as AI fences, rule 4, keyed on "claude-code in `agents`" instead of `ai_features`): claude-code present -> strips only the marker lines; absent -> deletes the whole fenced block. Current instance: `<!-- CC-HOOKS-START/END -->` around the deps-guard hook bullet in `docs/SECURITY.md`'s Enforcement section (the hook is a Claude Code enforcement mechanic, so other rosters do not get the bullet). |
| 19 | Writes `docs/features.json` from the answers' `features` list (schema 1) and `docs/agents.json` from the roster; `docs/BACKLOG.md` and `docs/LEDGER.md` ship as static files (empty until the first feature ships and merges -- `scripts/backlog.py` and the `iteration` skill fill them in later, not the renderer). |
| 20 | Frontend projects: renders `docs/design/` (DESIGN.md + mockups/) and the profile tokens.css; `has_frontend: no` skips both (skip_file rule). There is no separate design agent or skill in v4.0.0 -- design fidelity is one of `@reviewer`'s four lenses, checked at the REVIEW step of the `iteration` skill, not a dedicated pass. |
| 21 | mem0 memory block inserts after `<!-- /FW-BLOCK: learning -->`. |
| 22 | `AGENTS.md` is capped at 100 lines after every substitution and insertion; the renderer raises if the rendered file exceeds it (context economy is a hard requirement of this rule, not a style preference). |

Keep `docs/_init-answers.json` until Phase 5's placeholder grep and
`features_check.py` pass, then delete it (`rm docs/_init-answers.json`)
BEFORE running the quality gate -- it is transient renderer working state,
not project content, and its content lives on in the rendered docs.

### Phase 4.5: Install dependencies

Dependency work is the one part of generation that stays with the agent: it
runs environment-dependent package-manager commands, so it cannot be a
deterministic file render. Two steps.

**First, capability dependencies** (from the backend framework, AI features,
LLM/embeddings, and database answers). The rendered manifest ships a
minimal core only; append ONLY the dependencies the answers call for, using the
chosen profile's `add_dep_command` (prefix Python's `uv add` with
`DEPS_VETTED=1` so the deps-guard hook lets a vetted install through). Map
intent to packages, per language:

- **Python** -- FastAPI: `fastapi`, `uvicorn[standard]`; Flask: `flask`; Streamlit/Gradio: `streamlit`/`gradio`; Postgres: `sqlalchemy`, `alembic`, `psycopg[binary]`; SQLite/DuckDB: `sqlalchemy`/`duckdb`; vectors: `pgvector`/`chromadb`/`pinecone-client`/`qdrant-client`; LLM: `openai` (also OpenRouter)/`anthropic`/`google-genai`; `httpx` for outbound HTTP.
- **TypeScript** -- API: `express` or `fastify` (+ `@types/*`); Postgres: `pg`+`@types/pg` or `drizzle-orm`; vectors: `chromadb`/`@pinecone-database/pinecone`/`@qdrant/js-client-rest`; LLM: `openai`/`@anthropic-ai/sdk`/`@google/genai`; config validation: `zod`. Frontend frameworks (React/Next/Vue) per the user's choice.
- **Go** -- HTTP: stdlib `net/http` (no dep) or `chi`/`gin`; Postgres: `github.com/jackc/pgx/v5`; LLM: the provider's official Go SDK or `net/http`. Add via `go get`.
- **Rust** -- HTTP server: `axum` or `actix-web` (+ `tokio`); Postgres: `sqlx`; LLM: the provider's official Rust SDK or `reqwest`. Add via `cargo add`.

Choose the smallest set that covers the answers; do not add a database/vector/LLM dep the project did not ask for. If mem0 was opted in, also add `mem0ai` (Python: `DEPS_VETTED=1 uv add mem0ai`; for other languages, add the equivalent client or leave a clearly-marked note in `docs/gotchas.md` if none is established).

**Then install.** If `{{USES_DEVCONTAINER}}` is `no`:

1. Verify the chosen package manager is available (the bootstrap should have caught this for known languages; verify again here for safety).
2. Run `{{INSTALL_COMMAND}}` to install deps from the manifest file.
3. Smoke-test:
   - Python: `uv run python -c "import sys; print(f'Python {sys.version.split()[0]} venv ready')"`
   - TypeScript: `node -e "console.log('Node ' + process.version + ' ready')"`
   - Rust: `cargo --version`
   - Go: `go version`
4. If install fails, leave the scaffold in place (do not roll back). Report the failing dep and ask the user to fix the manifest then re-run install.

If `{{USES_DEVCONTAINER}}` is `yes`: append the capability deps to the manifest, but **skip the install**. Deps will install inside the container.

### Phase 5: Verify and report

First, confirm the **core** files (every project, every language) exist:

```bash
test -f AGENTS.md && test -f README.md && test -f .env.example && \
test -f .mcp.json && test -f .claude/.template-version && \
test -f .github/workflows/qa.yml && test -f .github/pull_request_template.md && \
test -f docs/PRD.md && test -f docs/features.json && \
test -f docs/LEDGER.md && test -f docs/BACKLOG.md && \
test -f docs/SECURITY.md && test -f docs/language-standards.md && \
test -f docs/deviations.md && test -f docs/plans/README.md && \
test -f docs/plans/archive/.gitkeep && test -f docs/archive/.gitkeep && \
test -f docs/agents.md && test -f docs/agents.json && \
test -f scripts/features_check.py && python3 scripts/features_check.py && \
test -f scripts/backlog.py && test -f scripts/tamper_check.py && \
test -f scripts/factory_doctor.sh && \
test -f .claude/skills/iteration/SKILL.md && test -f .claude/skills/security-review/SKILL.md && \
test -f .claude/skills/tech-debt/SKILL.md
```

(`.claude/skills/` ships for every roster -- plain-markdown procedures, not
Claude Code slash commands -- so this check is unconditional.)

Then, ONLY when `claude-code` is in the agent roster, confirm the Claude-specific
enforcement tree landed:

```bash
test -L CLAUDE.md && test -d .claude/agents && \
test -f .claude/agents/reviewer.md && test -f .claude/agents/utility.md && \
test -f .claude/settings.json && test -f .claude/hooks/deps-guard.sh
```

And, ONLY when the project has a frontend (the frontend answer not `no`), also
confirm the design tree landed:

```bash
test -f docs/design/DESIGN.md
```

(this ships for any frontend project regardless of which agents drive it --
there is no separate design skill or agent in v4.0.0; design fidelity is one
of `@reviewer`'s four lenses.)

When `claude-code` is NOT in the roster: skip the Claude-specific enforcement
block above, and tell the user the bootstrap-installed skill helpers --
`init-project` itself and the Phase 1 `mattpocock/skills` pack (`tdd`,
`grill-me`, `to-prd`, `caveman`, `write-a-skill`, `handoff`) -- are inert for
their agents and safe to delete. This does NOT include the three generated
`.claude/skills/` procedures checked above (`iteration`, `security-review`,
`tech-debt`): those are the project's own canonical procedures and the
driving agent should read and follow them even without Claude Code.

Then confirm the chosen profile landed: its manifest (`{{MANIFEST_FILE}}`) exists, and the green-scaffold source + test exist (Python `src/example.py`+`tests/test_example.py`; TypeScript `src/example.ts`+`tests/example.test.ts`; Go `greet.go`+`greet_test.go`; Rust `src/lib.rs` (with its in-file unit test) + `tests/e2e.rs` + `rust-toolchain.toml`).

Then check no unresolved placeholders remain:

```bash
! grep -rn '{{[A-Z0-9_]*}}' . --include='*.md' --include='*.txt' --include='*.toml' --include='*.yml' --include='*.yaml' --include='*.json' --include='*.sh' --include='*.py' --include='*.ts' --include='*.go' --include='*.rs' --include='*.mod' --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=skills 2>/dev/null
```

(`--exclude-dir=skills` skips every dir literally named `skills`, which covers both the bootstrap-installed helper skills and this project's own generated `.claude/skills/` procedures. Some of those procedures (`iteration`, for one) DO carry placeholders in their template source (`{{QA_COMMAND}}`, `{{E2E_COMMAND}}`) -- excluding the dir here is safe anyway because `render.py` already substitutes them like any other file and its own `leftover_scan()` (rule 15, fails closed) is the actual backstop; this grep is a redundant human-readable double-check, not the only line of defense. The generated `.claude/hooks/` and `.claude/agents/` files ARE checked -- they carry substituted values.)

Now delete the renderer input, BEFORE running the quality gate: `rm
docs/_init-answers.json` (its content lives on in the rendered docs). It is
transient working state, not project content -- a project language's gate
(e.g. TypeScript's prettier check) has no reason to see it, and leaving it
on disk into the gate run is a bug, not a convenience.

Finally, **run the quality gate** (inside the dev container if one is used): `{{QA_COMMAND}}`. Every complete profile ships a green-on-first-run scaffold, so the gate must pass on the first run. If it is not green, fix the scaffold before handing off -- a project that starts red is a bug.

Report what was generated, then hand off:

> "Bootstrap complete. Your project is ready. Next steps:
> 1. {{If dev container}}: Reopen in dev container, then run `{{INSTALL_COMMAND}}` inside. {{Else}}: Deps are already installed; `{{QA_COMMAND}}` is green on the fresh scaffold. Use `{{FIX_COMMAND}}` to auto-format locally.
> 2. Initialize git: `git add . && git commit -m 'chore: bootstrap project'`. Push to enable CI.
> 3. Restart Claude Code so `.mcp.json` (Context7) registers.
> 4. Start your first task -- run the `iteration` skill against the first entry in `docs/features.json`, replacing `src/example.py` and `tests/test_example.py` with your first feature."

Then, if the repo has a GitHub remote and `gh` is available, offer (do not run unasked) to enable branch protection -- the generated CI is merge-blocking only once the repo requires its checks:

```bash
gh api -X PUT "repos/{owner}/{repo}/branches/main/protection" \
  -F 'required_status_checks[strict]=true' \
  -F 'required_status_checks[contexts][]=qa' \
  -F 'required_status_checks[contexts][]=e2e' \
  -F 'required_status_checks[contexts][]=features-check' \
  -F 'enforce_admins=false' -F 'required_pull_request_reviews=null' -F 'restrictions=null'
```

Explain the trade-off in one line: without this, a red build can still be merged by pushing directly.

---

## Placeholder substitution

Templates use `{{PLACEHOLDER}}` syntax. **`render.py` performs every
substitution** -- these tables are the reference map of what each placeholder
means and which answer (or profile value) feeds it. Do not substitute by hand.
Any new placeholder must be added here, to the answers schema (or
`profile.json`), and to `render.py`'s mapping, together.

### Universal placeholders (asked or derived)

| Placeholder | Source |
|---|---|
| `{{PROJECT_NAME}}` | the conversation (name) |
| `{{PROJECT_GOAL}}` | the conversation (one-sentence goal) |
| `{{PROJECT_SLUG}}` | derived from the name: lowercase, hyphenated, valid package/module identifier |
| `{{PRIMARY_USER}}` | the conversation (who it's for) |
| `{{CORE_PROBLEM}}` | the conversation (the problem, why now) |
| `{{CORE_JOURNEY}}` | the conversation (the heart: the core user-visible flow, as steps) -- renders into `docs/PRD.md`'s journey section, and is also the raw material for the `features[].serves` "journey step" phrasing the agent writes by hand |
| `{{SUCCESS_MEASURE}}` | the conversation (what success looks like, concretely) |
| `{{RISKIEST_ASSUMPTION}}` | the conversation (the assumption that sinks the project if wrong) -- answers-file only (no template consumer in v4.0.0) |
| `{{REQ_AC_LIST}}` | the conversation (3-5 observable acceptance criteria) -- kept in the answers file as the raw `- [ ] **REQ-ACn:** <criterion>` lines; answers-file only (no template consumer in v4.0.0 -- no `docs/requirements.md` exists to render it into). These criteria are the source for each feature's `acceptance` array in Phase 4, not for this placeholder. |
| `{{NON_GOALS}}` | the conversation (bullet list; at least two concrete non-goals) |
| `{{OTHER_USERS}}` | the conversation (bullet list; `- none identified yet` if empty) -- answers-file only (no template consumer in v4.0.0) |
| `{{CONSTRAINT_TIME}}` | the conversation -- answers-file only (no template consumer in v4.0.0) |
| `{{CONSTRAINT_COST}}` | the conversation (includes LLM/API budget when AI is in scope) -- answers-file only (no template consumer in v4.0.0) |
| `{{CONSTRAINT_DATA}}` | the conversation -- answers-file only (no template consumer in v4.0.0) |
| `{{FIRST_MILESTONE}}` | the conversation -- derived date or `none set` |
| `{{DEPLOYMENT_TARGET}}` | the conversation (where this runs and is hosted) |
| `{{SCALE_EXPECTATIONS}}` | the conversation -- answers-file only (no template consumer in v4.0.0) |
| `{{INTEGRATIONS}}` | the conversation (bullet list; `- none` if none) -- answers-file only (no template consumer in v4.0.0) |
| `{{PAIN_POINT}}` | the conversation (positioning) |
| `{{PRODUCT_CATEGORY}}` | the conversation (positioning) |
| `{{CURRENT_ALTERNATIVE}}` | the conversation (positioning) |
| `{{KEY_BENEFIT}}` | the conversation (positioning) |
| `{{KEY_DIFFERENTIATOR}}` | the conversation (positioning) |
| `{{IN_SCOPE_LIST}}` | derived from the core journey + acceptance criteria (bullet list) |
| `{{SUCCESS_METRICS}}` | the success measure, rendered as 1-3 `- <metric> -- target` lines |
| `{{PRD_SURFACES}}` | derived: `project.surfaces` (bullet list; `- (no user-facing surfaces -- API/CLI product)` when empty) -- renders into `docs/PRD.md`'s Surfaces section |
| `{{READS_UNTRUSTED}}` | the security-sensitive answer (`yes`/`no`) -- answers-file only (no template consumer in v4.0.0; the security-profile line in `docs/SECURITY.md` is written directly by renderer rule 10, not through this placeholder) |
| `{{HOLDS_PRIVATE_DATA}}` | the security-sensitive answer (`yes`/`no`) -- answers-file only (no template consumer in v4.0.0), same as above |
| `{{ACTS_OUTWARD}}` | the security-sensitive answer (`yes`/`no`) -- answers-file only (no template consumer in v4.0.0), same as above |
| `{{E2E_BROWSER_INSTALL_STEP}}` | derived from the frontend answer + profile `e2e_browser_install` (renderer rule 12) |
| `{{LANGUAGE}}` | the conversation (language) |
| `{{HAS_FRONTEND}}` | the conversation (frontend?) |
| `{{BACKEND_FRAMEWORK}}` | inferred from the conversation -- answers-file only (no template consumer in v4.0.0) |
| `{{AI_FEATURES}}` | inferred from the conversation (comma-separated) |
| `{{VECTOR_DB}}` | inferred from the conversation -- answers-file only (no template consumer in v4.0.0) |
| `{{LLM_PROVIDER}}` | inferred from the conversation -- answers-file only (no template consumer in v4.0.0) |
| `{{EMBEDDINGS_MODEL}}` | inferred from the conversation -- answers-file only (no template consumer in v4.0.0) |
| `{{DATABASE}}` | inferred from the conversation -- answers-file only (no template consumer in v4.0.0) |
| `{{USES_DEVCONTAINER}}` | the conversation, or the documented default (`yes`) |
| `{{POSITIVE_REFERENCE_TEXT}}` | the conversation (codebase-shape reference, if offered) -- rendered line (Phase 4 renderer table, rule 5) |
| `{{NEGATIVE_REFERENCE_TEXT}}` | the conversation (codebase-shape anti-reference, optional) -- rendered line, may be empty |
| `{{DESIGN_REFERENCES}}` | the frontend visual-reference follow-up -- bullet list; empty string when `design` is `null` |
| `{{DESIGN_TONE}}` | the frontend visual-reference follow-up -- tone words; empty string when `design` is `null` |
| `{{DESIGN_ANTI_REFERENCE}}` | the frontend visual-reference follow-up -- anti-reference; empty string when `design` is `null` |
| `{{MEMORY_DOC_LINE}}` | derived from the mem0 opt-in (`templates/conditional/memory-doc-line.md`, or empty) |
| `{{AI_DISCIPLINE_BLOCK}}` | derived from the AI-features answer (`templates/conditional/ai-discipline.md`, or empty) |
| `{{CODEX_REVIEW_STEP}}` | derived from the codex-reviewer opt-in -- `templates/conditional/codex-review-step.md`, or empty |
| `{{CODEX_ROSTER_NOTE}}` | derived from the codex-reviewer opt-in -- `templates/conditional/codex-roster-note.md`, or empty |
| `{{AGENT_MATRIX}}` | derived from the agent roster -- per-agent sections from `templates/conditional/agents/`, joined |
| `{{DATE}}` | today, ISO format (`date` in the answers file) |

`opt_ins.explanations`, `opt_ins.seed_gotchas`, and `opt_ins.mem0` have no placeholder of their own: they are switches in the answers file's `opt_ins` section that turn renderer rules 6-8 on or off.

Rows marked **answers-file only (no template consumer in v4.0.0)** above are still asked (or inferred), still required by the answers schema, and still land in `render.py`'s mapping -- `render.py` fails on an unmapped placeholder, so keeping the mapping entry is required either way, not optional cleanup. They simply have no `{{...}}` occurrence left in any file under `templates/core/` or `templates/profiles/` to substitute into, most often because the v3 redesign retired the doc that used to render them (e.g. `docs/requirements.md`) in favor of `docs/features.json` and `docs/PRD.md`. Removing the schema requirement and mapping entry for any of them is a breaking answers-schema change (touches `render_schema.py` and all nine golden fixtures) and is deliberately out of scope here -- if a row's answer is never used anywhere (not even to inform a derived field or a hand-written doc section), that is a signal to prune it in a dedicated pass, not silently.

### Language-derived placeholders (from the profile)

The renderer reads these from `templates/profiles/<lang>/profile.json` (the
machine-readable copy of the YAML blocks below -- keep the two in sync; the
golden-fixture CI cross-checks the load-bearing values).

| Placeholder | Filled from language profile |
|---|---|
| `{{LANGUAGE_VERSION}}` | profile.language_version |
| `{{PACKAGE_MANAGER}}` | profile.package_manager |
| `{{MANIFEST_FILE}}` | profile.manifest_file |
| `{{INSTALL_COMMAND}}` | profile.install_command |
| `{{ADD_DEP_COMMAND}}` | profile.add_dep_command |
| `{{QA_COMMAND}}` | profile.qa_command |
| `{{FIX_COMMAND}}` | profile.fix_command |
| `{{E2E_COMMAND}}` | profile.e2e_command |
| `{{TEST_RUNNER}}` | profile.test_runner |
| `{{TEST_COMMAND}}` | profile.test_command |
| `{{LINT_TOOL}}` | profile.lint_tool |
| `{{LINT_COMMAND}}` | profile.lint_command |
| `{{FORMAT_TOOL}}` | profile.format_tool |
| `{{FORMAT_COMMAND}}` | profile.format_command |
| `{{TYPE_TOOL}}` | profile.type_tool |
| `{{TYPE_COMMAND}}` | profile.type_command |
| `{{PRECOMMIT_INSTALL_COMMAND}}` | profile.precommit_install_command |
| `{{TEST_PATH_REGEX}}` | profile.test_path_regex -- the pattern `scripts/tamper_check.py` uses to recognize a test-file path for the tamper guard |
| `{{CI_SETUP_STEPS}}` | profile.ci_setup_steps (multi-line YAML block) |
| `{{LANGUAGE_PRECOMMIT_HOOKS}}` | profile.precommit_hooks (multi-line YAML block) |
| `{{LIBRARY_DOCS_URLS}}` | profile.library_docs_urls (markdown list) |
| `{{TYPE_ANNOTATION_NOTES}}` | profile.notes.type_annotations |
| `{{IMPORT_NOTES}}` | profile.notes.imports |
| `{{ASYNC_NOTES}}` | profile.notes.async |
| `{{ERROR_NOTES}}` | profile.notes.errors |
| `{{CONFIG_NOTES}}` | profile.notes.config |
| `{{LOGGING_NOTES}}` | profile.notes.logging |
| `{{TEST_LAYOUT_NOTES}}` | profile.notes.test_layout |
| `{{PRECOMMIT_HOOKS_NOTES}}` | profile.notes.precommit_hooks |

---

## Language profiles

The YAML blocks below are the human-readable profile reference (commands for
Phase 4.5, CI notes, conventions). The renderer consumes the machine-readable
copy at `templates/profiles/<lang>/profile.json` -- when you change a value
here, change it there too (CI cross-checks the load-bearing scalars).

### Python (fully supported)

```yaml
language_version: "3.12+"
file_extension: "py"
package_manager: "uv"
manifest_file: "pyproject.toml"
install_command: "uv sync"
add_dep_command: "uv add"
qa_command: "uv run qa"
fix_command: "uv run fix"
e2e_command: "bash scripts/e2e.sh"
e2e_browser_install: "uv run playwright install --with-deps chromium"
test_runner: "pytest"
test_path_regex: '^tests/'
test_command: "uv run pytest -m 'not e2e'"
lint_tool: "ruff"
lint_command: "uv run ruff check ."
format_tool: "ruff format"
format_command: "uv run ruff format --check ."
type_tool: "mypy"
type_command: "uv run mypy src/"
precommit_install_command: "uv run pre-commit install"

ci_setup_steps: |
  - name: Set up uv
    uses: astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5
    with:
      enable-cache: true
  - name: Set up Python
    run: uv python install 3.12
  - name: Install deps
    run: uv sync

precommit_hooks: |
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

library_docs_urls: |
  ### Core stack
  - **uv**: https://docs.astral.sh/uv/
  - **ruff**: https://docs.astral.sh/ruff/
  - **mypy**: https://mypy.readthedocs.io/
  - **pytest**: https://docs.pytest.org/
  - **Pydantic v2**: https://docs.pydantic.dev/latest/
  - **pydantic-settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

  ### AI / RAG (use Context7 first)
  - **OpenAI SDK**: https://github.com/openai/openai-python
  - **Anthropic SDK**: https://github.com/anthropics/anthropic-sdk-python
  - **LangChain**: https://python.langchain.com/docs/introduction/
  - **Chroma**: https://docs.trychroma.com/
  - **pgvector**: https://github.com/pgvector/pgvector

  ### Frontend (if applicable)
  - **Streamlit**: https://docs.streamlit.io/
  - **Gradio**: https://www.gradio.app/docs

notes:
  type_annotations: |
    - Python 3.12+ syntax: `list[int]` not `List[int]`. `dict[str, X]` not `Dict[str, X]`.
    - Every function signature fully typed, including return types.
    - `from __future__ import annotations` at the top of every module.
  imports: |
    - Order: stdlib -> third-party -> local. Sorted by ruff (`I` rule set).
    - One module per import line for stdlib and third-party.
    - If a name is used ONLY in annotations, ruff's TC rules will move it under `if TYPE_CHECKING:` -- but a name a framework resolves at RUNTIME from the annotation (e.g. FastAPI's `Request`/`Response`/`UploadFile` in route signatures) must stay a real import. Keep those imports at runtime and mark them `# noqa: TC002` if flagged.
  async: |
    - Match the project shape: in a server or any concurrent context, I/O (HTTP, DB, LLM) should be `async`. In a CLI, script, batch job, or library with no concurrency, plain sync is simpler and fine -- do not add async for its own sake.
    - When you do go async, use `asyncio.TaskGroup` (Python 3.11+) for concurrent work, and keep the whole I/O path async (no sync calls blocking the loop).
  errors: |
    - Specific exception classes per domain. Never bare `Exception`.
    - Fail-closed on safety/security: if uncertain, refuse rather than proceed.
    - Framework dependency-injection defaults (e.g. FastAPI `Depends(...)`) are called markers, not values: never replace `Depends(get_settings)` with a bare `get_settings()` call at import time -- the first form resolves per-request, the second freezes one instance at import and 500s under test overrides.
  config: |
    - `pydantic-settings` for all configuration.
    - Never hardcode API keys, URLs, or model names. Pull from env or settings.
  logging: |
    - `logging` module, not `print`.
    - Structured log lines (JSON if going to ingest, key=value otherwise).
  test_layout: |
    - `tests/` mirrors `src/` structure. Unit + functional tests run in the fast gate.
    - `tests/e2e/` holds end-to-end tests marked `@pytest.mark.e2e`; they are excluded from the fast gate and run via `scripts/e2e.sh` in CI. For a UI use `pytest-playwright` (headless browser); for API-only assert the full request -> response -> persisted-state path.
    - Security/red-team tests are marked `@pytest.mark.security` and follow the `docs/SECURITY.md` checklist.
    - Use `pytest-asyncio` for async tests. Inject fakes via fixtures/dependency objects; no mocks for code you own.
    - `factory-boy` or hand-rolled fixtures in `tests/fixtures/` for data.
    - `hypothesis` for property-based tests on pure functions.
    - `--import-mode=importlib` is set in addopts: test files may share basenames across folders without `__init__.py` shims.
  precommit_hooks: |
    This profile ships `.pre-commit-config.yaml` with `ruff` (`--fix`) and `ruff-format`, plus the generic hooks (trailing-whitespace, yaml/toml/json validation, large-file guard). Install once with `uv run pre-commit install`. (TypeScript, Go, and Rust profiles ship no pre-commit; their `qa` gate + CI are the enforcement.)
```

### TypeScript (complete)

Files live in `templates/profiles/typescript/`. The gate is expressed as npm scripts in `package.json` (qa is verify-only; fix mutates; e2e is separate). Ships no pre-commit config.

```yaml
language_version: "Node 22 (LTS) / TypeScript 5.7+"
file_extension: "ts"
package_manager: "npm"
manifest_file: "package.json"
install_command: "npm install"
add_dep_command: "npm install"
qa_command: "npm run qa"
fix_command: "npm run fix"
e2e_command: "npm run e2e"
e2e_browser_install: "npx playwright install --with-deps chromium"
test_runner: "vitest"
test_path_regex: '\.(test|spec)\.[jt]sx?$|^tests/'
test_command: "npx vitest run"
lint_tool: "eslint"
lint_command: "npx eslint ."
format_tool: "prettier"
format_command: "npx prettier --check ."
type_tool: "tsc"
type_command: "npx tsc --noEmit"
precommit_install_command: ""   # TypeScript profile ships no pre-commit; qa + CI are the gate

ci_setup_steps: |
  - name: Set up Node
    uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4
    with:
      node-version: '22'
      cache: 'npm'
  - name: Install deps
    run: npm ci

library_docs_urls: |
  ### Core stack
  - **TypeScript**: https://www.typescriptlang.org/docs/
  - **Vitest**: https://vitest.dev/
  - **ESLint (flat config)**: https://eslint.org/docs/latest/
  - **typescript-eslint**: https://typescript-eslint.io/
  - **Prettier**: https://prettier.io/docs/
  - **Playwright**: https://playwright.dev/docs/intro

notes:
  type_annotations: |
    - `strict: true`. Annotate every exported function's params and return type; let inference handle locals. Prefer `unknown` over `any`; never `as any` or `// @ts-ignore`.
  imports: |
    - ES modules only (`"type": "module"`). `import`/`export`, never `require`. Use `import type { X }` for type-only imports.
  async: |
    - Server/concurrent context: I/O is `async`/`await`. CLI/library with no concurrency: plain sync is fine -- do not add async for its own sake. Never leave a floating promise.
  errors: |
    - Throw `Error` subclasses per domain; never throw strings. Fail closed on safety/security.
  config: |
    - Read `process.env` at one boundary; validate it (e.g. zod) into a typed config. Secrets in `.env` (gitignored), never hardcoded.
  logging: |
    - Structured logger (`pino`) or `console` with structured fields; no scattered `console.log` in committed code.
  test_layout: |
    - `tests/` mirrors `src/`; unit + functional (`*.test.ts`) run in the fast gate via `vitest run`. `tests/e2e/` holds Playwright specs, excluded from the fast gate, run via `npm run e2e`.
    - Inject fakes via params/factories; avoid mocking modules you own.
  precommit_hooks: |
    - Not used. The TypeScript profile ships no `.pre-commit-config.yaml`; `npm run qa` (local + CI) is the gate.
```

### Go (complete)

Files live in `templates/profiles/go/`. The gate is `scripts/qa.sh` (verify-only: gofmt-check, vet, golangci-lint, test); fix mutates; e2e is build-tag gated (`//go:build e2e`). Ships no pre-commit config.

```yaml
language_version: "1.25+"
file_extension: "go"
package_manager: "go mod"
manifest_file: "go.mod"
install_command: "go mod download"
add_dep_command: "go get"
qa_command: "bash scripts/qa.sh"
fix_command: "bash scripts/fix.sh"
e2e_command: "bash scripts/e2e.sh"
e2e_browser_install: ""   # Go e2e is API/CLI-level by default (no browser)
test_runner: "go test"
test_path_regex: '_test\.go$'
test_command: "go test -race ./..."
lint_tool: "golangci-lint"
lint_command: "golangci-lint run"
format_tool: "gofmt"
format_command: "gofmt -l ."   # CHECK form (lists unformatted files); fix.sh does -w
type_tool: "go build"
type_command: "go build ./..."
precommit_install_command: ""   # Go profile ships no pre-commit; qa + CI are the gate

ci_setup_steps: |
  - name: Set up Go
    uses: actions/setup-go@40f1582b2485089dde7abd97c1529aa768e1baff # v5
    with:
      go-version: "1.25"
      cache: true
  - name: Download modules
    run: go mod download
  - name: Install golangci-lint (pinned + checksum-verified)
    run: |
      curl -sSfL -o /tmp/golangci-install.sh https://raw.githubusercontent.com/golangci/golangci-lint/v2.12.2/install.sh
      echo "d32d3534af96cfd59546a084d22b213e8a47541cada5013aa8a84c4fa2589905  /tmp/golangci-install.sh" | sha256sum -c -
      sh /tmp/golangci-install.sh -b "$(go env GOPATH)/bin" v2.12.2
      echo "$(go env GOPATH)/bin" >> "$GITHUB_PATH"

library_docs_urls: |
  ### Core stack
  - **Effective Go (idioms)**: https://go.dev/doc/effective_go
  - **Managing dependencies**: https://go.dev/doc/modules/managing-dependencies
  - **testing package**: https://pkg.go.dev/testing
  - **golangci-lint**: https://golangci-lint.run/

notes:
  type_annotations: |
    - Statically typed; the compiler is the type checker (`go build ./...`). Explicit types on exported signatures; `:=` for obvious locals. Keep zero values meaningful.
  imports: |
    - Group stdlib / third-party / local, blank-line separated. `goimports` (fix.sh) sorts and prunes. Unused imports fail compilation.
  async: |
    - Concurrency is goroutines + channels, only where it earns its keep; CLI/script/library stays sequential. Use `context.Context` on I/O paths; never leak goroutines.
  errors: |
    - Return `error` last; check it immediately. Wrap with `fmt.Errorf("...: %w", err)`; inspect with `errors.Is`/`As`. Reserve `panic` for unrecoverable state. Fail closed.
  config: |
    - Config from env (`os.Getenv`) or flags; never hardcode keys/URLs/models. Secrets out of source and `go.mod`.
  logging: |
    - `log/slog` (structured), not `fmt.Println`, for application logs.
  test_layout: |
    - `_test.go` files beside the code (`package app`) run in the fast gate via `go test ./...`. `tests/e2e/` is `//go:build e2e`-gated, excluded from the fast gate, run via `scripts/e2e.sh`.
    - Table-driven tests + `t.Run` subtests. Inject fakes via interfaces you own; avoid mocking frameworks.
  precommit_hooks: |
    - Not used. The Go profile ships no `.pre-commit-config.yaml`; `bash scripts/qa.sh` (local + CI) is the gate.
```

### Rust (complete)

Files live in `templates/profiles/rust/`. The gate is `scripts/qa.sh` (verify-only: line cap, fmt-check, clippy with warnings-as-errors, check, test); fix mutates; e2e tests are `#[ignore]`-tagged in `tests/e2e.rs` and run via `scripts/e2e.sh`. The toolchain (compiler + clippy + rustfmt) is pinned by `rust-toolchain.toml`, which rustup honors everywhere (local, dev container, CI). The manifest ships as a plain `Cargo.toml` (no `.example` suffix needed: cargo never scans nested directories, so the template copy is inert -- unlike Python's `pyproject.toml`). Ships no pre-commit config.

```yaml
language_version: "1.96 (edition 2024; pinned by rust-toolchain.toml)"
file_extension: "rs"
package_manager: "cargo"
manifest_file: "Cargo.toml"
install_command: "cargo fetch"
add_dep_command: "cargo add"
qa_command: "bash scripts/qa.sh"
fix_command: "bash scripts/fix.sh"
e2e_command: "bash scripts/e2e.sh"
e2e_browser_install: ""   # Rust e2e is API/CLI-level by default (no browser)
test_runner: "cargo test"
test_path_regex: '^tests/'
test_command: "cargo test"
lint_tool: "clippy"
lint_command: "cargo clippy --all-targets -- -D warnings"
format_tool: "rustfmt"
format_command: "cargo fmt --check"   # CHECK form; fix.sh runs `cargo fmt` (write)
type_tool: "cargo check"
type_command: "cargo check"
precommit_install_command: ""   # Rust profile ships no pre-commit; qa + CI are the gate

ci_setup_steps: |
  - name: Set up Rust
    # Installs the toolchain pinned in rust-toolchain.toml (channel + the
    # clippy/rustfmt components) and enables cargo caching. rustflags is
    # cleared so the scripts alone define strictness (qa runs clippy with
    # -D warnings); the action would otherwise export RUSTFLAGS="-D warnings"
    # and make plain builds stricter in CI than locally.
    uses: actions-rust-lang/setup-rust-toolchain@166cdcfd11aee3cb47222f9ddb555ce30ddb9659 # v1
    with:
      rustflags: ""
  - name: Fetch dependencies
    run: cargo fetch

library_docs_urls: |
  ### Core stack
  - **The Rust Book**: https://doc.rust-lang.org/book/
  - **Standard library**: https://doc.rust-lang.org/std/
  - **The Cargo Book**: https://doc.rust-lang.org/cargo/
  - **Clippy lint list**: https://rust-lang.github.io/rust-clippy/master/
  - **rustfmt**: https://github.com/rust-lang/rustfmt

notes:
  type_annotations: |
    - Statically typed; the compiler is the type checker (`cargo check`). Explicit types on public signatures; let inference handle locals. Prefer borrowed views (`&str`, `&[T]`) for parameters and owned types for returns.
  imports: |
    - `use` statements at the top, grouped stdlib / third-party / crate-local, blank-line separated (rustfmt keeps each group sorted). No wildcard imports outside preludes and test modules.
  async: |
    - Add async (tokio) only when the project is genuinely concurrent (server, many parallel I/O calls); a CLI, batch job, or library stays synchronous -- do not add an async runtime for its own sake. When async, keep the whole I/O path async and never block the executor (no `std::thread::sleep` or sync file I/O inside it).
  errors: |
    - Return `Result<T, E>` with a domain error enum (`thiserror` in libraries; `anyhow` acceptable at the application boundary). No `unwrap()`/`expect()` outside tests and provably-infallible spots; `?` for propagation; `panic!` only for unrecoverable invariants. Fail closed on safety/security.
  config: |
    - Read env at one boundary into a typed config struct; never hardcode keys/URLs/models. Secrets in `.env` (gitignored), never in source or Cargo.toml.
  logging: |
    - `tracing` (structured, with spans) for application logs -- not `println!`.
  test_layout: |
    - Unit tests live beside the code in `#[cfg(test)] mod tests` blocks; integration tests in `tests/`; both run in the fast gate via `cargo test`. `tests/e2e.rs` is `#[ignore]`-tagged, excluded from the fast gate, run via `scripts/e2e.sh` (`cargo test --test e2e -- --ignored`).
    - Table-style cases via loops over input/expected pairs; inject fakes via traits you own; avoid mocking frameworks.
  precommit_hooks: |
    - Not used. The Rust profile ships no `.pre-commit-config.yaml`; `bash scripts/qa.sh` (local + CI) is the gate.
```

### Experimental languages (Other)

"Other" has **no profile** -- there is no profile folder to copy, so a generated project would be core-only with no working toolchain. Do not imply otherwise. Get explicit consent first:

> "Heads up: that language isn't a built profile yet. I can lay down the universal core (AGENTS.md, docs, security files, CI shape), but you'd have to build the toolchain yourself -- there's no validated manifest, lint/format/type setup, qa/fix scripts, or green scaffold -- so the first quality-gate run won't pass until you complete it. Proceed on that basis, switch to Python/TypeScript/Go/Rust, or have me add a profile for it properly first?"

If they proceed: `render.py` cannot run without a `profile.json`, so this is the ONE path where generation is manual -- copy `templates/core/` only, substitute the discovery placeholders from the answers file by hand, leave clearly-marked TODOs for the toolchain placeholders in `docs/language-standards.md` and `.github/workflows/qa.yml`, do NOT generate a manifest or scripts, and tell them the gate is not green until they finish the toolchain. The better path is to add a real profile under `templates/profiles/<lang>/` (see the repo `AGENTS.md` `<adding-a-language-profile>`) so the experience matches the complete profiles.

---

## Failure modes and how to handle them

**The user can't decide on a language.**
Python, TypeScript, Go, and Rust are all complete profiles; default to Python if there is no other signal. Don't let analysis paralysis block progress.

**The user wants to skip the interview.**
Minimum, cannot be skipped: name, one-sentence goal, the core flow, and at
least one acceptance criterion. Everything else can take the documented
default (Phase 4 table) or a `TODO(interview-skipped)` sentinel per rule
zero. Explain why: every field left blank ships as a TODO that later becomes
a surprise, which is the exact failure this template exists to prevent.

**The user wants to bootstrap into a non-empty directory.**
Refuse unless they explicitly confirm overwriting. Show what would be overwritten first.

**Skill installation fails (no npm/node).**
This is a hard failure. The `tdd` skill is required. Stop and ask the user to install Node.js, then re-run.

**Package manager not available for chosen language.**
Stop with a clear install link for the chosen language's package manager (`uv`, `npm`, `cargo`, `go`).

**Context7 MCP fails to start after bootstrap.**
Check that `npx` is available. The Context7 server in `.mcp.json` uses `npx -y @upstash/context7-mcp@3.2.3`. If npx is broken, document the failure in `docs/gotchas.md` and instruct the user to either fix npx or remove the Context7 entry from `.mcp.json`.

---

## After bootstrap: how the system works

Once bootstrap completes, the project enters normal mode. The agent should:

1. Read `AGENTS.md` on every new conversation -- it is the only always-loaded doc, capped at 100 lines.
2. Run the `iteration` skill for every entry in `docs/features.json` -- it routes a chore straight to build, and a feature through GRILL -> RED -> GREEN -> REVIEW -> MERGE, building any needed mockup at GRILL when the feature's `surface` is not `"none"`.
3. Treat `docs/features.json` as the spec -- keep statuses honest; a feature is not `done` until its mapped tests exist and pass, and a dropped feature keeps its entry with a reason in `notes`, never a deletion. `docs/BACKLOG.md` (`scripts/backlog.py`) is its generated human-readable view.
4. Dispatch `@reviewer` at the REVIEW step of every feature -- fresh context by design, never the agent that built the change -- for plan conformance, correctness, design fidelity on visual surfaces, and security when the `security-review` skill's trigger matches.
5. Log deviations from a plan or mockup in `docs/deviations.md`, collect lessons the project pays for in `docs/gotchas.md`, and run `bash scripts/factory_doctor.sh` after merge to prune worktrees and merged branches.

This skill is no longer needed after bootstrap. It can be deleted from `.claude/skills/` if the user wants to keep the project minimal.
