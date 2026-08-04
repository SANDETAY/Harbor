# 05 — Backend & cloud

Harbor runs **offline-first**. Cloud is for account, household, and calendar OAuth.

## Stack

| Piece | Role |
|-------|------|
| **Supabase** | Auth, database (Postgres), edge functions |
| **Google / Apple / email** | Account sign-in (Microsoft account login not used) |
| **config.local.js** | Project URL + anon key for the app (not in git) |

## Files you care about

| Path | Purpose |
|------|---------|
| `docs/supabase/schema.sql` | Core schema |
| `docs/supabase/schema-c1-*.sql` | Household / display name / life share |
| `docs/supabase/schema-d-calendar-oauth.sql` | Calendar OAuth tables |
| `docs/supabase/FIX-*.sql` | One-shot SQL fixes (run in SQL Editor) |
| `docs/supabase/functions/` | Edge functions (calendar OAuth) |
| `docs/supabase/config.local.js` | **Your** secrets (gitignored) |
| `docs/supabase/config.example.js` | Template (if present) |
| `js/harbor-cloud.js` | Client helper loaded by the app |

## First-time cloud setup

1. Create a project at [Supabase Dashboard](https://supabase.com/dashboard)  
2. Copy **Project URL** + **anon public key** into `docs/supabase/config.local.js`  
3. Run SQL schemas in order (schema → c1 → c1b → c1c → d) in **SQL Editor**  
4. Enable providers: see [../auth/AUTH-PROVIDERS.md](../auth/AUTH-PROVIDERS.md)  
5. Set **Site URL** + **Redirect URLs** (include `com.sandetay.harbor://auth/callback` for native)  
6. `bash scripts/cap-prepare.sh` so native shell gets the config  

## Your project (if still the sandbox)

Auth callback pattern:

`https://dyaicsnoefkfshesyogk.supabase.co/auth/v1/callback`

Confirm in Supabase → Project Settings → API if the ref changed.

## Troubleshooting cloud

| Symptom | Check |
|---------|--------|
| Email sign-in dead / grey | Missing `config.local.js` in native build |
| Google works web, fails TestFlight | Redirect URLs missing native schemes |
| Invite errors | Run `FIX-invite-gen-random-bytes.sql` |
| Household RPC errors | Run household FIX SQL + schemas |

Full provider guide: [../auth/AUTH-PROVIDERS.md](../auth/AUTH-PROVIDERS.md)  
Calendar OAuth: [../auth/CALENDAR-OAUTH.md](../auth/CALENDAR-OAUTH.md)  

## Bookmarks

Open [../bookmarks/open-bookmarks.html](../bookmarks/open-bookmarks.html) → section **Backend**.
