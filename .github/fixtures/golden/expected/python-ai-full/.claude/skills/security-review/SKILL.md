---
name: security-review
description: >-
  The security trigger and review procedure for this project. Use when deciding
  whether work needs a security pass, and to run one -- "does this need security
  review?", auth changes, new input surfaces, new tools.
---

# security-review

## The trigger (canonical -- this is its only home)

Work is security-triggering when it adds or changes any of: external input
handling; dependence on untrusted generated output; public publishing of
content; authentication or authorization; a tool or automation with side
effects; persistence of untrusted content.

## When the trigger matches

Matching work is a feature whose plan carries a threat model (the `iteration`
skill's GRILL step). Then:

1. `@reviewer` runs the security lens in a fresh context, an independent
   red-team pass; a "security focus" inside code review does not substitute.
   Without subagents, run the equivalent pass in a fresh session.
2. Apply the `docs/SECURITY.md` delta for the new surface, or record in the
   feature's `notes` why none is needed. A stale threat model is worse than
   none.
3. Findings become failing security tests before fixes, so the gap stays
   closed in CI. Prove controls on the real enforcement path, never via a
   debug endpoint.
