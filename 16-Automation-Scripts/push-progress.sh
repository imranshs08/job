#!/usr/bin/env bash
# ============================================================
# push-progress.sh — Daily DevOps 2027 Progress Commit & Push
# Usage:  bash push-progress.sh [optional commit message]
# ============================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DATE_TAG=$(date +"%Y-%m-%d %H:%M %Z")
MSG="${1:-"progress: daily update ${DATE_TAG}"}"

echo "📂 Repo: $REPO_ROOT"
echo "📝 Commit: $MSG"
echo ""

# 1. Stage everything changed
git add -A
echo "✅ Staged all changes"

# 2. Commit (skip if nothing to commit)
if git diff --cached --quiet; then
  echo "ℹ️  Nothing new to commit — skipping commit step"
else
  git commit -m "$MSG"
  echo "✅ Committed"
fi

# 3. Pull with rebase (handles the scheduled bot commits on origin/main)
echo "🔄 Rebasing on top of origin/main..."
git pull --rebase origin main
echo "✅ Rebase done"

# 4. Push
git push origin main
echo ""
echo "🚀 Pushed! GitHub Pages will update in ~30–60 seconds."
echo "🌐 https://imranshs08.github.io/job/"
