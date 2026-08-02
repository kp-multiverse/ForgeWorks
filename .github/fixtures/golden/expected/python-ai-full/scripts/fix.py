"""`uv run fix` -- local auto-repair (ruff --fix + format write). See _run.py."""

from __future__ import annotations

from scripts._run import run


def main() -> None:
    run("fix.sh")
