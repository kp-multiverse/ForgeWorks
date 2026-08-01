#!/usr/bin/env bash
# factory doctor -- list and prune stale worktrees and merged branches.
# Set FACTORY_BASE to the base branch name (default: main).
# Safe by default: prunes only worktrees whose directory is gone and merged
# branches; anything with uncommitted or unmerged work is LISTED, not touched.
set -euo pipefail

BASE="${FACTORY_BASE:-main}"
git rev-parse --verify --quiet "$BASE" >/dev/null || { echo "factory-doctor: base branch '$BASE' not found (set FACTORY_BASE)"; exit 1; }

echo "== worktrees =="
git worktree prune
git worktree list
echo
echo "== merged branches (safe to delete) =="
git branch --merged "$BASE" | grep -vE '^\*|  '"$BASE"'$' || echo "  none"
echo
echo "== NOT merged (needs a human decision) =="
git branch --no-merged "$BASE" | grep -v '^\*' || echo "  none"
echo
echo "Delete a merged branch with: git branch -d <name>"
echo "Remove a finished worktree with: git worktree remove <path>"
