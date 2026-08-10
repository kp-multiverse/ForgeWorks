# Deviations log

When implementation must deviate from a plan, a mockup, or an acceptance
criterion: take the conservative option, add ONE entry here, keep going. The
owner reviews this file with the diff. `scripts/prune.py --check` (CI) owns
the entry cap -- the reasoning lives in the commit, not here. A feature's
entries are deleted at merge by `scripts/prune.py`; a residual that must
outlive its feature moves to `docs/SECURITY.md` or the feature's `notes`
first.

Format: `- YYYY-MM-DD F0NN: <what deviated and the conservative choice made>`
