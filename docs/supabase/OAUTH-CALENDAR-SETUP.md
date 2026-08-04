# Phase D — Google Calendar OAuth (Harbor walkthrough)

**Status:** Not live in the app yet. This is the setup + build path.  
**Scope (v1):** **Read-only** Google Calendar → Schedule. Outlook later.  
**Budget / household data:** never involved.

---

## 0. Two different “OAuth”s (don’t mix them up)

| What | Purpose | Harbor today |
|------|---------|--------------|
| **Supabase Auth → Google** | “Sign in with Google” for your Harbor account | Optional later; not required for calendars |
| **Google Calendar API OAuth** | “Let Harbor read my calendars” | **This doc** — needs Cloud Console + Edge Functions |

You already sign in with **email/password**. Calendar OAuth is a **second** consent that only grants calendar read.

---

## 1. Architecture (security-first)

```
Harbor app (publishable key only)
    │
    ├─ POST /functions/v1/calendar-google-start   → redirect URL to Google
    │
    └─ GET  /functions/v1/calendar-google-callback ← Google returns ?code=
              │
              ├─ exchange code → refresh_token (server only)
              ├─ store in calendar_connections (RLS: user owns row)
              └─ redirect browser back to Harbor ?calendar=connected

Harbor app
    └─ POST /functions/v1/calendar-google-events
              │  uses stored refresh_token + client_secret
              └─ returns events JSON → merge into Schedule (local)
```

**Never put in the app or git:**
- Google **Client secret**
- Supabase **service_role** key  
- Refresh tokens (DB only, server-side)

**OK in the app:**
- Supabase project URL  
- Publishable (anon) key  
- Google **Client ID** is semi-public; still better only on the Edge Function for this flow

---

## 2. What you do first (Google Cloud Console) — ~15 min

### 2.1 Create / open a project
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (e.g. `Harbor Calendar`) or pick an existing one  
3. Note the project name

### 2.2 Enable the Calendar API
1. **APIs & Services → Library**
2. Search **Google Calendar API** → **Enable**

### 2.3 OAuth consent screen
1. **APIs & Services → OAuth consent screen**
2. User type: **External** (unless you only use Workspace internal)
3. App name: `Harbor`  
4. User support email: yours  
5. Developer contact: yours  
6. **Scopes → Add or remove:**
   - `.../auth/calendar.readonly`  
     (Google Calendar API → see all calendars, read-only)
7. **Test users** (while status is **Testing**):
   - Add **every Gmail** you’ll use to connect (including yours)
8. Save

> While the app is in **Testing**, only listed test users can connect.  
> “Production” verification is only needed if you ship to many outside users.

### 2.4 Create OAuth client
1. **APIs & Services → Credentials → Create credentials → OAuth client ID**
2. Application type: **Web application**
3. Name: `Harbor Calendar Web`
4. **Authorized redirect URIs** — add **exactly** (replace `PROJECT_REF`):

```
https://PROJECT_REF.supabase.co/functions/v1/calendar-google-callback
```

Find `PROJECT_REF` in Supabase → **Project Settings → General → Reference ID**  
(Example: `abcdefghijklmnop` → `https://abcdefghijklmnop.supabase.co/functions/v1/calendar-google-callback`)

5. Create → copy:
   - **Client ID**
   - **Client secret**  
   Keep the secret in a password manager; you will paste it only into Supabase secrets.

### 2.5 Optional local redirect (later)
You do **not** need localhost redirect if the callback always hits Supabase Edge Functions (recommended). Harbor opens Google, Google returns to Supabase, Supabase redirects to your Harbor URL.

---

## 3. What you do in Supabase

### 3.1 Run the SQL (after C1)
File: `docs/supabase/schema-d-calendar-oauth.sql`  
**SQL Editor → New query → paste all → Run**

Creates `calendar_connections` (per-user tokens; RLS = own rows only).

### 3.2 Deploy Edge Functions
From a machine with [Supabase CLI](https://supabase.com/docs/guides/cli) logged in:

```bash
cd ~/Desktop/Harbor
supabase login
supabase link --project-ref PROJECT_REF
supabase secrets set \
  GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com" \
  GOOGLE_CLIENT_SECRET="your-client-secret" \
  HARBOR_OAUTH_RETURN_URL="http://127.0.0.1:3000/" \
  HARBOR_OAUTH_RETURN_URL_PROD="https://YOUR-PRODUCTION-HOST/"

supabase functions deploy calendar-google-start
supabase functions deploy calendar-google-callback
supabase functions deploy calendar-google-events
supabase functions deploy calendar-google-disconnect
```

Set return URLs to wherever you open Harbor (local server or production).

### 3.3 JWT
Edge Functions should verify the user’s Supabase JWT (the app sends `Authorization: Bearer <access_token>`).  
Never accept a “user id” alone without a valid session.

---

## 4. What the app will do (implementation checklist)

| Step | Piece |
|------|--------|
| 1 | Pro gate: “Connect Google Calendar” |
| 2 | Call `calendar-google-start` → open returned Google URL |
| 3 | After redirect back, toast “Calendar connected” |
| 4 | Call `calendar-google-events` on open / pull-to-refresh Schedule |
| 5 | Map events into existing Schedule stores (same shape as device/ICS import) |
| 6 | Disconnect clears server row + local cache |

**Not in v1:** write events back to Google, multi-account Google, Outlook, free-tier OAuth.

---

## 5. Your checklist (do in order)

- [ ] Google Cloud project created  
- [ ] Calendar API enabled  
- [ ] OAuth consent screen + `calendar.readonly` + **you as test user**  
- [ ] Web OAuth client + redirect URI = Supabase function URL  
- [ ] Client ID + secret saved offline  
- [ ] Tell the agent: “Google client is ready” + paste **Client ID only** (not secret) + your Supabase project ref + Harbor return URL  
- [ ] Agent: SQL + Edge Functions + Harbor UI wiring  
- [ ] You: set secrets + deploy functions  
- [ ] Test with Pro sandbox ON  

---

## 6. Common failures

| Symptom | Fix |
|---------|-----|
| `redirect_uri_mismatch` | Redirect URI in Google Console must match Edge Function URL **exactly** (https, path, no trailing slash mismatch) |
| `access_denied` / app not verified | Add your Gmail under **Test users** |
| `invalid_client` | Wrong client id/secret in Supabase secrets |
| Connect works, no events | Wrong Google account, empty calendar, or API not enabled |
| Function 401 | Not signed into Harbor cloud (email account) when connecting |

---

## 7. Privacy copy (product)

- Harbor requests **read-only** calendar access.  
- Tokens live on **your** Supabase project, not in the browser.  
- Disconnect removes the connection.  
- Budget and other Harbor data are **not** shared with Google.

---

## 8. Outlook (later)

Same pattern with **Microsoft Azure app registration** + Microsoft Graph `Calendars.Read`, separate Edge Functions. Do Google end-to-end first.

---

*Related: [CALENDAR-V1.md](../CALENDAR-V1.md) · [PRO-IMPLEMENTATION.md](../PRO-IMPLEMENTATION.md) · [GETTING-STARTED.md](./GETTING-STARTED.md)*
