# Product Vision: Ledgerline

The north star for this project. Captures the *what* and *why*. Stable across iterations.

For the enforceable feature list, see `features.json`.

---

## Positioning (Geoffrey Moore)

For **A solo freelancer who dreads sorting a quarter's transactions before filing taxes.**
who **dreads sorting a quarter's transactions before filing taxes**,
Ledgerline is a **CSV ledger categorizer**
that **categorizes automatically and only asks about what it is unsure of**.
Unlike **hand-sorting rows in a spreadsheet**,
we **low-confidence rows are flagged instead of silently miscategorized**.

## 5W answers

- **Who:** A solo freelancer who dreads sorting a quarter's transactions before filing taxes.
- **What:** A web app that turns a freelancer's raw bank CSV export into a categorized income/expense ledger.
- **Why:** Bank CSV exports are flat and uncategorized; freelancers currently hand-sort hundreds of rows in a spreadsheet before every filing.
- **When:** 2026-08-30
- **Where:** Static SPA hosted on the freelancer's own infra.
- **How:** see the core flow in `docs/features.json`

## Scope

**In scope** -- what v1 will do:

- CSV upload and rules-based categorization.
- Low-confidence flagging and manual recategorization.
- Clean CSV export of the final ledger.

**Out of scope (non-goals)** -- what it deliberately will NOT do:

- No bank API integrations in the first iteration; CSV upload only.
- No multi-currency support; single-currency ledgers only.

## Business goals

Outcome + metric + target. Cap at three.

- time to exported ledger -- under 10 minutes
- rows requiring manual recategorization -- under 10% on the reference export

## Success looks like

> A freelancer produces a confirmed, exportable ledger from a raw CSV in under ten minutes, down from an afternoon.

---

*Last updated: 2026-07-25*
