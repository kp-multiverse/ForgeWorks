#!/usr/bin/env python3
"""Print what a fresh session needs to pick the work back up. This is `go`.

    python3 scripts/resume.py           # the brief
    python3 scripts/resume.py --check   # CI: would `go` work right now?

## Why this derives instead of storing

The obvious design is a `docs/RESUME.md` the agent rewrites at every state
change. That is wrong twice over. It would be a THIRD writer for facts that
already have two -- `docs/features.json` knows which feature is live,
`docs/LEDGER.md` knows the phase -- which is the same "one fact written twice"
defect the doc budgets were built to kill. And a hand-rewritten snapshot is
prose discipline pretending to be a transaction: crash between the state change
and the rewrite and it describes the PREVIOUS phase, so `go` resumes into the
wrong work confidently. Confidently is the dangerous part.

So nothing here is stored. Every field is read from the file that already owns
it, and the fields are cross-checked. When they disagree this REFUSES to print
a brief, because a resume built on contradictory pointers is worse than no
resume: you cannot tell it went wrong until the work is done wrong.

## What the owner has to do

Nothing. Never "remember this before I clear". If a decision only exists in the
conversation, the `iteration` skill's CHECKPOINT step is what writes it down --
this script only reads.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

FEATURES = os.path.join("docs", "features.json")
LEDGER = os.path.join("docs", "LEDGER.md")
PLANS = os.path.join("docs", "plans")
PHASES = ("GRILL", "RED", "GREEN", "REVIEW", "MERGED")
NEXT_PHASE = {"GRILL": "RED", "RED": "GREEN", "GREEN": "REVIEW", "REVIEW": "MERGE"}


def git(*args: str) -> str:
    try:
        r = subprocess.run(("git",) + args, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def ledger_lines() -> list[str]:
    if not os.path.exists(LEDGER):
        return []
    with open(LEDGER, encoding="utf-8") as f:
        return [ln.strip() for ln in f if "|" in ln and not ln.lstrip().startswith(("#", "Format", "F012"))]


def collect() -> tuple[dict, list[str]]:
    """Read every pointer from the file that owns it. Never guess."""
    problems: list[str] = []
    state: dict = {}
    try:
        with open(FEATURES, encoding="utf-8") as f:
            feats = json.load(f)["features"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        return {}, [f"cannot read {FEATURES}: {exc}"]

    live = [ft for ft in feats if ft["status"] == "in-progress"]
    if len(live) > 1:
        ids = ", ".join(ft["id"] for ft in live)
        problems.append(
            f"{len(live)} features are in-progress ({ids}). `go` cannot choose. "
            f"Finish or park one -- an abandoned in-progress entry is the usual cause."
        )
    elif not live:
        todo = next((ft for ft in feats if ft["status"] == "todo"), None)
        state["idle"] = True
        state["next_todo"] = todo["id"] if todo else None
        state["next_title"] = todo["title"] if todo else None
        return state, problems

    ft = live[0]
    state["feature"] = ft
    state["id"] = ft["id"]

    lines = [ln for ln in ledger_lines() if ln.startswith(ft["id"])]
    if not lines:
        problems.append(
            f"{ft['id']} is in-progress but has no line in {LEDGER}. The ledger is "
            f"how a restart learns the phase; without it `go` is guessing."
        )
    else:
        last = lines[-1]
        state["ledger"] = last
        parts = [p.strip() for p in last.split("|")]
        phase = next((p for p in parts if p in PHASES), None)
        if not phase:
            problems.append(f"last {LEDGER} line for {ft['id']} names no known phase: {last}")
        state["phase"] = phase
        # `next:` rides in the evidence field, e.g.
        #   ... | agent: main | plan: docs/plans/F012.md, next: write AC1-AC3 tests
        low = last.lower()
        state["next"] = last[low.index("next:") + 5:].strip() if "next:" in low else None

    plan = os.path.join(PLANS, f"{ft['id']}.md")
    if not os.path.exists(plan):
        match = [n for n in sorted(os.listdir(PLANS))] if os.path.isdir(PLANS) else []
        match = [n for n in match if n.lower().startswith(ft["id"].lower()) and n.endswith(".md")]
        plan = os.path.join(PLANS, match[0]) if match else ""
    if plan:
        state["plan"] = plan
    else:
        problems.append(
            f"{ft['id']} is in-progress but has no plan under {PLANS}/. Either it was "
            f"deleted early, or the feature never went through GRILL."
        )

    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    state["branch"] = branch
    if branch and branch != "HEAD" and ft["id"].lower() not in branch.lower() and branch != "main":
        problems.append(
            f"on branch {branch!r}, which does not name {ft['id']}. Either you are on "
            f"the wrong branch or the wrong feature is marked in-progress."
        )
    state["dirty"] = bool(git("status", "--porcelain"))
    return state, problems


def brief(state: dict) -> str:
    if state.get("idle"):
        if state.get("next_todo"):
            return (f"Nothing in progress. Next in the backlog: "
                    f"{state['next_todo']} -- {state['next_title']}.\n"
                    f"Say the word and I will start it at GRILL.")
        return "Nothing in progress and nothing todo. The backlog is empty."
    ft = state["feature"]
    phase = state.get("phase") or "?"
    lines = [
        f"{ft['id']} -- {ft['title']}",
        f"  phase   {phase} done -> next {NEXT_PHASE.get(phase, '?')}",
        f"  branch  {state.get('branch') or '?'}{'  (uncommitted changes present)' if state.get('dirty') else ''}",
        f"  plan    {state.get('plan') or '(none)'}",
    ]
    if state.get("next"):
        lines.append(f"  next    {state['next']}")
    lines.append(f"  read    python3 scripts/backlog.py --feature {ft['id']}  +  {state.get('plan') or ''}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    checking = argv[:1] == ["--check"]
    state, problems = collect()
    if problems:
        for p in problems:
            print(f"::error::resume: {p}")
        print("\nresume: the pointers disagree, so no brief is printed. Fix the "
              "contradiction above before continuing -- resuming from a wrong "
              "pointer costs more than the minute this takes.")
        return 1
    if checking:
        print("resume-check: OK (`go` has exactly one unambiguous place to start)")
        return 0
    print(brief(state))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
