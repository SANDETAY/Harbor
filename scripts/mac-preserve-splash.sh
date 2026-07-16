#!/usr/bin/env bash
# Harbor — splash protect helpers for Mac scripts
# Source this file:  source scripts/mac-preserve-splash.sh
#
# Native launch art lives in git. Hard resets / cap sync must not silently
# replace a Mac-tuned splash. Use backup_splash / restore_splash around resets.
# (Do not set -e here — this file is sourced by other scripts.)

# Paths relative to repo root. Keep in sync with docs/APP-STORE-IOS.md
HARBOR_SPLASH_PATHS=(
  "ios/App/App/Assets.xcassets/Splash.imageset"
  "ios/App/App/Base.lproj/LaunchScreen.storyboard"
  "harbor-ios-launch-solid.png"
  "harbor-ios-launch-splash.png"
  "harbor-splash-anchor.png"
  "harbor-splash-anchor-512.png"
  "capacitor.config.json"
  # HTML + generator — first-frame handoff (mark/word/slogan animate after native)
  "index.html"
  "scripts/gen-ios-splash.py"
  "sw.js"
  "ios/App/App.xcodeproj/project.pbxproj"
)

harbor_splash_backup_dir() {
  echo "${HARBOR_SPLASH_BACKUP_DIR:-}"
}

backup_splash() {
  local root="${1:-.}"
  local bak
  bak="$(mktemp -d "${TMPDIR:-/tmp}/harbor-splash.XXXXXX")"
  export HARBOR_SPLASH_BACKUP_DIR="$bak"
  mkdir -p "$bak"
  local p
  for p in "${HARBOR_SPLASH_PATHS[@]}"; do
    if [ -e "$root/$p" ]; then
      mkdir -p "$bak/$(dirname "$p")"
      cp -R "$root/$p" "$bak/$p"
    fi
  done
  echo "Splash backed up → $bak"
}

restore_splash() {
  local root="${1:-.}"
  local bak="${HARBOR_SPLASH_BACKUP_DIR:-}"
  if [ -z "$bak" ] || [ ! -d "$bak" ]; then
    echo "No splash backup to restore (ok if first clone)."
    return 0
  fi
  local p
  for p in "${HARBOR_SPLASH_PATHS[@]}"; do
    if [ -e "$bak/$p" ]; then
      mkdir -p "$root/$(dirname "$p")"
      rm -rf "$root/$p"
      cp -R "$bak/$p" "$root/$p"
    fi
  done
  echo "Splash restored from backup (not overwritten by pull/reset)."
}

cleanup_splash_backup() {
  local bak="${HARBOR_SPLASH_BACKUP_DIR:-}"
  if [ -n "$bak" ] && [ -d "$bak" ]; then
    rm -rf "$bak"
  fi
  unset HARBOR_SPLASH_BACKUP_DIR || true
}
