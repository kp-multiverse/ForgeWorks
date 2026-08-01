# Design direction: Ledgerline

The visual spec for this project. The `iteration` skill's GRILL step reads this
before any mockup; design reviews grade shipped screens against it and the
approved mockup in `mockups/`.

## Direction (from the setup interview)

**References -- what to steal, from where:**
- airtable.com -- dense tabular editing that stays legible at speed
- linear.app -- calm density, restrained color, keyboard-first affordances

**Tone:** calm, precise, unhurried

**Anti-reference (never let it look like this):** generic spreadsheet clone: default browser table styling, no visual hierarchy, red/green the only signal

## Tokens

The canonical values live in the tokens file for your language profile:
TypeScript: `src/styles/tokens.css`; Python: `static/tokens.css`; profiles
without a shipped tokens file (Go/Rust in v3.0.0): define the token table
right here in this file and treat it as canonical. Rules of thumb: one type
scale (fixed ratio), at most two fonts, body >= 16px; one spacing unit used
everywhere; one accent color spent on the primary action only. Change a
token, not a one-off value. TODO markers in the tokens file (or, for Go/Rust,
in this section) are choices still open -- settle them in the `iteration`
skill's GRILL step.

## Aesthetic rubric

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
