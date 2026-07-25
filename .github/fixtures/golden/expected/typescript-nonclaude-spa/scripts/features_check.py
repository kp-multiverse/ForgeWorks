#!/usr/bin/env python3
"""Validate docs/features.json -- the machine-checked feature list.

Checks: schema shape, unique F-ids, status/tier enums, and the two hard
rules: a `done` feature must cite at least one test whose file exists, and a
`dropped` feature must carry a reason in `notes`. Test EXECUTION is the
quality gate's job, not this script's. Run locally or in CI:

    python3 scripts/features_check.py
"""
from __future__ import annotations

import json
import os
import re
import sys

REQUIRED = ("id", "title", "intent", "serves", "acceptance", "tests",
            "status", "tier")
STATUSES = {"todo", "in-progress", "done", "dropped"}
TIERS = {"light", "standard", "high-risk"}
ID_RE = re.compile(r"^F\d{3}$")
PATH = os.path.join("docs", "features.json")


def check() -> list[str]:
    try:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{PATH}: {exc}"]
    feats = data.get("features")
    if not isinstance(feats, list) or not feats:
        return [f"{PATH}: 'features' must be a non-empty list"]
    errors: list[str] = []
    seen: set[str] = set()
    for i, ft in enumerate(feats):
        where = f"features[{i}]"
        if not isinstance(ft, dict):
            errors.append(f"{where}: must be an object")
            continue
        missing = [k for k in REQUIRED if k not in ft]
        if missing:
            errors.append(f"{where}: missing {missing}")
            continue
        fid = ft["id"]
        where = f"{fid} ({where})"
        if not isinstance(fid, str) or not ID_RE.match(fid):
            errors.append(f"{where}: id must match F000-F999")
        elif fid in seen:
            errors.append(f"{where}: duplicate id")
        else:
            seen.add(fid)
        if ft["status"] not in STATUSES:
            errors.append(f"{where}: status must be one of {sorted(STATUSES)}")
        if ft["tier"] not in TIERS:
            errors.append(f"{where}: tier must be one of {sorted(TIERS)}")
        if not isinstance(ft["acceptance"], list) or not ft["acceptance"]:
            errors.append(f"{where}: acceptance must be a non-empty list")
        tests = ft["tests"]
        if not isinstance(tests, list):
            errors.append(f"{where}: tests must be a list")
            tests = []
        if ft["status"] == "done":
            if not tests:
                errors.append(f"{where}: done with no mapped tests")
            for t in tests:
                test_file = str(t).split("::", 1)[0]
                if not os.path.exists(test_file):
                    errors.append(f"{where}: cited test file missing: {test_file}")
        if ft["status"] == "dropped" and not str(ft.get("notes") or "").strip():
            errors.append(f"{where}: dropped without a reason in notes")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("features-check: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    with open(PATH, encoding="utf-8") as f:
        feats = json.load(f)["features"]
    done = sum(1 for ft in feats if ft["status"] == "done")
    print(f"features-check: OK ({done}/{len(feats)} done)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
