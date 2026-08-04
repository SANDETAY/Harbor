#!/usr/bin/env bash
# Upload Harbor.ipa to App Store Connect without Xcode's broken "Fetch App Record" step.
# Uses an App Store Connect API key (not an app-specific password).
#
# Setup (once):
# 1) Open https://appstoreconnect.apple.com/access/integrations/api
# 2) Generate API Key → Admin or App Manager → Download AuthKey_XXXXXX.p8
# 3) Put the .p8 in ~/private_keys/  (or edit KEY_PATH below)
# 4) Fill in ISSUER_ID and KEY_ID below
# 5) Run:  bash ~/Desktop/upload-harbor-ipa.sh

set -euo pipefail

IPA="${IPA:-$HOME/Desktop/Harbor-393.ipa}"
# --- fill these in after generating the key ---
ISSUER_ID="${APP_STORE_CONNECT_ISSUER_ID:-}"   # UUID at top of API Keys page
KEY_ID="${APP_STORE_CONNECT_KEY_ID:-}"         # e.g. AB12CD34EF
KEY_PATH="${APP_STORE_CONNECT_KEY_PATH:-}"     # e.g. $HOME/private_keys/AuthKey_AB12CD34EF.p8

if [[ -z "$ISSUER_ID" || -z "$KEY_ID" ]]; then
  echo "Missing ISSUER_ID / KEY_ID."
  echo "Edit this script or export:"
  echo "  export APP_STORE_CONNECT_ISSUER_ID='xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'"
  echo "  export APP_STORE_CONNECT_KEY_ID='XXXXXXXXXX'"
  echo "  export APP_STORE_CONNECT_KEY_PATH=\"\$HOME/private_keys/AuthKey_XXXXXXXXXX.p8\""
  echo ""
  echo "Create key: https://appstoreconnect.apple.com/access/integrations/api"
  exit 1
fi

if [[ -z "$KEY_PATH" ]]; then
  # Common locations
  for c in \
    "$HOME/private_keys/AuthKey_${KEY_ID}.p8" \
    "$HOME/.appstoreconnect/private_keys/AuthKey_${KEY_ID}.p8" \
    "$HOME/Downloads/AuthKey_${KEY_ID}.p8" \
    "$HOME/Desktop/AuthKey_${KEY_ID}.p8"
  do
    [[ -f "$c" ]] && KEY_PATH="$c" && break
  done
fi

if [[ ! -f "$IPA" ]]; then
  echo "IPA not found: $IPA"
  exit 1
fi
if [[ ! -f "$KEY_PATH" ]]; then
  echo "API key .p8 not found. Set APP_STORE_CONNECT_KEY_PATH."
  exit 1
fi

# altool looks for keys in ~/.appstoreconnect/private_keys by default
mkdir -p "$HOME/.appstoreconnect/private_keys"
cp -f "$KEY_PATH" "$HOME/.appstoreconnect/private_keys/AuthKey_${KEY_ID}.p8"

echo "Uploading: $IPA"
echo "Key ID:    $KEY_ID"
echo "Issuer:    $ISSUER_ID"
echo ""

xcrun altool --upload-app \
  --type ios \
  --file "$IPA" \
  --apiKey "$KEY_ID" \
  --apiIssuer "$ISSUER_ID" \
  --verbose

echo ""
echo "Upload finished. Check App Store Connect → TestFlight in a few minutes."
