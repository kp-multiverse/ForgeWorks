# Mockups -- the visual spec

One committed HTML file per user-visible surface, named `<feature-id>-<name>.html`
(e.g. `F003-dashboard.html`). The approved mockup IS the spec for that surface:
the mockup is approved in the `iteration` skill's GRILL step, built against in GREEN
(visual values from the tokens file, not the mockup's inline values), and the reviewer
grades the shipped screen against it. The committed path goes in the feature's
`mockup` field in `docs/features.json`; note the pick rationale in that
feature's `notes` field.

**Exactly one file per LIVE surface.** The 3-4 options explored at GRILL are
throwaway: only the winner is ever committed. When a surface is replaced, its
mockup is overwritten in the same branch; when a surface is removed, its mockup
is deleted with it. Superseded and rejected mockups live in git history, not
here. A directory with more mockups than the app has screens is stale by
definition -- nothing grades against them, so nothing keeps them true.
