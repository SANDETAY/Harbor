# Deploy Google Calendar OAuth Edge Functions

**Google only.** Outlook Connect is not deployed.

## Prerequisites

1. SQL: `docs/supabase/schema-d-calendar-oauth.sql`  
2. Harbor Pro sandbox + signed in  
3. Google Web OAuth client redirect:

```text
https://dyaicsnoefkfshesyogk.supabase.co/functions/v1/calendar-oauth-callback
```

## Deploy

```bash
cd ~/Desktop/Harbor
npx supabase login   # if needed
npx supabase link --project-ref dyaicsnoefkfshesyogk
bash scripts/deploy-calendar-oauth.sh
```

## Secrets

```bash
npx supabase secrets set \
  GOOGLE_CLIENT_ID="....apps.googleusercontent.com" \
  GOOGLE_CLIENT_SECRET="..." \
  OAUTH_STATE_SECRET="$(openssl rand -hex 32)"
```

Do **not** set Microsoft calendar secrets.

## Verify

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  "https://dyaicsnoefkfshesyogk.supabase.co/functions/v1/calendar-oauth-start" \
  -H "Content-Type: application/json" -d '{}'
```

**401** = live · **404** = not deployed  

## Test

Harbor → Pro → Calendars → **Connect Google Calendar**.
