#!/usr/bin/env python3
"""Validate docs/features.json -- the machine-checked feature list.

Checks: schema shape, unique F-ids, status/tier enums, and the hard rules:
a `done` feature must cite at least one test whose file exists, a `dropped`
feature must carry a reason in `notes`, and a feature with a surface (not "none")
may not leave todo without citing an existing mockup file under docs/design/mockups/.
Test EXECUTION is the quality gate's job, not this script's. Run locally or in CI:

    python3 scripts/features_check.py
"""

from __future__ import annotations

import json
import os
import re
import sys

REQUIRED = ("id", "title", "intent", "serves", "acceptance", "tests", "status", "tier", "surface")
STATUSES = {"todo", "in-progress", "done", "dropped"}
TIERS = {"chore", "feature"}
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
        surface = ft["surface"]
        if not isinstance(surface, str) or not surface.strip():
            errors.append(f"{where}: surface must be a non-empty string ('none' if not visual)")
        elif surface != "none" and ft["status"] != "todo":
            mockup = ft.get("mockup")
            if not isinstance(mockup, str) or not mockup.strip():
                errors.append(
                    f"{where}: surface feature past todo needs a 'mockup' path "
                    f"(docs/design/mockups/...) -- no mockup, no code"
                )
            elif os.path.isabs(mockup) or ".." in mockup.split(os.sep):
                errors.append(
                    f"{where}: mockup must be a repo-relative "
                    f"path with no '..' component: {mockup}"
                )
            elif not mockup.startswith("docs/design/mockups/") or not os.path.isfile(mockup):
                errors.append(f"{where}: mockup file missing: {mockup}")
        acceptance = ft["acceptance"]
        if not isinstance(acceptance, list) or not acceptance:
            errors.append(f"{where}: acceptance must be a non-empty list")
        else:
            for j, a in enumerate(acceptance):
                if not isinstance(a, str) or not a.strip():
                    errors.append(f"{where}: acceptance[{j}] must be a non-empty string")
        tests = ft["tests"]
        if not isinstance(tests, list):
            errors.append(f"{where}: tests must be a list")
            tests = []
        else:
            for j, t in enumerate(tests):
                if not isinstance(t, str) or not t.strip():
                    errors.append(f"{where}: tests[{j}] must be a non-empty string")
                    continue
                test_file = t.split("::", 1)[0]
                if not test_file:
                    errors.append(f"{where}: tests[{j}] has no file part before '::'")
                    continue
                if os.path.isabs(test_file) or ".." in test_file.split(os.sep):
                    errors.append(
                        f"{where}: tests[{j}] must be a repo-relative "
                        f"path with no '..' component: {test_file}"
                    )
                    continue
                if ft["status"] == "done" and not os.path.isfile(test_file):
                    errors.append(f"{where}: cited test file missing: {test_file}")
        if ft["status"] == "done" and not tests:
            errors.append(f"{where}: done with no mapped tests")
        notes = ft.get("notes")
        if "notes" in ft and not isinstance(notes, str):
            errors.append(f"{where}: notes must be a string")
        if ft["status"] == "dropped" and not str(notes or "").strip():
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
