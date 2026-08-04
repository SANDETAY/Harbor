# Harbor — Google Calendar OAuth (Phase B)

**Status:** Client UI + Edge Functions for **Google Calendar** only.  
**Outlook / Microsoft calendar Connect is not offered** — use phone calendars or `.ics` import.

**Related:** [CALENDAR-V1.md](./CALENDAR-V1.md) · [DEPLOY-CALENDAR-OAUTH.md](./DEPLOY-CALENDAR-OAUTH.md) · [schema-d-calendar-oauth.sql](../supabase/schema-d-calendar-oauth.sql)

---

## Product rules

| Path | Free / Pro |
|------|------------|
| Manual events, .ics **file**, phone calendars (EventKit) | **Free** |
| ICS URL (direct / optional helper) | Free (limits optional) |
| **Google Calendar OAuth** | **Harbor Pro** |

Tokens never live in the browser long-term. Refresh tokens stay in Supabase (`calendar_connections`), written only by Edge Functions (service role).

---

## Prerequisites

1. Supabase project with schema + `schema-d-calendar-oauth.sql`  
2. App signed-in via Harbor Account  
3. Harbor Pro (sandbox or real entitlement)  
4. Edge Functions deployed + Google secrets (see [DEPLOY-CALENDAR-OAUTH.md](./DEPLOY-CALENDAR-OAUTH.md))

---

## Google Cloud setup

1. Enable **Google Calendar API**.  
2. OAuth consent screen (External + Testing for dev; add test users).  
3. **Web application** OAuth client.  
4. Authorized redirect URIs:

```text
https://<PROJECT_REF>.supabase.co/auth/v1/callback
https://<PROJECT_REF>.supabase.co/functions/v1/calendar-oauth-callback
```

(Login + calendar Connect.)

5. Secrets on Supabase: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OAUTH_STATE_SECRET`.

Scopes: `openid email https://www.googleapis.com/auth/calendar.readonly`

---

## Edge Functions

| Function | Role |
|----------|------|
| `calendar-oauth-start` | Returns Google authorize URL |
| `calendar-oauth-callback` | Exchanges code → stores refresh_token |
| `calendar-oauth-disconnect` | Deletes Google connection row |

---

## App flow

1. **Life → Schedule → Calendars**  
2. **Connect Google Calendar** (Pro + signed in)  
3. Browser consent → return to Harbor → connected email shown  

Outlook is not in the UI. Users with Outlook can add it on the iPhone or import `.ics`.
