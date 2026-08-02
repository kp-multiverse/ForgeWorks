# Gotchas -- what reality charged us for

Traps that bit us, and non-obvious facts about this codebase or stack. Agents
add an entry after a task that surprised them, and read this before working in
the same area again.

**An entry earns its place by changing a future decision.** Not by being true,
and not by being interesting. Budget: 8K chars for the whole file (see
`AGENTS.md` `<context>`).

## Format -- four short lines, newest first

```
### [Area] Short title
**Symptom:** what looked broken / surprising
**Cause:** why it happened
**Fix:** what works
**Date:** YYYY-MM-DD
```

Four lines is the format, not a floor to expand from. If an entry needs a code
sample to be useful, it belongs in a code comment at the place it bites.

## Pruning

Delete an entry when any of these is true -- do not wait for the budget:

- The code now makes the mistake impossible (a guard, a type, a test).
- The dependency, API, or file it describes is gone.
- It restates something the codebase now says more clearly.

At the budget, prune until nothing left is deletable -- not until the file
squeaks under 8K. A gotchas file parked at 99% of its cap release after release
means nothing was ever pruned, only shaved.

## Entries

<!-- Newest first. -->

### [General] Patch the cause, not the symptom
**Symptom:** a failure was fixed but the same bug recurs with a different shape.
**Cause:** the fix patched the surface (special case, magic string, swallowed exception) instead of the underlying category (bad input, wrong config, dependency version, race, missing edge case).
**Fix:** identify which category the cause is in first; fix at that level.
**Date / Task:** seeded by `/init-project`.

### [General] Trust artifacts, not summaries
**Symptom:** a subagent reported success; the actual artifact (test run, metric, file change) told a different story.
**Cause:** subagent summaries describe intent, not reality.
**Fix:** open the artifact on disk, run the test yourself, or grep the file before trusting any "done" claim.
**Date / Task:** seeded by `/init-project`.

### [General] Handle external I/O at one boundary, not everywhere
**Symptom:** a single transient failure (a DNS blip, a momentary 5xx, a dropped connection) aborted a whole multi-step run.
**Cause:** the error propagated raw from deep inside the flow; nothing between the call site and the top retried or degraded it, and the framework did not absorb it either.
**Fix:** wrap each external call (network, third-party API, tool) at a single boundary that retries transient errors with backoff and then degrades gracefully (empty result + a logged warning). One dead call then costs a call, not the run; a real outage still ends loudly after the retry budget.
**Date / Task:** seeded by `/init-project`.

---

## Generic lessons (candidates for backporting to the template)

A gotcha that would apply to any project on any stack, not just this one. Flag
it here in one line; the template's `<self-improvement>` review picks it up.

<!-- Add generic lessons here, one line each. -->
