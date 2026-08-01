#!/usr/bin/env python3
"""Regenerate docs/BACKLOG.md from docs/features.json.

One line per feature, array order preserved (priority order). Run at every
MERGE (iteration skill step 5.6) or any time by hand:

    python3 scripts/backlog.py
"""

from __future__ import annotations

import json
import os
import sys

SRC = os.path.join("docs", "features.json")
DST = os.path.join("docs", "BACKLOG.md")
ICONS = {"done": "[x]", "in-progress": "[~]", "todo": "[ ]", "dropped": "[-]"}


def main() -> int:
    try:
        with open(SRC, encoding="utf-8") as f:
            feats = json.load(f)["features"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"backlog: cannot read {SRC}: {exc}")
        return 1
    lines = [
        "# Backlog",
        "",
        "Generated from `docs/features.json` by `scripts/backlog.py` -- do not edit by hand.",
        "Order is priority order. `[x]` done, `[~]` in progress, `[ ]` todo, `[-]` dropped.",
        "",
    ]
    done = 0
    for ft in feats:
        icon = ICONS.get(ft.get("status", "todo"), "[?]")
        if ft.get("status") == "done":
            done += 1
        lines.append(f"- {icon} **{ft['id']}** {ft.get('title', '')}")
    lines += ["", f"{done}/{len(feats)} done.", ""]
    with open(DST, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"backlog: wrote {DST} ({done}/{len(feats)} done)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
