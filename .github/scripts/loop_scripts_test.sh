#!/usr/bin/env bash
# The loop's state scripts (feature.py, resume.py, prune.py, features_check.py)
# on a rendered fixture: a feature walks GRILL -> done and every pointer agrees
# at each step. Run from the repo root.
set -euo pipefail
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
python3 init-project/render.py --answers .github/fixtures/golden/python-ai-full.json \
  --core init-project/templates/core --profile init-project/templates/profiles/python \
  --out "$tmp/proj" >/dev/null
cd "$tmp/proj" && git init -q && git -c user.name=ci -c user.email=ci@example.com commit -q --allow-empty -m init && git add -A && git -c user.name=ci -c user.email=ci@example.com commit -qm scaffold
ok() { out=$("$@" 2>&1) || { echo "loop-scripts: FAIL -- $*"; echo "$out"; exit 1; }; }
fails() { if out=$("$@" 2>&1); then echo "loop-scripts: FAIL -- expected failure: $*"; echo "$out"; exit 1; fi; }
ok python3 scripts/features_check.py
python3 scripts/resume.py | grep -q "Nothing in progress" || { echo "FAIL idle brief"; exit 1; }
ok python3 scripts/feature.py F001 status=in-progress phase=grill next="draft plan"
ok python3 scripts/resume.py --check                      # grill without a plan resumes
printf '# F001\n\n## Decisions\n- x\n' > docs/plans/F001.md
printf '<html></html>\n' > docs/design/mockups/F001-list.html
ok python3 scripts/feature.py F001 mockup=docs/design/mockups/F001-list.html
git checkout -qb feat/F001-x
ok python3 scripts/feature.py F001 phase=red tests+=tests/test_example.py::test_greet
python3 scripts/resume.py | grep -q "RED -> next GREEN" || { echo "FAIL brief phase"; exit 1; }
fails python3 scripts/feature.py F001 phase=bogus
python3 scripts/feature.py F001 | grep -q '"phase": "red"' || { echo "FAIL invalid update landed"; exit 1; }
ok python3 scripts/feature.py F001 notes+="deviation: kept sync I/O"
ok python3 scripts/feature.py F001 status=done
python3 scripts/feature.py F001 | grep -q '"phase"' && { echo "FAIL phase must drop on done"; exit 1; }
fails python3 scripts/features_check.py                  # leftover plan
python3 scripts/prune.py | grep -q "deleted docs/plans/F001.md" || { echo "FAIL prune"; exit 1; }
grep -q '\[x\] \*\*F001\*\*' docs/BACKLOG.md || { echo "FAIL backlog regen"; exit 1; }
ok python3 scripts/prune.py --check
ok python3 scripts/features_check.py
ok python3 scripts/resume.py --check
echo "loop-scripts: OK"
