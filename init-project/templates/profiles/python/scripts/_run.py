"""One home for the `uv run <name>` entry points.

Each shim in this package is a two-line wrapper around the shell script that
does the real work, so the wrapper logic lives here and nowhere else -- see the
`iteration` skill's GREEN step on saying it once.
"""

from __future__ import annotations

import os
import subprocess
import sys


def run(script_name: str) -> None:
    """Run the sibling shell script and exit with its status."""
    script = os.path.join(os.path.dirname(__file__), script_name)
    sys.exit(subprocess.call(["bash", script]))
