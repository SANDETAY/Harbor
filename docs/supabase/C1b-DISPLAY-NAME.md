# C1b — Display name (not email prefix)

## Why
Household members showed the email local-part when `profiles.display_name` was empty.

## Run in Supabase
1. **SQL Editor → New query**
2. Paste all of `schema-c1b-display-name.sql`
3. **Run** (safe to re-run)

## App (build 413+)
- **Household** → when linked, **Your name in this household** → Save  
- **Account & cloud** (signed in) → **Display name** → Save  

Both call RPC `set_my_display_name` (updates `profiles` + `household_members`).

## Optional
Owner can rename the household via RPC `rename_household` (client method exists; UI can be added later).
