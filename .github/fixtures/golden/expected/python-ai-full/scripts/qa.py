"""`uv run qa` -- verify only (lint, format check, types, tests). See _run.py."""

from __future__ import annotations

from scripts._run import run


def main() -> None:
    run("qa.sh")
