# ForgeWorks

> One command turns an empty folder into a structured, TDD-driven, security-gated project — built for **agentic coding**.

**Senior-team discipline for your AI coding agent.** You bring the idea plus working development and agentic-coding experience -- ForgeWorks wraps your agent in a senior team's discipline (planning, a real test pyramid, a security review, a second-opinion reviewer), so a solo developer can turn a prompt into a product that is actually tested, secure, and shippable -- not a throwaway demo. (If you have never driven an AI coding agent before, expect a learning curve: the machine enforces the quality gate, the feature-list check, and reviews scaled to risk.)

It is not a starter app. It installs the rules, specialist roles, and deterministic gates that make an AI coding agent produce code you can actually review, ship, and maintain. The core is stack-agnostic; your language and tooling are chosen in a short interview, not hard-coded.

```bash
mkdir my-project && cd my-project && git init
bash <(curl -fsSL https://raw.githubusercontent.com/Kpakfar/ForgeWorks/v3.0.0/bootstrap/install.sh)
# then open your agent and run:  /init-project
```

## Why use it

- **Portable rules; enforcement is Claude Code today.** The whole constitution lives in `AGENTS.md` (symlinked to `CLAUDE.md`) — the cross-tool standard read by Claude Code, Codex, Cursor, opencode, and others. The rules and docs (`AGENTS.md`) are portable to any agent; the deep orchestration and local gates (subagents, hooks, MCP) run in Claude Code today, and other agents ignore the Claude-specific parts gracefully.
- **Two agents, two perspectives.** Drive with your primary agent and bring a **second one as an independent reviewer** — e.g. **Codex** (opt in during setup) — for a genuine second opinion on important changes. Two models reviewing beats one.
- **Ceremony sized to risk, not to habit.** Three risk tiers — light, standard, high-risk — set how much planning and review a change needs, from "just build it" to a user-approved plan plus a full security review. UI-heavy slices get a real mockup to approve *before* implementation.
- **The whole test pyramid, at spec time.** Unit + functional/API + headless-browser e2e + security tests are named in the plan and written first (Red phase) for standard and high-risk work.
- **Security is enforced, not requested.** Access-control/IDOR, secrets, supply chain, and (for AI apps) prompt-injection defenses live in `AGENTS.md` + `docs/SECURITY.md`, backed by a real `PreToolUse` supply-chain hook (a best-effort guard, not a sandbox) — because prompt-level security is theater.
- **Self-improving & upgradeable.** Lessons flow back into the template; existing projects pull updates with `/upgrade-project`, non-destructively.

## What you get

- **`AGENTS.md` constitution** — a ~80-line core (architecture, security, risk tiers, roster) that stays the single source of truth, plus on-demand skills for planning, design, and security discipline for the ceremony that doesn't need to live on every page.
- **5 subagents** — `@implementer`, `@code-reviewer` (+ optional Codex second opinion), `@security-reviewer`, `@design-reviewer` (frontend projects), and `@utility` (haiku-pinned, for mechanical chores that should never burn expensive-model tokens).
- **Skills** — `slice` (the tiered per-feature workflow), `design-loop` (mockup -> build -> screenshot-verify, frontend projects), `security-review` (the trigger + procedure), `tech-debt` (on-demand sweep), and `select-agents` (change the agent roster mid-project).
- **Deterministic gates** — a verify-only `qa` (plus a local `fix`), a supply-chain `deps-guard` hook, a `features.json`/`features_check.py` feature-list check, and CI (fast gate + separate e2e job).
- **Living docs** — product vision, the feature list (`docs/features.json`), design docs, gotchas, SECURITY, and `docs/deviations.md` for agent judgment calls.
- **Batteries** — Context7 MCP for live library docs, an optional dev container, a green-on-first-run scaffold, a PR template, and a pre-commit config (Python profile only).

## How it works

The main agent orchestrates the loop; `tdd` and `grill-me` (from `mattpocock/skills`) drive the methodology and planning. The `slice` skill picks a risk tier per change; code review is mandatory, a security red-team pass runs on a canonical trigger, and a design review checks shipped screens against the approved mockup on frontend projects. Tasks with no behavioral effect (typos, doc wording, formatting) skip the ceremony — anything that changes what the product does, however small, does not. The same quality gate runs locally (a `Stop` hook that blocks a red build) and in CI.

<!-- TODO(v3): docs/forgeworks-loop.png still depicts the v2 loop (test-spec-writer
     and tech-debt as subagents, a fixed seven-step cycle, no design-reviewer or
     risk tiers) -- regenerate it for v3 before re-enabling. Original alt text:
     "The ForgeWorks multi-agent TDD loop: a one-time bootstrap session, then a
     repeating seven-step cycle driven by an orchestration layer that dispatches
     six specialist subagents" -->
<!-- ![The ForgeWorks multi-agent TDD loop](docs/forgeworks-loop.png) -->

## Upgrade an existing project

Run the **same command** inside it — `install.sh` detects a generated project and installs `/upgrade-project` instead of bootstrapping:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Kpakfar/ForgeWorks/v3.0.0/bootstrap/install.sh)
# then run:  /upgrade-project
```

It reconciles your project against the current template — copying missing files and grafting new rule blocks **without overwriting your content**. Non-destructive and idempotent. (Never re-run `/init-project` on an existing project; that overwrites your filled-in docs.)

## Repo layout

```
bootstrap/        seed kit + install.sh (bootstraps empty dirs, routes existing ones to upgrade)
init-project/     /init-project skill — interview + generation; templates/core/ + templates/profiles/<lang>/
upgrade-project/  /upgrade-project skill — non-destructive reconcile for existing projects
docs/             how-to-use.md and ROADMAP.md
VERSION           stamped into generated projects
```

## Languages

**Python, TypeScript, Go, and Rust** are complete profiles — pick any in the interview and you get only that language's toolchain (no cross-language leakage). All four are verified green on the first run by CI, on the **merged core+profile tree** (the exact shape a generated project has). "Other" isn't built yet (the interview tells you so and gets consent). Adding a language is a documented recipe (`docs/how-to-use.md`). Releases are versioned tags (current: `v3.0.0`): a pinned tag gives you the same template files tomorrow, though runtime inputs (npm/degit/Context7) aren't fully reproducible yet — see `docs/ROADMAP.md`.

## Status

ForgeWorks is an opinionated harness — a capable product with a clear roadmap. Be aware of what is and isn't mechanically true today:

- **Generation is deterministic.** The agent interviews you and writes an answers file; a stdlib-Python renderer (`init-project/render.py`) turns it into the project tree — same answers, same bytes, locked by golden-fixture CI (eight answer sets, byte-for-byte against committed expected trees, hostile values included). Only the interview itself and dependency installs remain agent work.
- **The supply-chain guard is best-effort.** The `deps-guard` hook reduces risk; it is not a sandbox. The real controls are lockfile review and CI scanning.
- **Profiles:** Python, TypeScript, Go, and Rust are each verified green in CI on the merged core+profile tree, quality gate and e2e runner included.

## License

MIT. Use it, change it.
