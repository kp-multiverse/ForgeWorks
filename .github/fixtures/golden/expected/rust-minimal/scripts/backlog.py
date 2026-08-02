#!/usr/bin/env python3
"""Read `docs/features.json` -- the whole list, or one feature.

Two modes:

    python3 scripts/backlog.py              # regenerate docs/BACKLOG.md
    python3 scripts/backlog.py --feature F012   # print ONE entry, as JSON

The second mode exists for context economy. `features.json` grows with the
project (70K+ chars on a mature one); an agent building one feature needs one
entry. Reading the file whole to get it costs 20-35x the tokens and blows the
session's checkpoint budget -- see `AGENTS.md` `<context>`. Scripts may read it
whole; a working session should not.
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


def one(feats: list, fid: str) -> int:
    for ft in feats:
        if ft.get("id") == fid:
            print(json.dumps(ft, indent=2, ensure_ascii=False))
            return 0
    ids = ", ".join(f.get("id", "?") for f in feats)
    print(f"backlog: no feature {fid!r}. Known ids: {ids}")
    return 1


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
    feats = load()
    if feats is None:
        return 1
    if argv[:1] == ["--feature"]:
        if len(argv) != 2:
            print("usage: backlog.py --feature <id>")
            return 1
        return one(feats, argv[1])
    if argv:
        print(f"backlog: unknown argument {argv[0]!r}; use --feature <id> or no arguments")
        return 1
    return regenerate(feats)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
