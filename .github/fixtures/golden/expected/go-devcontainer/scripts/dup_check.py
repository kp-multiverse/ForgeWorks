#!/usr/bin/env python3
"""Fail when the same block of source appears in two or more files.

DRY has a rule in `AGENTS.md` `<commands>` + the `iteration` skill, but a rule nobody
measures is a suggestion. This is the measurement: every 6-line window of
every source file, normalized and hashed. A window found in two different files
is copied code, copied markup, or -- most often in an agent-built project -- the
same paragraph of justification restated in five docstrings.

Normalization strips what varies without changing the shape: comments, blank
lines, string literals, numbers, and runs of whitespace. So two functions that
differ only in their strings still count as duplicates, which is the point.

    python3 scripts/dup_check.py            # check, exit 1 on a finding
    python3 scripts/dup_check.py --list     # print every finding, exit 0

Real exceptions -- framework boilerplate you cannot factor out -- go in a
committed `.dup-ignore`, one glob per line, `#` for comments. Adding a line
there is a decision someone can review; silently living with duplication is not.
"""

from __future__ import annotations

import fnmatch
import hashlib
import os
import re
import sys

WINDOW = 6
SUFFIXES = {".go"}
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".next", ".astro", "target", "vendor", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", "coverage", ".claude",
}
LINE_COMMENT = re.compile(r"^\s*(#|//|\*|/\*|--|<!--)")
LITERAL = re.compile(r'"[^"]*"|\'[^\']*\'|`[^`]*`')
NUMBER = re.compile(r"\b\d[\d_.]*\b")
WHITESPACE = re.compile(r"\s+")


def ignores() -> list[str]:
    if not os.path.exists(".dup-ignore"):
        return []
    with open(".dup-ignore", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


def sources(patterns: list[str]) -> list[str]:
    out = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if not name.endswith(tuple(SUFFIXES)):
                continue
            path = os.path.normpath(os.path.join(root, name))
            if any(fnmatch.fnmatch(path, p) for p in patterns):
                continue
            out.append(path)
    return sorted(out)


def normalize(path: str) -> list[tuple[str, int]]:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            raw = f.read().split("\n")
    except OSError:
        return []
    kept = []
    for lineno, line in enumerate(raw, 1):
        if not line.strip() or LINE_COMMENT.match(line):
            continue
        text = WHITESPACE.sub(" ", NUMBER.sub("N", LITERAL.sub("S", line))).strip()
        if len(text) < 8:  # braces, `end`, single tokens: shape, not substance
            continue
        kept.append((text, lineno))
    return kept


def main(argv: list[str]) -> int:
    listing = argv[:1] == ["--list"]
    patterns = ignores()
    windows: dict[str, list[tuple[str, int]]] = {}
    for path in sources(patterns):
        lines = normalize(path)
        for i in range(len(lines) - WINDOW + 1):
            body = "\n".join(t for t, _ in lines[i:i + WINDOW])
            windows.setdefault(hashlib.sha256(body.encode()).hexdigest(), []).append(
                (path, lines[i][1])
            )
    findings = {}
    for digest, hits in windows.items():
        files = {p for p, _ in hits}
        if len(files) > 1:
            findings.setdefault(tuple(sorted(files)), []).append(hits[0])
    if not findings:
        print(f"dup-check: OK ({len(windows)} windows, no block shared between files)")
        return 0
    for files, hits in sorted(findings.items(), key=lambda kv: -len(kv[1])):
        where = ", ".join(f"{p}:{n}" for p, n in sorted(hits)[:3])
        print(
            f"::error::{len(hits)} block(s) of {WINDOW}+ lines shared between "
            f"{len(files)} files: {' | '.join(files)} (first at {where})"
        )
    total = sum(len(h) for h in findings.values())
    print(
        f"dup-check: {total} duplicated block(s) across {len(findings)} file group(s). "
        "Extract to one home, or -- if this is framework boilerplate that cannot be "
        "factored out -- add the path to .dup-ignore with a reason."
    )
    return 0 if listing else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
