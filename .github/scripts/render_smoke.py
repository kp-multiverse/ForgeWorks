#!/usr/bin/env python3
"""Render smoke test: substitute core + each complete profile with safe values
and assert NO leftover {{PLACEHOLDER}} remains, and the manifest landed.

This proves template *completeness* (every placeholder used is fillable) and
feeds the per-profile CI gate runs via --emit. The real generation path is
init-project/render.py; its conditional matrix and hostile-value escaping are
locked byte-for-byte by .github/scripts/golden_test.py. Run from the repo root.
"""

from __future__ import annotations

import glob
import os
import re
import shutil
import sys
import tempfile

T = "init-project/templates"

# Profile values come from each profile.json -- the SAME file render.py reads.
# They used to be duplicated here, which is how {{SOURCE_SUFFIXES}} shipped in
# four profiles while this smoke test still failed on two of them: one fact,
# two homes, drifting. A gate reads the source; it does not keep a copy.
def profile_values(lang: str) -> dict:
    import json as _json
    with open(f"{T}/profiles/{lang}/profile.json", encoding="utf-8") as f:
        prof = _json.load(f)
    vals = {k.upper(): v for k, v in prof.items()
            if isinstance(v, str) and not k.startswith("_")}
    vals.pop("DISPLAY_NAME", None)
    vals["LANGUAGE_PRECOMMIT_HOOKS"] = "\n".join(prof.get("precommit_hooks") or [])
    vals["CI_SETUP_STEPS"] = "\n".join(prof.get("ci_setup_steps") or [])
    vals["LIBRARY_DOCS_URLS"] = "\n".join(prof.get("library_docs_urls") or [])
    for key, ph in {"type_annotations": "TYPE_ANNOTATION_NOTES", "imports": "IMPORT_NOTES",
                    "async": "ASYNC_NOTES", "errors": "ERROR_NOTES", "config": "CONFIG_NOTES",
                    "logging": "LOGGING_NOTES", "test_layout": "TEST_LAYOUT_NOTES",
                    "precommit_hooks": "PRECOMMIT_HOOKS_NOTES"}.items():
        notes = (prof.get("notes") or {}).get(key)
        if not notes:
            raise SystemExit(f"{lang}/profile.json: notes.{key} is missing or empty. "
                             f"Defaulting it is how a missing key passed unnoticed before.")
        vals[ph] = "\n".join(notes)
    return vals

COMMON = dict(
    PROJECT_NAME="Smoke", PROJECT_SLUG="smoke", PROJECT_GOAL="a goal",
    PRIMARY_USER="dev", CORE_PROBLEM="x", CORE_JOURNEY="1. x", SUCCESS_MEASURE="x",
    RISKIEST_ASSUMPTION="x", NON_GOALS="- x", LANGUAGE="L", LANGUAGE_VERSION="1",
    HAS_FRONTEND="no", BACKEND_FRAMEWORK="none", AI_FEATURES="none", VECTOR_DB="none",
    LLM_PROVIDER="none", EMBEDDINGS_MODEL="none", DATABASE="none", USES_DEVCONTAINER="no",
    DATE="2026", PACKAGE_MANAGER="pm", ADD_DEP_COMMAND="add", TEST_RUNNER="t",
    TEST_COMMAND="t", LINT_TOOL="l", LINT_COMMAND="l", FORMAT_TOOL="f", FORMAT_COMMAND="f",
    TYPE_TOOL="ty", TYPE_COMMAND="ty", CI_SETUP_STEPS="# ci", LIBRARY_DOCS_URLS="- d",
    AI_DISCIPLINE_BLOCK="", CODEX_REVIEW_STEP="", CODEX_ROSTER_NOTE="", MEMORY_DOC_LINE="",
    AGENT_MATRIX="### Claude Code\n\nx",
    POSITIVE_REFERENCE_TEXT="x", NEGATIVE_REFERENCE_TEXT="",
    REQ_AC_LIST="- [ ] **REQ-AC1:** x", OTHER_USERS="- x", CONSTRAINT_TIME="x",
    CONSTRAINT_COST="x", CONSTRAINT_DATA="x", FIRST_MILESTONE="x",
    DEPLOYMENT_TARGET="x", SCALE_EXPECTATIONS="x", INTEGRATIONS="- x",
    PAIN_POINT="x", PRODUCT_CATEGORY="x", CURRENT_ALTERNATIVE="x",
    KEY_BENEFIT="x", KEY_DIFFERENTIATOR="x", IN_SCOPE_LIST="- x",
    SUCCESS_METRICS="- x", READS_UNTRUSTED="no", HOLDS_PRIVATE_DATA="no",
    ACTS_OUTWARD="no", E2E_BROWSER_INSTALL_STEP="# no browser",
    DESIGN_REFERENCES="- x", DESIGN_TONE="x", DESIGN_ANTI_REFERENCE="x",
    PRD_SURFACES="- Smoke surface",
    **{k: "x" for k in ("TYPE_ANNOTATION_NOTES", "IMPORT_NOTES", "ASYNC_NOTES",
                        "ERROR_NOTES", "CONFIG_NOTES", "LOGGING_NOTES",
                        "TEST_LAYOUT_NOTES", "PRECOMMIT_HOOKS_NOTES")},
)

# The rendered tree simulates a NO-AI, no-Claude-Code project, so every AI and
# CC fence is deleted wholesale (smoke only asserts placeholder completeness,
# not the keep-vs-drop distinction render.py applies per real answers) -- in
# EVERY file that carries one (SECURITY.md, reviewer.md,
# and any future fenced file).
FENCE = re.compile(r"<!-- (?:AI|CC)-[A-Z]+-START -->.*?<!-- (?:AI|CC)-[A-Z]+-END -->\n?", re.S)

# Hidden files/dirs (.claude, .github, .env.example, ...) that MUST be visited.
# glob('**/*') silently skips dotfiles, so we walk instead and assert coverage.
SENTINELS = (".claude/hooks/quality-gate.sh", ".github/workflows/qa.yml", ".env.example")


def all_files(root: str) -> list[str]:
    out = []
    for dirpath, _, names in os.walk(root):  # os.walk includes dotfiles/dirs
        out += [os.path.join(dirpath, n) for n in names]
    return out


def render(lang: str, out: str) -> list[str]:
    shutil.copytree(f"{T}/core", out)
    for root, _, files in os.walk(f"{T}/profiles/{lang}"):
        rel = os.path.relpath(root, f"{T}/profiles/{lang}")
        for fn in files:
            if rel == "." and fn == "profile.json":
                continue  # renderer input, never part of a generated project
            d = os.path.join(out, rel)
            os.makedirs(d, exist_ok=True)
            shutil.copy2(os.path.join(root, fn), os.path.join(d, fn))
    if lang == "python" and os.path.exists(f"{out}/pyproject.toml.example"):
        os.rename(f"{out}/pyproject.toml.example", f"{out}/pyproject.toml")
    mapping = {**COMMON, **profile_values(lang)}
    for f in all_files(out):
        try:
            c = open(f, encoding="utf-8").read()
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        c = FENCE.sub("", c)
        for k, v in mapping.items():
            c = c.replace("{{%s}}" % k, v)
        open(f, "w", encoding="utf-8").write(c)
    leftover = []
    for f in all_files(out):
        try:
            leftover += re.findall(r"\{\{[A-Z0-9_]+\}\}", open(f, encoding="utf-8").read())
        except (UnicodeDecodeError, IsADirectoryError):
            pass
    if not os.path.exists(os.path.join(out, mapping["MANIFEST_FILE"])):
        leftover.append("<missing manifest %s>" % mapping["MANIFEST_FILE"])
    # Assert the hidden files were actually present and visited.
    for s in SENTINELS:
        if not os.path.exists(os.path.join(out, s)):
            leftover.append("<sentinel not rendered: %s>" % s)
    return leftover


def main() -> int:
    # --emit <lang> <dir>: render ONE merged core+profile tree to <dir> so CI can
    # run the language's real quality gate on the same shape a generated project
    # has (profile-only runs miss core/profile interactions, e.g. a formatter
    # that scans core files).
    if len(sys.argv) == 4 and sys.argv[1] == "--emit":
        lang, out = sys.argv[2], sys.argv[3]
        left = render(lang, out)
        if left:
            print(f"FAIL [{lang}] leftover/missing: {sorted(set(left))}")
            return 1
        print(f"ok   [{lang}] merged core+profile rendered to {out}")
        return 0
    rc = 0
    for lang in ("python", "typescript", "go", "rust"):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "proj")
            left = render(lang, out)
            if left:
                print(f"FAIL [{lang}] leftover/missing: {sorted(set(left))}")
                rc = 1
            else:
                print(f"ok   [{lang}] rendered clean, manifest present")
    return rc


if __name__ == "__main__":
    sys.exit(main())
