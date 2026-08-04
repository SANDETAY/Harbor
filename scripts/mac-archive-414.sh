#!/usr/bin/env bash
# Archive Harbor for TestFlight (build 414)
set -euo pipefail
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ARCHIVE_PATH="$ROOT/build/Harbor-414.xcarchive"
mkdir -p "$ROOT/build"
LOG=/tmp/harbor-archive.log

echo "Archiving → $ARCHIVE_PATH"
xcodebuild -workspace ios/App/App.xcworkspace \
  -scheme App \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -archivePath "$ARCHIVE_PATH" \
  clean archive \
  CODE_SIGN_STYLE=Automatic \
  2>&1 | tee "$LOG"

echo "Archive log: $LOG"
ls -la "$ARCHIVE_PATH"
echo "ARCHIVE_OK"
