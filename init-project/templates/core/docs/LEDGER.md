# Ledger -- open features only

One physical line per state change, appended by the `iteration` skill.
Pointers, not prose: counts, SHAs, paths, `next:` -- the story lives in the
commit message. `scripts/prune.py --check` (CI) owns the entry cap, and
`scripts/prune.py` deletes a feature's lines at merge; commits are the
durable record.

Format: `Fnnn | STATE | round a/b | YYYY-MM-DD HH:MM | agent: X | evidence, next: <action>`

---
