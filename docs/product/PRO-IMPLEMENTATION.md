# Harbor Pro — implementation plan

**Status:** In progress (app gates first; cloud next)  
**Updated:** 2026-07-29  

## Product freeze (complete release scope)

### Free (no account)
- Task, energy, Brief, Library  
- Life: Schedule, Grocery, Bills, Subscriptions  
- Streaks + Harbor Day  
- Themes: **Harbor Mint** + **Harbor Night** only  
- Local export / import  
- Device calendars + ICS file / URL (as today)  

### Pro (subscription)
| Feature | Phase |
|---------|--------|
| Budget tab | **A — app gates (now)** |
| Extra themes (Lilac, Blush, Peach, Lagoon) | **A — app gates (now)** |
| Account (Supabase Auth) | **B** |
| Cloud backup + multi-device sync | **B** |
| Share with partner (tasks, grocery, bills, subs) | **C** |
| OAuth calendars (Google) | **D** |
| Store IAP (RevenueCat or native) | **B/E** (sandbox toggle until then) |

---

## Phase A — Entitlement + UI gates ✅ / in repo

1. `isHarborPro()` — sandbox flag + future store/cloud flags  
2. Upgrade sheet explaining Pro  
3. Lock Budget (Life tab + flyout)  
4. Lock non–Mint/Night themes in Settings  
5. Menu entry: Harbor Pro  
6. Settings: developer/sandbox **Unlock Pro** toggle  

## Phase B — Supabase foundation

**You first (beginner walkthrough):** `docs/supabase/GETTING-STARTED.md`

1. Create Supabase project (you)  
2. Run `docs/supabase/schema.sql`  
3. Enable Email auth; copy URL + anon key  
4. (Dev) Add URL + anon key → local config (gitignored)  
5. Sign in / out UI in Harbor (agent)  
6. Push/pull `harbor_snapshots` (export JSON)  
7. Wire `isHarborPro` to `profiles.is_pro` + sandbox  

## Phase C — Household share

### C1 — Membership only (implemented — run `schema-c1-household.sql`)
1. `households` + `household_members` + hashed invites  
2. Secure invite code (RPC-only accept; SHA-256 at rest)  
3. Local person tags link to `cloudUserId`  
4. **Budget is never shared** (excluded from Pro family scope for now)

### C2 — Shared work (later)
1. Shared grocery / assigned tasks  
2. Still no budget share unless product decision changes

## Phase D — Calendar OAuth

1. Edge Function holds OAuth secrets  
2. Google Calendar (then Outlook)  
3. Merge into Schedule as Pro source  

## Phase E — Real money

1. App Store / Play subscriptions  
2. RevenueCat → webhook → `profiles.is_pro`  

---

## Local testing (no Supabase yet)

Settings → Advanced → **Harbor Pro (sandbox)** ON  
→ Budget + all themes unlock.

---

## Files

| Path | Role |
|------|------|
| `index.html` | Gates + upgrade sheet + sandbox |
| `docs/FREE-VS-PRO.md` | Product copy |
| `docs/supabase/schema.sql` | Tables + RLS |
| `docs/supabase/config.example.js` | Keys template |
| `js/harbor-cloud.js` | Client stub (Phase B) |
