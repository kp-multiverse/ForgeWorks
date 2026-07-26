---
name: design-loop
description: >-
  The design workflow for user-visible surfaces. Use BEFORE implementing any
  new screen, page, or significant visual change -- and after building it, to
  verify fidelity. Divergent mockups -> owner picks -> committed mockup is the
  spec -> build -> screenshot-compare.
---

# design-loop

Read `docs/design/DESIGN.md` first (direction, tokens, rubric). It exists to
prevent the default look; do not start from a blank aesthetic.

## New surface

1. **Diverge.** Build 3-4 genuinely different directions as one throwaway HTML
   file each (or one file with a variant switcher) -- different layout
   strategies, not recolors of one idea. All must respect the tokens file and
   the anti-reference. Real content over lorem ipsum.
2. **Owner picks.** This is the one human design gate. Present the variants,
   let the owner pick and amend.
3. **Commit the winner** to `docs/design/mockups/<feature-id>-<name>.html`
   (see the README there) and note the pick in the feature's `notes` field.
   The mockup is now the spec for that surface.
4. **Build against the mockup**, taking colors/spacing/type from the tokens
   file, not from the mockup's inline values. States are part of the surface:
   loading, empty, and error get designed, not defaulted.
5. **Verify visually.** Run the app, screenshot the surface in its real states
   (wide + narrow), and compare against the mockup and rubric yourself; then
   dispatch `@design-reviewer` for the fresh-context grade (or, when
   subagents aren't available in your harness, run the equivalent
   independent pass in a fresh context). Iterate until it reports MATCHES,
   or the owner accepts named deltas (log them in `docs/deviations.md`).

## Existing surface

Re-read its mockup before changing it. If the change is big enough to alter
the mockup, update the mockup in the same branch -- mockup and screen move
together or the drift compounds.
