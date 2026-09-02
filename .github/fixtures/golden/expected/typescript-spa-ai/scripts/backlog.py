#!/usr/bin/env python3
"""Regenerate docs/BACKLOG.md, the human-readable view of docs/features.json.

    python3 scripts/backlog.py

`scripts/prune.py` runs this at every merge, so the file is rarely written by
hand. To read ONE feature, use `scripts/feature.py <id>` -- a working session
never reads features.json whole.
"""

from __future__ import annotations

import json
import os
import sys

SRC = os.path.join("docs", "features.json")
DST = os.path.join("docs", "BACKLOG.md")
ICONS = {"done": "[x]", "in-progress": "[~]", "todo": "[ ]", "dropped": "[-]"}


def load() -> list | None:
    try:
        with open(SRC, encoding="utf-8") as f:
            return json.load(f)["features"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"backlog: cannot read {SRC}: {exc}")
        return None


def regenerate(feats: list) -> int:
    lines = [
        "# Backlog",
        "",
        "Generated from `docs/features.json` by `scripts/backlog.py` -- do not edit by hand.",
        "Order is priority order. `[x]` done, `[~]` in progress, `[ ]` todo, `[-]` dropped.",
        "",
    ]
    done = 0
    for ft in feats:
        fid = ft.get("id")
        if not fid:
            print(f"backlog: entry missing id: {ft!r}")
            return 1
        icon = ICONS.get(ft.get("status", "todo"), "[?]")
        if ft.get("status") == "done":
            done += 1
        lines.append(f"- {icon} **{fid}** {ft.get('title', '')}")
    lines += ["", f"{done}/{len(feats)} done.", ""]
    with open(DST, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"backlog: wrote {DST} ({done}/{len(feats)} done)")
    return 0


def main(argv: list[str]) -> int:
    if argv:
        print(f"backlog: unknown argument {argv[0]!r}; this script takes none")
        return 1
    feats = load()
    return 1 if feats is None else regenerate(feats)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
