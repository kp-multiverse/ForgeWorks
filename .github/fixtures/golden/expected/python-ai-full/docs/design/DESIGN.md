# Design direction: Recipe Radar

The visual spec for this project. The `design-loop` skill reads this before any
mockup; `@design-reviewer` grades shipped screens against it and the approved
mockup in `mockups/`.

## Direction (from the setup interview)

**References -- what to steal, from where:**
- datasette.io -- plain, content-first layout that gets out of the way
- a well-lit recipe card: one photo, short ingredient list, numbered steps

**Tone:** warm, uncluttered, mobile-first

**Anti-reference (never let it look like this):** cluttered recipe blogs: ad blocks, autoplay video, ingredient list buried under a life story

## Tokens

The canonical values live in the tokens file (see `structure` note in the
profile: `src/styles/tokens.css` or `static/tokens.css`). Rules of thumb:
one type scale (fixed ratio), at most two fonts, body >= 16px; one spacing
unit used everywhere; one accent color spent on the primary action only.
Change a token, not a one-off value. TODO markers in the tokens file are
choices still open -- settle them in the first design-loop pass.

## Aesthetic rubric (what `@design-reviewer` grades)

1. **Mockup fidelity.** The shipped screen matches the approved mockup in
   `mockups/` -- layout, hierarchy, states, and liveness (loading, empty,
   error states exist and look designed, not defaulted).
2. **No generic-AI tells.** Automatic fail for: purple-gradient hero, a
   three-rounded-cards feature grid, default-font-everywhere, uniform
   border-radius on every element, centered-everything layouts, emoji as
   icons on interactive elements.
3. **Tokens, not one-offs.** Colors, spacing, and type come from the tokens
   file; hardcoded values are findings.
4. **One deliberate risk.** Each major surface takes one justified aesthetic
   risk (an asymmetric layout, an expressive type moment, a signature
   interaction) consistent with the tone words above.
5. **Quiet floor.** Keyboard focus visible, contrast readable, motion
   respects reduced-motion, responsive at narrow widths.
