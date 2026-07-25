# Roadmap

Where ForgeWorks is today, and what is genuinely deferred. This is the honest
companion to the README `## Status` section — read both before judging what the
tool does mechanically versus what is still future work.

## Current state

- **Architecture: core + profiles.** A generated project is `init-project/templates/core/`
  (language-free files: `AGENTS.md`, docs, security files, `.mcp.json`, CI shape)
  plus exactly one `init-project/templates/profiles/<lang>/`. No second language's
  files ever leak in.
- **Language profiles.** Python, TypeScript, Go, and Rust are complete profiles,
  each **verified green on the first run by the root CI** (`.github/workflows/ci.yml`),
  which renders the merged core+profile tree — the exact shape a generated
  project has — and runs the real quality gate and e2e runner on it.
  "Other" is not built — the interview says so and asks for consent
  before continuing.
- **Generation is deterministic (since v2.3.0).** The agent runs the interview
  and writes `docs/_init-answers.json`; `init-project/render.py` (stdlib
  Python, plain string substitution) renders the tree — every placeholder,
  conditional rule, structured-file escape, symlink, chmod, and version stamp.
  Same answers, same bytes. A golden-fixture CI job
  (`.github/scripts/golden_test.py`) compares seven rendered answer sets —
  including a hostile-values fixture — byte-for-byte against committed
  expected trees. Only the interview itself and the package-manager dependency
  steps remain agent-executed.
- **Portability.** The rules and docs (`AGENTS.md`, symlinked to `CLAUDE.md`) are
  the cross-tool standard and travel to any agent. The deep orchestration and
  local gates (subagents, hooks, MCP) run in Claude Code.

## Known limitations / roadmap

- **Supply-chain pinning is largely done (v2.4.0).** GitHub Actions are
  SHA-pinned (with a CI job asserting it), dev-container base images are
  digest-pinned, the `uv` installer is sha256-verified, and `degit` and the
  Context7 MCP package are version-pinned. Remaining softness: the npm/npx
  runtime itself and degit's fetch integrity are trusted; the `deps-guard`
  hook stays a best-effort guard, not a sandbox.
- **Cross-agent parity beyond rules + roster is future.** Since v2.5.0 the
  interview selects the project's agent roster (B13), emits it as a runtime
  config (`docs/agents.json` + `docs/agents.md`), and ships `/select-agents`
  for mid-project changes. Other agents inherit the rules, docs, and roster;
  dedicated adapters that reproduce the Claude Code subagents, hooks, and MCP
  orchestration elsewhere are still not built.
- ~~Conditional prototype/mockup-skill install at bootstrap~~ -- **shipped in
  v3.0.0** as the generated `design-loop` skill (mockup -> build ->
  screenshot-verify, frontend projects), backed by `docs/design/` and the
  `@design-reviewer` subagent.
- ~~**Express/starter mode**~~ -- **superseded in v3.0.0** by the three risk
  tiers (light / standard / high-risk) in `<risk-tiers>`: ceremony now scales
  to the change instead of needing a separate lighter mode.
- **v2's universal ship-record/audit chain was removed in v3.0.0.** The
  per-slice ship record, `docs/current-task/`, and the `ship-audit` CI job
  are gone; risk tiers plus `docs/deviations.md` replace them with
  judgment-scaled ceremony instead of a mandatory audit trail on every
  change. Rationale:
  `docs/superpowers/specs/2026-07-25-v3.0.0-fable-era-harness-design.md`.
- **A 5-minute worked example** ("watch it build one real feature" walkthrough
  doc) is deferred.
