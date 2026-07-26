### Enforcement omitted (no Claude Code in this roster)

This project was generated without the Claude Code enforcement stack: no
subagents (`.claude/agents/`, including the mandatory `@code-reviewer` /
`@security-reviewer` and, for frontend projects, `@design-reviewer`), no hooks
(including the `deps-guard` supply-chain guard and the quality-gate `Stop`
hook), and no `.claude/settings.json` or `CLAUDE.md` symlink. Where
`AGENTS.md`, `docs/SECURITY.md`, or `docs/language-standards.md` mandate a
subagent or hook, treat the mandate as a manual responsibility of the driving
agent -- nothing replaces that automation today.

What DOES still ship: the plain-markdown procedures under `.claude/skills/`
(`slice`, `security-review`, `tech-debt`, `select-agents`, and -- for frontend
projects -- `design-loop`). They are not Claude Code slash commands here, but
they are still the canonical procedures for this project; read and follow them
manually. In particular, the security review trigger (when a change needs a
security pass) lives in `.claude/skills/security-review/SKILL.md`, not in a
subagent. `select-agents` describes re-probing the roster via a Claude Code
skill invocation -- with no Claude Code installed, edit `docs/agents.json`
directly instead, using that skill's file as the reference for what changes.
Keep `docs/features.json` current by hand.
