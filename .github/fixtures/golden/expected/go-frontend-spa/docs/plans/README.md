# Plans -- one per FEATURE, alive only while it is being built

One file per FEATURE (`<feature-id>.md`): approach, riskiest assumption + how
it was de-risked, data shapes, threat model, and test list. Owner approval
happens once, live, at the end of the `iteration` skill's GRILL step. Chores
don't require plans; use the PR description instead.

**A plan is deleted at MERGE.** It is working state for one feature, not a
record. Everything durable it produced has a permanent home already:

| In the plan | Durable home |
|---|---|
| Acceptance criteria (EARS) | the feature's `acceptance` array in `docs/features.json` |
| Test list | the feature's `tests` array, and the tests themselves |
| Threat model | new rows / edited checklist lines in `docs/SECURITY.md` |
| The approved mockup | `docs/design/mockups/<id>-<name>.html` |
| What shipped, and the evidence | the commit, and the ledger line |
| A surprise reality handed you | `docs/gotchas.md` |

If something in the plan is not in one of those and still changes a future
decision, put it there **first** -- then delete the plan. Keeping the file to
hold it is how a project ends up with hundreds of docs nobody reads.

The full text stays in git history if anyone ever needs it.
