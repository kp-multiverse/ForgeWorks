#!/usr/bin/env bash
# factory doctor -- list and prune stale worktrees and merged branches.
# Safe by default: prunes only worktrees whose directory is gone and merged
# branches; anything with uncommitted or unmerged work is LISTED, not touched.
set -euo pipefail

echo "== worktrees =="
git worktree prune
git worktree list
echo
echo "== merged branches (safe to delete) =="
git branch --merged main | grep -vE '^\*|  main$' || echo "  none"
echo
echo "== NOT merged (needs a human decision) =="
git branch --no-merged main | grep -v '^\*' || echo "  none"
echo
echo "Delete a merged branch with: git branch -d <name>"
echo "Remove a finished worktree with: git worktree remove <path>"
