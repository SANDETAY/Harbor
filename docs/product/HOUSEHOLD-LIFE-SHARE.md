# Household share — selective Life + bidirectional Tasks

**Build:** 447+  
**SQL:** `docs/supabase/schema-c1c-life-share.sql` (after C1 household membership)  
**Payload:** `household_life_share` pack **v4** with portable person refs + `shareMeta`.

## Bidirectional

**Owner and family members** can both push. Example: wife shares her list so husband (owner) can see it; husband assigns chores to wife and sees Dones after refresh.

## What can be shared (per device checklist)

Each phone picks **what leaves that phone** — never a forced full dump.

| Category | What syncs | Default |
|----------|------------|---------|
| **Bills** | Life bills | On |
| **Subscriptions** | Renewals | On |
| **Grocery** | Shared list items | On |
| **Recipes** | Custom recipe book (ingredients, cooking cards, cover thumbs) | On |
| **Schedule events** | Harbor calendar events | On |
| **Family-assigned tasks** | Tasks tagged Wife / kids / multi-assign | On |
| **My own task list** | Me-only tasks on *this* phone (so partner/owner can see them) | On |
| **People tags** | Names/colors + cloud user link for mapping | On |

**Recipes notes:** Only **custom** recipes (Recipe book) merge by id across phones. Built-in weeknight dinners stay local. Cover photos are optional compressed thumbs only (no scan photos).

**Never shared:** Budget, Hire/pro schedule rows, device calendar OAuth tokens, full solo cloud backup.

## Task identity (important)

“Me” on wife’s phone is **not** “Me” on husband’s. Harbor rewrites assignees to portable `user:<uuid>` refs so:

- Her personal tasks show under **her** person tag on his phone  
- Completions still merge by task id after Fetch / app open  

## Task filter (owner focus)

- Default filter **Me** — your work, not family noise  
- **Family** menu — check one person  
- **All** — household view  

## Continuous sync

1. Both **sign in** and join the same household.  
2. Each person: Household → check categories → **Share my selected items**.  
3. Auto-sync (default): push after changes, pull on open.  
4. **Fetch latest** if something is stuck.

Turning a category **off** does not wipe others’ already-shared data for that category.

## Setup (Supabase)

1. `schema.sql`  
2. `schema-c1-household.sql` (or `FIX-household-invite-ambiguous.sql`)  
3. `schema-c1c-life-share.sql`  

## Limits (honest)

- Not realtime sockets — pull on open + push on change / manual.  
- Same Supabase project for both accounts.  
- Invite codes: 7 days, single use.  
- Prefer **Complete** for finished chores.  
- **Deletes of shared tasks** use tombstones (`deletedHabitIds` in the pack) so they don’t reappear after sync.  
- **Deletes of people tags** (kids / custom labels) use `deletedProfileKeys` so Fetch / auto-sync does not re-add them. Linked household accounts (signed-in partner) are never permanently suppressed.  
- **Deletes of custom recipes** use `deletedRecipeIds` so Fetch / reopen does not re-add a recipe you removed. Weeknight dinners are local builtins and are not tombstoned.  
- **Deletes of grocery items** use `deletedGroceryIds` so a partner’s Fetch cannot resurrect a line you removed. Edits / checks use `updatedAt` so the newer change wins on merge.  
- **Task assignees:** Partner tags you by name → your phone shows **Me**, not the author. Legacy ambiguous `me` refs still map to the author.  
- Concurrent push: other phone’s pack is pulled and re-merged; a toast explains conflict recovery.

## Test script

Full two-phone checklist: **[docs/handbook/09-household-two-phone-test.md](../handbook/09-household-two-phone-test.md)**

Quick path:

1. A and B signed in; A creates household + invite; B joins.  
2. A: bills on, grocery off, tasks assigned on.  
3. A: task “Dentist” tagged **Wife** → Share selected.  
4. B: Fetch → bill + Wife task appear; A’s “Me” tasks do not.  
5. B completes shared task → Share or auto-sync → A reloads → completion shows.  
6. A deletes a shared task → B Fetch → task stays gone.

*Related: [FREE-VS-PRO.md](./FREE-VS-PRO.md) · schema-c1c-life-share.sql*
