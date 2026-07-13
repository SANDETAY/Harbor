#!/usr/bin/env bash
# Harbor — Mac setup for TestFlight (clone if needed, install, sync iOS, open Xcode)
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/SANDETAY/Harbor/main/scripts/mac-testflight-setup.sh | bash
# Or after clone:
#   bash scripts/mac-testflight-setup.sh

set -euo pipefail

REPO_URL="https://github.com/SANDETAY/Harbor.git"
REPO_DIR="${HOME}/Harbor"

echo ""
echo "=== Harbor Mac → TestFlight setup ==="
echo ""

# --- checks ---
need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing: $1"
    return 1
  fi
  return 0
}

if ! need git; then
  echo "Install Xcode Command Line Tools, then re-run:"
  echo "  xcode-select --install"
  exit 1
fi

if ! need node; then
  echo "Install Node.js from https://nodejs.org (LTS), then re-run this script."
  exit 1
fi

if ! need npm; then
  echo "npm missing (usually comes with Node). Reinstall Node LTS, then re-run."
  exit 1
fi

echo "git:  $(git --version)"
echo "node: $(node -v)"
echo "npm:  $(npm -v)"
echo ""

# --- clone or update ---
if [ -d "${REPO_DIR}/.git" ]; then
  echo "Found existing repo at ${REPO_DIR}"
  cd "${REPO_DIR}"
  git pull --ff-only origin main || git pull origin main
else
  if [ -e "${REPO_DIR}" ]; then
    echo "ERROR: ${REPO_DIR} exists but is not a git repo."
    echo "Move/rename it, then re-run."
    exit 1
  fi
  echo "Cloning Harbor into ${REPO_DIR} ..."
  git clone "${REPO_URL}" "${REPO_DIR}"
  cd "${REPO_DIR}"
fi

echo ""
echo "Repo: $(pwd)"
git remote -v | head -2
git log -1 --oneline
echo ""

# --- npm + capacitor ---
echo "npm install ..."
npm install

echo "cap:prepare ..."
npm run cap:prepare

echo "cap sync ios ..."
npx cap sync ios

# --- CocoaPods ---
if ! command -v pod >/dev/null 2>&1; then
  echo ""
  echo "CocoaPods not found. Install with one of:"
  echo "  brew install cocoapods"
  echo "  sudo gem install cocoapods"
  echo "Then run:"
  echo "  cd ~/Harbor/ios/App && pod install && cd ~/Harbor && npx cap open ios"
  exit 1
fi

echo "pod install ..."
cd ios/App
pod install
cd ../..

echo ""
echo "=== Setup complete ==="
echo "Next in Xcode:"
echo "  1. Signing & Capabilities → your Team · Bundle ID com.sandetay.harbor"
echo "  2. Destination: Any iOS Device (arm64)  [not Simulator]"
echo "  3. Product → Archive"
echo "  4. Distribute App → App Store Connect → Upload"
echo "  5. App Store Connect → TestFlight → Internal testing"
echo ""
echo "Opening Xcode workspace..."
npx cap open ios
