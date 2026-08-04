#!/usr/bin/env bash
# Portable cap:prepare for Mac/Linux (mirrors scripts/cap-prepare.ps1)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/native-www"
rm -rf "$OUT"
mkdir -p "$OUT"
files=(
  index.html sw.js manifest.webmanifest privacy.html
  harbor-favicon-32.png harbor-apple-touch.png
  harbor-icon-192.png harbor-icon-512.png
  harbor-mark.png harbor-mark.svg
  harbor-splash-anchor.png harbor-splash-anchor-512.png
  harbor-fab-anchor.png harbor-fab-anchor-128.png
)
for f in "${files[@]}"; do
  if [ -f "$ROOT/$f" ]; then
    cp "$ROOT/$f" "$OUT/$f"
  else
    echo "warn: missing optional asset: $f" >&2
  fi
done
# JS assets (cloud client + offline PDF reader for recipe import)
mkdir -p "$OUT/js"
if [ -f "$ROOT/js/harbor-cloud.js" ]; then
  cp "$ROOT/js/harbor-cloud.js" "$OUT/js/harbor-cloud.js"
fi
if [ -d "$ROOT/js/pdfjs" ]; then
  mkdir -p "$OUT/js/pdfjs"
  cp -R "$ROOT/js/pdfjs/." "$OUT/js/pdfjs/"
  echo "Included js/pdfjs (recipe PDF reader)."
fi
# Optional Supabase config (gitignored). Copy if present so TestFlight cloud/auth works.
if [ -f "$ROOT/docs/supabase/config.local.js" ]; then
  mkdir -p "$OUT/docs/supabase"
  cp "$ROOT/docs/supabase/config.local.js" "$OUT/docs/supabase/config.local.js"
  echo "Included docs/supabase/config.local.js in native-www."
else
  echo "warn: docs/supabase/config.local.js missing — cloud sign-in will stay unconfigured in native shell." >&2
fi
if [ ! -f "$OUT/index.html" ]; then
  echo "ERROR: index.html missing — cannot prepare native-www" >&2
  exit 1
fi
echo "Prepared $OUT for Capacitor (webDir)."
