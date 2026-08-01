---
name: security-review
description: >-
  The security trigger and review procedure for this project. Use when deciding
  whether work needs a security pass, and to run one -- "does this need security
  review?", auth changes, new input surfaces, new tools.
---

# security-review

## The trigger (canonical -- this is its only home)

Work is security-triggering when it adds or changes any of:
external input handling; dependence on untrusted generated output; public
publishing of content; authentication or authorization; a tool or automation
with side effects; persistence of untrusted content.

## Procedure when the trigger matches

1. Dispatch `@reviewer` with the security lens and a fresh context (an
   independent red-team pass; a "security focus" inside code review does
   not substitute) -- or, when subagents aren't available in your harness,
   run the equivalent independent pass in a fresh context.
2. Apply the `docs/SECURITY.md` delta for the new surface, or record in the
   review notes why none is needed. A stale threat model is worse than none.
3. Findings become failing security tests before fixes -- the gap stays closed
   in CI. Prove controls on the real enforcement path with the live path's
   flags, never via a debug/introspection endpoint.

Matching work is a FEATURE whose GRILL includes a threat model (`AGENTS.md`
`<tiers>`), full stop.
