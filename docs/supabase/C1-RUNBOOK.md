# C1 Household linking — what you run in Supabase

## Before you start
- Phase B (`schema.sql`) already applied  
- Email auth works; you can sign in from Harbor  

## Run this SQL
1. Supabase → **SQL Editor** → New query  
2. Open on your Mac:  
   `Desktop/Harbor/docs/supabase/schema-c1-household.sql`  
3. Copy **all** → paste → **Run**  
4. Success = green (no rows is normal)

If you already ran an older C1 draft, re-run the full file — it uses `create or replace` / `drop policy if exists` and is safe to re-apply.

## What this adds
| Object | Purpose |
|--------|---------|
| `household_invites` | Secure one-time invites (token **hashed** at rest) |
| RPCs | `create_household`, `create_household_invite`, `accept_household_invite`, `leave_household`, `remove_household_member`, `list_my_households`, … |
| RLS | Members only see their household; invites not listable by token scan |
| Entitlement lock | `profiles.is_pro` / `pro_until` not writable by end-user JWT |

**Not included:** shared tasks, bills, budget (budget never shared).

## Test in Harbor (build 412+)
1. Pro sandbox ON  
2. Two browsers or accounts: A and B  
3. A: Menu → Household → **Create household** → **Create invite code** → Copy  
4. B: Sign in → Household → paste code → **Join**  
5. A: should see B under members  
6. A: Edit local “Wife” person → **Link to cloud member** → pick B  
7. Reload A — linked status should still show (cloudUserId preserved)

## Security notes
- Invite code is 64 hex chars; shown **once**; stored as SHA-256 only  
- Expires in **7 days**; single use  
- Max **10** pending invites per household  
- Owner cannot leave while others remain (must remove them first)  
- Publishable key alone cannot list invites or join without a valid token  
- **No direct REST writes** on households / members / invites — join/leave/invite only via RPCs  
- **One household per user** — `UNIQUE(user_id)` on members + create/accept checks  
- **No membership oracle** — helpers take household id only (bound to `auth.uid()`)  
- **`profiles.is_pro` not client-writable** — trigger + column grants freeze entitlements for JWT users  
- **Budget is never shared** (not in schema, not in RPCs, not in UI)  
- Local `cloudUserId` is a UUID map only — does not grant cloud access by itself  
- Pro UI gate is still client-side for sandbox testing; the entitlement **row** is server-protected  

## If something fails
| Error | Meaning |
|-------|---------|
| function does not exist | C1 SQL not run |
| Only the household owner can invite | Signed in as member, not owner |
| Leave your current household… | Already in another household |
| Invalid invite code | Typo, expired, already used, or revoked |
| unique constraint / one_household | User already has a membership row (leave first) |
