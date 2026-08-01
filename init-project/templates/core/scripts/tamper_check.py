#!/usr/bin/env python3
"""Test-tamper guard: a changed or deleted existing test needs a stated reason.

Compares HEAD against the merge base with TAMPER_BASE (default origin/main,
fallback main). Any Modified/Deleted file matching the profile's test-path
pattern requires a "test-change:" line somewhere in the commit messages of
the range. Added tests are always fine. Enforces the AGENTS.md hard rule
mechanically. Run locally or in CI:

    python3 scripts/tamper_check.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

TEST_PATH_RE = re.compile(r"{{TEST_PATH_REGEX}}")
REASON_RE = re.compile(r"^\s*test-change:\s*\S", re.MULTILINE)


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def main() -> int:
    base = os.environ.get("TAMPER_BASE", "origin/main")
    for candidate in (base, "main"):
        try:
            merge_base = _git("merge-base", candidate, "HEAD").strip()
            break
        except subprocess.CalledProcessError:
            continue
    else:
        print("tamper-check: SKIP (no base branch found)")
        return 0
    if merge_base == _git("rev-parse", "HEAD").strip():
        print("tamper-check: OK (no commits ahead of base)")
        return 0
    changed = _git("diff", "--name-status", f"{merge_base}..HEAD")
    touched = [
        (status, path)
        for line in changed.splitlines()
        for status, _, path in [line.partition("\t")]
        if status[:1] in ("M", "D", "R") and TEST_PATH_RE.search(path)
    ]
    if not touched:
        print("tamper-check: OK (no existing tests modified or deleted)")
        return 0
    messages = _git("log", "--format=%B", f"{merge_base}..HEAD")
    if REASON_RE.search(messages):
        print(f"tamper-check: OK ({len(touched)} test change(s), reason stated)")
        return 0
    print("tamper-check: FAIL -- existing tests changed with no stated reason.")
    for status, path in touched:
        print(f"  - {status}\t{path}")
    print('State the reason with a "test-change: <why>" line in a commit body.')
    return 1


if __name__ == "__main__":
    sys.exit(main())
