# Field feedback

Lessons from ForgeWorks-run projects that apply to the template itself, not to
one repo. One dated entry per lesson: what happened, root cause, what the
template should change. An upgrade or template session consumes an entry by
turning it into a plan/spec or a template change, then deletes it. This file
is an inbox, not an archive.

---

## 2026-08-22 -- Skill-ecosystem collision degraded output quality (kpakfar.me)

**What happened.** A week of visibly degraded agent output on kpakfar.me and
CV work: off-tone copy, invented facts, irrelevant responses. An audit found
the cause in the instruction stack, not the model.

**Root cause.** Three overlapping skill ecosystems were active at once: the
superpowers plugin, the mattpocock-skills plugin, and the standalone
`~/.agents/skills` set the template names as upstream (`tdd`, `grill-me`).
That gave every task 3 TDD skills, 3 debugging skills, 4 grilling skills and
3 review paths. Skill routing became a race, and generic process skills
(superpowers:brainstorming, injected via a SessionStart hook that demands
"invoke a skill before ANY response") preempted the project-specific skills
that carry the tone and factuality rules (kp-voice, tc-career-review, the
template's own `iteration`). Generic skill wins the race, generic output
ships.

**Second finding.** The template's checkpoint/docs budget measures repo files
only, but the real session-start load also includes global CLAUDE.md files,
the memory index, plugin SessionStart injections and MCP tool listings. On
this machine the repo-side budget was met while the actual session start was
several times larger, invisibly.

**Third finding.** Session-state memories (resume state, feature handoffs) go
stale and then inject outdated "facts" into new work. Durable preferences
belong in memory; state belongs in the repo's docs, which the template
already prunes mechanically.

**What the template should change.**
1. `AGENTS.md` or `/init-project` should state the one-copy rule explicitly:
   one source per process skill (tdd, grilling, debugging, review), and name
   which. Today the template names `tdd` and `grill-me` as upstream but says
   nothing about coexisting ecosystems.
2. Add a doctor check (factory_doctor or a new `skills_doctor`) that lists
   skill names appearing more than once across plugins, personal skills and
   project skills, and flags always-on SessionStart injection plugins that
   contradict the constitution's minimal-context checkpoint.
3. Document that the checkpoint budget is a lower bound: global config can
   blow it invisibly, so the doctor should also print the real session-start
   inventory (CLAUDE.md chain, memory index size, enabled plugins).
4. Memory guidance for template projects: durable preferences and gotchas in
   agent memory, state in repo docs where prune.py already governs it.

**Resolution on the reporting machine, 2026-08-22:** superpowers,
mattpocock-skills and four unused legal plugins disabled globally; the
standalone `tdd`/`grill-me` symlinks kept as the single copy; agent memory
compacted (five session-state memories consolidated into two).
