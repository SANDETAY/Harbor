#!/usr/bin/env bash
# Harbor — commit & push Mac splash so origin/main matches this machine.
# Run on Mac after you tune LaunchScreen / Splash.imageset:
#   cd ~/Desktop/Harbor && bash scripts/mac-push-splash.sh
#
# After this, git reset --hard origin/main will keep your splash.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# shellcheck source=mac-preserve-splash.sh
source "$ROOT/scripts/mac-preserve-splash.sh"

echo ""
echo "=== Push Mac splash → origin/main ==="
echo "Repo: $ROOT"
echo ""

git fetch origin

# Show what would be committed under splash paths
echo "Splash paths status:"
git status --short -- "${HARBOR_SPLASH_PATHS[@]}" || true
echo ""

# Stage only splash-related paths that exist
for p in "${HARBOR_SPLASH_PATHS[@]}"; do
  if [ -e "$p" ]; then
    git add -A -- "$p" 2>/dev/null || git add -- "$p" 2>/dev/null || true
  fi
done

if git diff --cached --quiet; then
  echo "No splash changes to commit — already matches the index."
  # Still show if working tree splash differs from origin
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    if git diff --quiet origin/main -- "${HARBOR_SPLASH_PATHS[@]}" 2>/dev/null; then
      echo "Splash already matches origin/main. You're good."
    else
      echo "Note: local splash may already be committed but not pushed, or origin is ahead."
      echo "  git log -1 --oneline"
      echo "  git push origin HEAD:main"
    fi
  fi
  exit 0
fi

git commit -m "$(cat <<'EOF'
Preserve Mac-tuned iOS splash / launch screen

Keeps LaunchScreen + Splash.imageset (and related brand assets) as tuned
on the Mac so TestFlight upload scripts do not regress the splash.
EOF
)"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "Pushing $BRANCH → origin ..."
git push -u origin "$BRANCH"

echo ""
echo "=== Done ==="
echo "origin now has this Mac splash. Safe update pattern:"
echo "  bash scripts/mac-update-for-upload.sh"
echo ""
