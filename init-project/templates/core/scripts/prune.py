#!/usr/bin/env python3
"""Mechanical doc death. Docs shrink by script, never by an LLM rewriting prose.

    python3 scripts/prune.py           # delete what closed features left behind
    python3 scripts/prune.py --check   # CI: fail on essay entries + unpruned leftovers

THIS SCRIPT OWNS THE ENTRY CAP below -- prose points here, never restates it.
It deletes whole files only and never rewrites an entry: rewriting is how an
owed obligation quietly becomes a done claim.

What dies when a feature reaches done/dropped: its plan file, mockups no
feature entry cites, probe files nothing cites. Move anything still decisive
FIRST -- to a gotcha, a SECURITY.md row, or the feature's `notes` -- then
prune. A successful prune also regenerates docs/BACKLOG.md.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backlog  # noqa: E402

GOTCHA_ENTRY_CAP = 800  # chars per `### ` entry; four short lines fit easily

GOTCHAS = os.path.join("docs", "gotchas.md")
PLANS = os.path.join("docs", "plans")
MOCKUPS = os.path.join("docs", "design", "mockups")
PROBES = os.path.join("docs", "probes")


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


def gotchas_check() -> list[str]:
    """Gotchas die by judgment (the code made them impossible), never by id --
    but an entry may not be an essay. Entry = `### ` to the next heading."""
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
    report = gotchas_check() if check else plans_prune(closed)
    report += mockups_prune(feats, check) + probes_prune(check)
    if check:
        for r in report:
            print(f"::error::prune-check: {r}")
        print(f"prune-check: {'FAIL' if report else 'OK (no essays, no leftovers)'}")
        return 1 if report else 0
    for r in report:
        print(f"prune: {r}")
    print(f"prune: {len(report)} deletion(s)")
    return backlog.regenerate(feats)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
