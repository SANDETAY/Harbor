#!/usr/bin/env bash
# Harbor — Mac: pull latest web app for TestFlight WITHOUT clobbering splash.
#
# Usage (preferred path on this machine):
#   cd ~/Desktop/Harbor
#   bash scripts/mac-update-for-upload.sh
#
# What it does:
#   1) Backs up splash / launch assets
#   2) git fetch + reset --hard origin/main  (web + code only effectively)
#   3) Restores splash backup so Mac-tuned launch art stays put
#   4) npm install, cap:prepare, cap sync ios, pod install
#   5) Opens Xcode
#
# First time: push your splash so main matches Mac:
#   bash scripts/mac-push-splash.sh

set -euo pipefail

# Prefer Desktop copy (this machine); fall back to ~/Harbor
if [ -d "${HOME}/Desktop/Harbor/.git" ]; then
  REPO_DIR="${HOME}/Desktop/Harbor"
elif [ -d "${HOME}/Harbor/.git" ]; then
  REPO_DIR="${HOME}/Harbor"
else
  REPO_DIR="${HOME}/Desktop/Harbor"
fi

# Allow override: HARBOR_DIR=/path/to/Harbor bash scripts/mac-update-for-upload.sh
REPO_DIR="${HARBOR_DIR:-$REPO_DIR}"

echo ""
echo "=== Harbor Mac update (splash-safe) ==="
echo ""

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing: $1"
    exit 1
  }
}

need git
need node
need npm

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "No git repo at $REPO_DIR"
  echo "Clone first, or set HARBOR_DIR:"
  echo "  git clone https://github.com/SANDETAY/Harbor.git ~/Desktop/Harbor"
  exit 1
fi

cd "$REPO_DIR"
# shellcheck source=mac-preserve-splash.sh
source "$REPO_DIR/scripts/mac-preserve-splash.sh" 2>/dev/null || {
  # If script not on disk yet (mid-pull), define minimal backup inline
  HARBOR_SPLASH_PATHS=(
    "ios/App/App/Assets.xcassets/Splash.imageset"
    "ios/App/App/Base.lproj/LaunchScreen.storyboard"
    "harbor-ios-launch-solid.png"
    "harbor-ios-launch-splash.png"
    "harbor-splash-anchor.png"
    "harbor-splash-anchor-512.png"
    "capacitor.config.json"
  )
  backup_splash() {
    local root="${1:-.}"
    HARBOR_SPLASH_BACKUP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/harbor-splash.XXXXXX")"
    export HARBOR_SPLASH_BACKUP_DIR
    local p
    for p in "${HARBOR_SPLASH_PATHS[@]}"; do
      if [ -e "$root/$p" ]; then
        mkdir -p "$HARBOR_SPLASH_BACKUP_DIR/$(dirname "$p")"
        cp -R "$root/$p" "$HARBOR_SPLASH_BACKUP_DIR/$p"
      fi
    done
    echo "Splash backed up → $HARBOR_SPLASH_BACKUP_DIR"
  }
  restore_splash() {
    local root="${1:-.}"
    local bak="${HARBOR_SPLASH_BACKUP_DIR:-}"
    [ -n "$bak" ] && [ -d "$bak" ] || return 0
    local p
    for p in "${HARBOR_SPLASH_PATHS[@]}"; do
      if [ -e "$bak/$p" ]; then
        mkdir -p "$root/$(dirname "$p")"
        rm -rf "$root/$p"
        cp -R "$bak/$p" "$root/$p"
      fi
    done
    echo "Splash restored from backup."
  }
  cleanup_splash_backup() {
    [ -n "${HARBOR_SPLASH_BACKUP_DIR:-}" ] && rm -rf "$HARBOR_SPLASH_BACKUP_DIR" || true
    unset HARBOR_SPLASH_BACKUP_DIR || true
  }
}

echo "Repo: $REPO_DIR"
git remote -v | head -2
echo ""

# 1) Protect splash before hard reset
backup_splash "$REPO_DIR"

# 2) Match origin/main for everything else
echo "git fetch + reset --hard origin/main ..."
git fetch origin
git reset --hard origin/main
git clean -fd --exclude=node_modules --exclude=ios/App/Pods --exclude=ios/App/App/public || true

# Re-source helpers if they just arrived from origin
if [ -f "$REPO_DIR/scripts/mac-preserve-splash.sh" ]; then
  # shellcheck source=mac-preserve-splash.sh
  source "$REPO_DIR/scripts/mac-preserve-splash.sh"
fi

# 3) Put Mac splash back (so this machine’s launch art always wins)
restore_splash "$REPO_DIR"

# 4) Native web assets + pods
echo "npm install ..."
npm install

echo "cap:prepare ..."
# cap:prepare is PowerShell on Windows; on Mac use a small portable copy
if [ -f "$REPO_DIR/scripts/cap-prepare.sh" ]; then
  bash "$REPO_DIR/scripts/cap-prepare.sh"
elif command -v pwsh >/dev/null 2>&1; then
  pwsh -File "$REPO_DIR/scripts/cap-prepare.ps1"
else
  # Portable prepare (no PowerShell required)
  OUT="$REPO_DIR/native-www"
  rm -rf "$OUT"
  mkdir -p "$OUT"
  for f in index.html sw.js manifest.webmanifest privacy.html \
    harbor-favicon-32.png harbor-apple-touch.png harbor-icon-192.png harbor-icon-512.png \
    harbor-mark.png harbor-mark.svg harbor-splash-anchor.png harbor-splash-anchor-512.png \
    harbor-fab-anchor.png harbor-fab-anchor-128.png; do
    [ -f "$REPO_DIR/$f" ] && cp "$REPO_DIR/$f" "$OUT/$f"
  done
  echo "Prepared native-www (portable)"
fi

# Restore splash again after prepare (in case assets were recopied)
restore_splash "$REPO_DIR"

echo "npx cap sync ios ..."
npx cap sync ios

# cap sync must not leave a different splash in Assets — restore once more
restore_splash "$REPO_DIR"

if command -v pod >/dev/null 2>&1; then
  echo "pod install ..."
  (cd "$REPO_DIR/ios/App" && pod install)
else
  echo "CocoaPods not found — install with: brew install cocoapods"
fi

cleanup_splash_backup

echo ""
echo "=== Ready for Xcode ==="
echo "Splash was preserved through pull/sync."
echo "  Destination: Any iOS Device (arm64)"
echo "  Product → Archive → Distribute → App Store Connect"
echo ""

if command -v npx >/dev/null 2>&1; then
  npx cap open ios || true
fi
