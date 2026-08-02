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

---

## Generic lessons (candidates for backporting to the template)

A gotcha that would apply to any project on any stack, not just this one. Flag
it here in one line; the template's `<self-improvement>` review picks it up.

<!-- Add generic lessons here, one line each. -->
