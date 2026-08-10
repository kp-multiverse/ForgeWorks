#!/usr/bin/env python3
"""Mechanical doc death. Docs shrink by script, never by an LLM rewriting prose.

    python3 scripts/prune.py           # delete what closed features left behind
    python3 scripts/prune.py --check   # CI: fail on essay entries + unpruned leftovers

THIS SCRIPT OWNS THE ENTRY CAPS below -- prose points here, never restates them.
It deletes whole lines and whole files only. It never rewrites an entry:
rewriting is how an owed obligation quietly becomes a done claim.

What dies when a feature reaches done/dropped: its LEDGER lines (the ledger
holds open features only; commits are the durable record), its deviations
lines, its plan file, mockups no feature entry cites, probe files nothing
cites. Move anything still decisive FIRST -- to a gotcha, a SECURITY.md row,
or the feature's `notes` -- then prune.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

LEDGER_LINE_CAP = 400  # chars; one physical line per state change
DEVIATION_ENTRY_CAP = 400  # chars per `- ` bullet (with its wrapped lines)
GOTCHA_ENTRY_CAP = 800  # chars per `### ` entry; four short lines fit easily

LEDGER = os.path.join("docs", "LEDGER.md")
DEVIATIONS = os.path.join("docs", "deviations.md")
GOTCHAS = os.path.join("docs", "gotchas.md")
PLANS = os.path.join("docs", "plans")
MOCKUPS = os.path.join("docs", "design", "mockups")
PROBES = os.path.join("docs", "probes")
FID = re.compile(r"\bF\d{3}\b")


def features() -> list[dict]:
    with open(os.path.join("docs", "features.json"), encoding="utf-8") as f:
        return json.load(f)["features"]


def closed_ids(feats: list[dict]) -> set[str]:
    return {ft["id"] for ft in feats if ft["status"] in ("done", "dropped")}


def read_lines(path: str) -> list[str]:
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines(keepends=True)


def ledger_prune(closed: set[str], check: bool) -> list[str]:
    """Entry = one physical line starting with an F-id. Header lines stay."""
    out: list[str] = []
    kept: list[str] = []
    for n, ln in enumerate(read_lines(LEDGER), 1):
        m = FID.match(ln.strip())
        if not m:
            kept.append(ln)
            continue
        if check and len(ln.rstrip("\n")) > LEDGER_LINE_CAP:
            out.append(
                f"{LEDGER}:{n}: entry is {len(ln.rstrip())} chars "
                f"(cap {LEDGER_LINE_CAP}). Pointers, not prose -- counts, SHAs, "
                f"paths, `next:`. The story belongs in the commit message."
            )
        if m.group(0) in closed:
            if check:
                out.append(
                    f"{LEDGER}:{n}: {m.group(0)} is closed -- run "
                    f"`python3 scripts/prune.py` (move anything still decisive "
                    f"to a gotcha or the feature's notes first)."
                )
            else:
                out.append(f"deleted {LEDGER}:{n} ({m.group(0)} closed)")
                continue
        kept.append(ln)
    if not check and out:
        with open(LEDGER, "w", encoding="utf-8") as f:
            f.writelines(kept)
    return out


def bullet_entries(path: str) -> list[tuple[int, str]]:
    """Group a `- ` bullet with its wrapped continuation lines (any indent)."""
    entries: list[tuple[int, str]] = []
    open_entry = False
    for n, ln in enumerate(read_lines(path), 1):
        if ln.startswith("- "):
            entries.append((n, ln))
            open_entry = True
        elif not ln.strip() or ln.startswith("#") or ln.startswith("`"):
            open_entry = False
        elif open_entry:
            n0, body = entries[-1]
            entries[-1] = (n0, body + ln)
    return entries


def deviations_prune(closed: set[str], check: bool) -> list[str]:
    out: list[str] = []
    doomed: set[int] = set()
    for n, entry in bullet_entries(DEVIATIONS):
        text = entry.rstrip("\n")
        if check and len(text) > DEVIATION_ENTRY_CAP:
            out.append(
                f"{DEVIATIONS}:{n}: entry is {len(text)} chars "
                f"(cap {DEVIATION_ENTRY_CAP}). One line: what deviated, the "
                f"conservative choice. The reasoning lives in the commit."
            )
        m = FID.search(text)
        if m and m.group(0) in closed:
            if check:
                out.append(
                    f"{DEVIATIONS}:{n}: {m.group(0)} is closed -- run "
                    f"`python3 scripts/prune.py` (a residual that outlives its "
                    f"feature belongs in SECURITY.md or the feature's notes)."
                )
            else:
                doomed.update(range(n, n + len(entry.splitlines())))
                out.append(f"deleted {DEVIATIONS}:{n} ({m.group(0)} closed)")
    if not check and doomed:
        kept = [ln for i, ln in enumerate(read_lines(DEVIATIONS), 1) if i not in doomed]
        with open(DEVIATIONS, "w", encoding="utf-8") as f:
            f.writelines(kept)
    return out


def gotchas_check() -> list[str]:
    """Gotchas die by judgment (the code made them impossible), never by id --
    but an entry may not be an essay. Entry = `### ` to the next `### `."""
    out: list[str] = []
    start, size = 0, 0
    for n, ln in enumerate(read_lines(GOTCHAS) + ["### sentinel"], 1):
        if ln.startswith("### ") or ln.startswith("## "):
            if start and size > GOTCHA_ENTRY_CAP:
                out.append(
                    f"{GOTCHAS}:{start}: entry is {size} chars "
                    f"(cap {GOTCHA_ENTRY_CAP}). Four short lines; a code sample "
                    f"belongs in a comment where it bites."
                )
            start, size = (n, 0) if ln.startswith("### ") else (0, 0)
        elif start:
            size += len(ln)
    return out


def plans_prune(closed: set[str]) -> list[str]:
    out: list[str] = []
    if not os.path.isdir(PLANS):
        return out
    for name in sorted(os.listdir(PLANS)):
        stem = name[:-3] if name.endswith(".md") else ""
        if not stem or name == "README.md":
            continue
        if any(stem == i or stem.lower().startswith(i.lower() + "-") for i in closed):
            os.remove(os.path.join(PLANS, name))
            out.append(f"deleted {PLANS}/{name} (feature closed)")
    return out


def mockups_prune(feats: list[dict], check: bool) -> list[str]:
    out: list[str] = []
    cited = {ft.get("mockup") for ft in feats if ft.get("mockup")}
    if not os.path.isdir(MOCKUPS):
        return out
    for name in sorted(os.listdir(MOCKUPS)):
        rel = f"{MOCKUPS}/{name}".replace(os.sep, "/")
        if name == "README.md" or rel in cited:
            continue
        if check:
            out.append(
                f"{rel}: no feature entry cites this mockup -- a losing "
                f"candidate. Run `python3 scripts/prune.py`."
            )
        else:
            os.remove(os.path.join(MOCKUPS, name))
            out.append(f"deleted {rel} (uncited mockup)")
    return out


def probes_prune(check: bool) -> list[str]:
    out: list[str] = []
    if not os.path.isdir(PROBES):
        return out
    for name in sorted(os.listdir(PROBES)):
        if name == "README.md":
            continue
        rel = f"{PROBES}/{name}".replace(os.sep, "/")
        try:
            r = subprocess.run(
                ["git", "grep", "-l", "-F", rel], capture_output=True, text=True, timeout=30
            )
        except (OSError, subprocess.SubprocessError):
            return out  # cannot verify citations -> touch nothing
        if r.returncode > 1:  # 1 = no matches; >1 = not a repo / git error
            return out
        hits = [h for h in r.stdout.splitlines() if not h.startswith(PROBES.replace(os.sep, "/"))]
        if hits:
            continue
        if check:
            out.append(f"{rel}: nothing cites this probe -- run `python3 scripts/prune.py`.")
        else:
            os.remove(os.path.join(PROBES, name))
            out.append(f"deleted {rel} (uncited probe)")
    return out


def main(argv: list[str]) -> int:
    check = argv[:1] == ["--check"]
    try:
        feats = features()
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"::error::prune: cannot read docs/features.json: {exc}")
        return 1
    closed = closed_ids(feats)
    report = ledger_prune(closed, check) + deviations_prune(closed, check)
    report += gotchas_check() if check else plans_prune(closed)
    report += mockups_prune(feats, check) + probes_prune(check)
    if check:
        for r in report:
            print(f"::error::prune-check: {r}")
        print(f"prune-check: {'FAIL' if report else 'OK (no essays, no leftovers)'}")
        return 1 if report else 0
    for r in report:
        print(f"prune: {r}")
    print(f"prune: {len(report)} deletion(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
