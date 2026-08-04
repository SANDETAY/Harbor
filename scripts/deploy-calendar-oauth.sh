#!/usr/bin/env bash
# Deploy Harbor calendar OAuth Edge Functions to Supabase.
# Prereq: npx supabase login && npx supabase link --project-ref dyaicsnoefkfshesyogk
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! npx supabase --version >/dev/null 2>&1; then
  echo "Installing supabase CLI (devDependency)…"
  npm install supabase --save-dev
fi

echo "Deploying calendar-oauth-start, callback, disconnect…"
npx supabase functions deploy calendar-oauth-start
npx supabase functions deploy calendar-oauth-callback
npx supabase functions deploy calendar-oauth-disconnect

echo ""
echo "Deploy done. Set secrets if you have not yet:"
echo "  npx supabase secrets set GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... OAUTH_STATE_SECRET=\$(openssl rand -hex 32)"
echo ""
echo "Verify (expect 401 when live, 404 when missing):"
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST \
  "https://dyaicsnoefkfshesyogk.supabase.co/functions/v1/calendar-oauth-start" \
  -H "Content-Type: application/json" -d '{}'
