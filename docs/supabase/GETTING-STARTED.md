# Harbor + Supabase — beginner setup guide

**Audience:** First time using Supabase / cloud backends  
**Goal:** Create a safe Harbor cloud project, run our schema, enable auth, and know what keys to share next  
**Does not yet:** Connect the app (that’s the next coding step after this checklist)

Take this slowly. Nothing here requires a credit card for the free tier. You can delete the whole project later if you want a clean start.

---

## 0. What you’re building (big picture)

```
┌─────────────────────────────┐
│  Harbor app (phone / web)   │
│  • Data lives on the device │
│  • Free features work offline│
└──────────────┬──────────────┘
               │  only when user opts into Pro cloud
               │  (sign in + backup / sync)
               ▼
┌─────────────────────────────┐
│  Supabase                   │
│  • Auth = “who is this user?”│
│  • Database = stored backups │
│  • RLS = “only you see yours”│
└─────────────────────────────┘
```

| Concept | Plain English |
|---------|----------------|
| **Supabase** | Hosted Postgres database + login system + APIs |
| **Project** | One isolated cloud sandbox for Harbor (like one app’s backend) |
| **Auth** | Users sign in (email, later Apple/Google) |
| **Table** | Spreadsheet-like storage (`profiles`, `harbor_snapshots`, …) |
| **RLS (Row Level Security)** | Rules so User A cannot read User B’s rows |
| **anon key** | Public client key — safe in the app *with* RLS |
| **service_role key** | God mode — **never** put in the app or GitHub |

Harbor stays **local-first**. Supabase is for Pro: account, backup, sync, later share.

---

## 1. Create a Supabase account & project

### 1.1 Sign up
1. Open [https://supabase.com](https://supabase.com)  
2. **Start your project** / Sign in (GitHub login is fine)  
3. Accept the free tier unless you already have a paid plan  

### 1.2 Create a new project (recommended: dedicated to Harbor only)
1. Click **New project**  
2. **Organization:** your personal org (default is fine)  
3. Fill in:

| Field | Suggestion |
|-------|------------|
| **Name** | `harbor` or `harbor-prod` |
| **Database password** | Generate a **strong** password and **save it in a password manager**. You need it for rare direct DB access — not for daily app use. |
| **Region** | Closest to you (e.g. US East if you’re in the US) |
| **Pricing** | Free |

4. Click **Create new project**  
5. Wait 1–2 minutes until status is **Healthy** / ready  

**Why a dedicated project?**  
If you experiment or mess up, you can delete *this* project without affecting other apps.

### 1.3 Bookmark these places in the dashboard
Left sidebar (names may vary slightly):

| Menu | You’ll use it for |
|------|-------------------|
| **Table Editor** | See tables and rows visually |
| **SQL Editor** | Run `schema.sql` |
| **Authentication** | Email / Apple / Google login |
| **Project Settings → API** | URL + anon key |

---

## 2. Understand the warning before you run SQL

When you paste our schema, Supabase may say:

> This query includes destructive operations…

### Is that normal?
**Yes.** The editor is cautious. Our script only:

| Statement | Meaning | Danger on a **brand-new** Harbor project |
|-----------|---------|------------------------------------------|
| `CREATE TABLE IF NOT EXISTS` | Make table if missing | None |
| `CREATE OR REPLACE FUNCTION` | Create/update a small helper | Low — only that function |
| `DROP TRIGGER IF EXISTS …` | Remove *our* trigger if re-running | Low — only that named trigger |
| `ON DELETE CASCADE` | If a user is deleted, remove *their* profile/snapshot | Intended; no mass delete of other data |
| RLS policies | Restrict who can read/write | Safety feature |

### When you should **not** run it blindly
- This project already has production data you care about under the same table names  
- You’re on a shared project used by something else  

**On a new empty Harbor project → safe to run.**

### What the schema creates

| Object | Purpose |
|--------|---------|
| `profiles` | One row per user (email, Pro flag later) |
| `harbor_snapshots` | Cloud backup of Harbor state (JSON) |
| `households` / `household_members` | Future sharing (empty until we build share) |
| Trigger `on_auth_user_created` | When someone signs up → create their `profiles` row |
| RLS policies | Each user only sees their own data |

Full file path on your Mac:

```text
/Users/brittany/Desktop/Harbor/docs/supabase/schema.sql
```

Or: `~/Harbor/docs/supabase/schema.sql`

---

## 3. Run the schema (step by step)

### 3.1 Open the SQL file on your computer
1. Finder → Desktop → **Harbor** → **docs** → **supabase** → **schema.sql**  
2. Open it in TextEdit / VS Code / any editor  
3. Select all → **Copy**

### 3.2 Open SQL Editor in Supabase
1. Supabase dashboard → your **harbor** project  
2. Left sidebar → **SQL Editor**  
3. **New query**  

### 3.3 Paste and run
1. Paste the full contents of `schema.sql`  
2. Read the warning if shown  
3. Click **Run** (or Cmd/Ctrl + Enter)  

### 3.4 Success looks like
- Green success / “Success. No rows returned” (normal for DDL)  
- **No red error** about permissions or syntax  

### 3.5 If something errors
| Error | What to do |
|-------|------------|
| Already exists | Often fine if you re-ran the script; tables use `IF NOT EXISTS` |
| Permission denied | Confirm you’re on the correct project as owner |
| Function/trigger name conflict | You’re not on a clean project — create a new project and re-run |

You can re-run the whole script on an empty project; `DROP TRIGGER IF EXISTS` is there so re-runs don’t fail on the trigger.

---

## 4. Verify the tables (don’t skip this)

### 4.1 Table Editor
1. Left sidebar → **Table Editor**  
2. Under **public** schema you should see:

- `profiles`  
- `harbor_snapshots`  
- `households`  
- `household_members`  

3. Click each — they should be **empty** (0 rows). That’s correct before any user signs up.

### 4.2 Check RLS is on (important)
1. Table Editor → select `profiles`  
2. Look for **RLS enabled** (or Database → Tables → policies)  
3. Same for `harbor_snapshots`  

If RLS were off, the anon key could be more dangerous. Our script turns it **on**.

### 4.3 Optional: list policies in SQL
New query:

```sql
select tablename, policyname
from pg_policies
where schemaname = 'public'
order by tablename, policyname;
```

You should see policies like `profiles_select_own`, `snapshots_select_own`, etc.

---

## 5. Turn on Authentication (Email first)

### 5.1 Enable Email provider
1. **Authentication** → **Providers**  
2. **Email** → enable  
3. For early testing, these settings are beginner-friendly:

| Setting | Beginner choice | Why |
|---------|-----------------|-----|
| **Confirm email** | Can disable temporarily on free/dev | Easier local testing; re-enable before real users |
| **Secure email change** | Leave default | Safer |

You can use **Confirm email = ON** if you prefer real confirmation emails from the start (check spam).

### 5.2 Don’t enable Apple/Google yet
Those need Apple Developer / Google Cloud console setup. We add them when we wire store login. **Email alone is enough for first backup tests.**

### 5.3 Auth URL config (later, when app connects)
**Authentication → URL configuration**

| Field | Eventually |
|-------|------------|
| Site URL | Your live site or app deep link |
| Redirect URLs | Localhost + production URLs |

For now, defaults are OK until we wire the client.

---

## 6. Get your API keys (what you’ll give me next)

### 6.1 Open API settings
1. Gear icon → **Project Settings**  
2. **API** (under Configuration)

### 6.2 Copy two values only

| Name in dashboard | What it is | Safe in app? |
|-------------------|------------|--------------|
| **Project URL** | e.g. `https://abcdefgh.supabase.co` | Yes |
| **anon public** key | Long JWT starting with `eyJ...` | Yes *with RLS* |
| **service_role** key | Another long JWT | **NO — never share in chat if avoidable; never commit to Git** |

### 6.3 How to store them on your Mac (good habit)

1. Copy `docs/supabase/config.example.js`  
2. Create a new file (same folder):

```text
docs/supabase/config.local.js
```

3. Paste and fill:

```js
window.HARBOR_SUPABASE = {
  url: 'https://YOUR_PROJECT_REF.supabase.co',
  anonKey: 'eyJ...your_anon_key...',
  debug: true
};
```

4. **Do not** commit `config.local.js` to GitHub (we’ll add it to `.gitignore` when wiring).  
5. When ready for me to wire the app, either:
   - Tell me the **URL + anon key** in chat, or  
   - Say “config.local.js is filled — wire the client” (if I can read that file on your machine)

### 6.4 What I will never need
- Your database password (unless we do advanced server work)  
- service_role key in the mobile/web app  

---

## 7. Mental model: what happens when a user uses Pro cloud

```
1. User taps “Sign in” (email magic link or password)
2. Supabase Auth verifies them → returns a session (JWT)
3. App loads their user id (auth.uid())
4. Trigger already created a profiles row
5. Backup: app uploads JSON → harbor_snapshots (user_id = them)
6. Restore: app downloads that JSON → merges into localStorage after confirm
7. RLS ensures every query is “where user_id = me”
```

Free users never need this path. Local Harbor keeps working.

---

## 8. Safety checklist (print this)

Before running SQL:
- [ ] Project name is clearly **Harbor** (not a shared experiment DB with other data)  
- [ ] Database password saved offline  

After SQL:
- [ ] Four tables visible in Table Editor  
- [ ] Tables empty  
- [ ] No red errors in SQL Editor history  

Auth:
- [ ] Email provider enabled  
- [ ] You understand confirm-email choice  

Keys:
- [ ] Only **URL + anon** will go in the app  
- [ ] **service_role** stays secret  
- [ ] Not pasted into public GitHub  

---

## 9. What you do **not** need to do yet

| Skip for now | Why |
|--------------|-----|
| Edge Functions | Later (webhooks, OAuth secrets) |
| Storage buckets | Later (photos) |
| Custom domains | Later |
| Production email templates | Later |
| Connecting RevenueCat / App Store | After backup works |
| Deleting RLS to “make testing easier” | Never — breaks security model |

---

## 10. After you’re done — message me with

Copy/paste something like:

```text
Supabase Harbor project ready.
URL: https://xxxx.supabase.co
anon key: eyJ....
Email auth: on
Confirm email: on/off
Tables: profiles, harbor_snapshots, households, household_members — all empty
```

Then **I will**:
1. Wire Supabase into Harbor (sign in, backup, restore)  
2. Keep Free fully offline  
3. Use sandbox Pro + later `profiles.is_pro`  
4. Walk you through the first test account end-to-end  

---

## 11. If you get stuck

| Symptom | Fix |
|---------|-----|
| Project still “setting up” | Wait; refresh dashboard |
| SQL Editor blank after run | Check **History** for error text |
| Don’t see tables | Confirm schema filter is **public** |
| Lost DB password | Project Settings → Database → reset password |
| Want a clean slate | Project Settings → **Pause/Delete project** → create new one |

---

## 12. Glossary (quick)

| Term | Meaning |
|------|---------|
| **Postgres** | The database engine Supabase runs |
| **Schema `public`** | Default place for app tables |
| **UUID** | Random unique id for users/rows |
| **JSONB** | JSON stored in the database (our backup blob) |
| **JWT** | Token proving “this request is user X” |
| **RLS** | Per-row security rules |
| **Cascade delete** | Deleting parent deletes children (user → their snapshots) |

---

## File map on your machine

```text
Desktop/Harbor/
  docs/
    PRO-IMPLEMENTATION.md          ← overall Pro phases
    FREE-VS-PRO.md                 ← product Free vs Pro
    supabase/
      GETTING-STARTED.md           ← this guide
      schema.sql                   ← run in SQL Editor
      config.example.js            ← template for keys
      config.local.js              ← YOU create (secrets; don’t commit)
  js/
    harbor-cloud.js                ← client stub (we’ll expand next)
```

---

You’ve got this. Order of operations:

1. New Harbor-only project  
2. Run `schema.sql`  
3. Verify tables  
4. Enable Email auth  
5. Copy URL + anon key  
6. Tell me you’re ready  

That’s the entire “don’t mess up” path for a first Supabase backend.
