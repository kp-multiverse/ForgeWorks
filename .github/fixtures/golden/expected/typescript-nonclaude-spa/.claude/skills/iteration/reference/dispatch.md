# Dispatch -- job cards and the model ladder

Read this only when work leaves the main context.

**Job card.** Work is dispatched on a card with four parts: the deliverable's
shape, the exact inputs (paths and named sections, never "read the docs"),
the model tier, and the done-check (the command or test that verifies the
result). If that card cannot be written, the job is not dispatchable. Keep it.

**Tiers** are named in `docs/agents.json` (`model_tiers`; model ids live
there, never in prose). Route by one rule: the cheapest model whose failure
the done-check would catch.

- `mechanical`: chores with a mechanical done-check (renames, log mining,
  regenerations, dep bumps the gate verifies). `@utility` runs these.
- `standard`: GREEN against complete RED tests for a non-UI feature.
- `judgment` (or this context): GRILL, RED, REVIEW, security, mockups --
  anywhere a wrong answer fails silently instead of loudly.

A tier value may carry a harness prefix (`opencode:<model-id>`): send the
card through that harness's non-interactive runner
(`opencode run -m <model-id> "<card>"`). A tier may also be an ordered list of
channels: spend order, free first. Dispatch on the first; a rate-limit or
quota block moves sideways to the next. Exhaustion is not failure.

**Escalation.** A card whose done-check fails twice at its tier comes back
one tier up, or into this context, with the failure output attached. Never a
third try at the same tier, never a silent retry. The GREEN stall cap still
applies afterwards.

**Rules that do not bend.** Commit before every dispatch. One writer per
branch. Subagents return a result of about 1-2K tokens, not a transcript.
Without subagents in the harness, run the same pass as an independent
fresh-context session.
