# 09 — Household two-phone test (15 minutes)

Use this before shipping when family sharing matters.  
**Goal:** create → share → complete → both see Done, and remove doesn’t reappear.

## Prerequisites

| Check | |
|--------|--|
| SQL applied | `schema-c1-household` (or FIX scripts) + **`schema-c1c-life-share.sql`** |
| Both phones | Signed in (Apple / Google / email) to **same** Supabase project |
| Build | Same app build on both if possible |
| Pro | Sandbox Pro on if share UI is gated |

Call phones **A** (owner) and **B** (partner).

---

## Script

### 1) Household + invite
1. **A:** Menu → Household → **Create household** (if needed).  
2. **A:** **Create invite** → copy / Messages to B.  
3. **B:** Household → paste code → **Join**.  
4. Confirm both show the same household name / membership.

### 2) What to share
On **both** phones (or at least A):

- Enable: **Family-assigned tasks**, **My tasks** (if testing personal lists), **Bills** (optional).  
- **Auto-sync** on (default).  
- Tap **Share my selected items** once after setup.

### 3) Create one shared task (avoid title duplicates)
1. **A only:** Create task **“Harbor share test — unload dishwasher”**.  
2. Assign to **B** (or Me+B multi).  
3. Wait ~5s or tap Share.  
4. **B:** Open app (or Household → **Fetch latest**).  
5. **Expect:** Same task appears once on B (same title).

### 4) Complete on the other phone
1. **B:** Complete the shared task.  
2. Wait ~5s / Share if needed.  
3. **A:** Open app or Fetch.  
4. **Expect:** Task shows done / completed on A (not a second open copy).

### 5) Soft delete (tombstone)
1. **A:** Create **“Harbor delete test — wipe counter”** assigned to B.  
2. Sync so **B** sees it.  
3. **A:** **Delete** it (confirm “Remove for household”).  
4. **Expect toast:** “Removed for household (syncing…)”.  
5. **B:** Fetch / reopen.  
6. **Expect:** Task is **gone** (does not reappear after a minute).

### 5b) People-tag delete + assignee identity
1. **A:** Household → add child tag **Adeline** → Share (People tags on).  
2. **A:** Remove **Adeline** → wait for sync / Share once.  
3. **A:** Fetch / reopen.  
4. **Expect:** Adeline stays **gone** (not re-added from household pack).  
5. **A:** Create task **“Send Email”** tagged **B** (by name).  
6. **B:** Fetch.  
7. **Expect:** Task shows on B tagged as **Me / B’s name**, **not** as A’s name.

### 6) Conflict toast (optional stress)
1. Both phones offline (Airplane mode) if easy.  
2. **A** edits a bill or task; **B** edits something else in share categories.  
3. Go online on both.  
4. **Expect:** One device may toast  
   *“Household caught up with the other phone…”* or  
   *“Household updated on another phone…”*  
   — data should settle after both open/share once.

---

## Pass / fail

| Step | Pass |
|------|------|
| 3 | One shared task on B, not two titles created separately |
| 4 | Completion visible on A |
| 5 | Delete stays gone on B |
| 6 | Conflict toast if race; no permanent split brain |

## Failures → fix

| Symptom | Action |
|---------|--------|
| Invite / SQL errors | Run `FIX-invite-gen-random-bytes.sql` + household FIX / c1c |
| Share does nothing | Both signed in; categories on; Share once |
| Task reappears after delete | Build with tombstones (467+); Fetch on both; delete again |
| People tag reappears after delete | Build 479+ (profile tombstones); delete again + Share once; personal cloud **Restore** will put old tags back |
| Task shows author’s name on assignee’s phone | Build 479+; re-Share the task; B Fetch |
| Two “same” chores | Both people created their own — use **one** creator |
| No conflict toast | Normal if no race; only shows when concurrent push |

## Anti-duplicate rules (tell the household)

1. **One person creates** family chores.  
2. The other **completes**, doesn’t re-add the same title.  
3. Prefer **Complete** over Delete for finished work.  
4. After big edits, open Harbor on both phones once.

---

*Related: [HOUSEHOLD-LIFE-SHARE.md](../product/HOUSEHOLD-LIFE-SHARE.md) · [06-troubleshooting.md](./06-troubleshooting.md)*
