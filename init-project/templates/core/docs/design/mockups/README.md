# Mockups -- the visual spec

One committed HTML file per user-visible surface, named `<feature-id>-<name>.html`
(e.g. `F003-dashboard.html`). The approved mockup IS the spec for that surface:
the mockup is approved in the `iteration` skill's GRILL step, built against in GREEN
(visual values from the tokens file, not the mockup's inline values), and the reviewer
grades the shipped screen against it. The committed path goes in the feature's
`mockup` field in `docs/features.json`; note the pick rationale in that
feature's `notes` field. Superseded mockups stay in git history;
keep only the current one per surface here.
