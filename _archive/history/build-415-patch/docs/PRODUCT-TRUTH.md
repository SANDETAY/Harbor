# Harbor — product truth (agent / builder memory)

**Last verified:** 2026-07-30 (from working tree / build **415** patch line)  
**Source of truth for UI/logic:** `index.html` (monolith). Do not invent features from old release notes or prior chat.

When in doubt: **grep the live `index.html`**, don’t trust memory.

---

## What Harbor is

Calm, **local-first** life OS: energy-aware **Task** list + **Daily Brief** + **Life** (schedule/grocery/bills/subs) + **Streaks** + **Library**.  
Core promise: *Your day, matched to your energy.*

- **No account required** for solo local use.
- Cloud / household / invites are **optional** later paths (Supabase when configured).
- Free first; Pro is mostly not a hard wall yet (sandbox + themes/budget notes in Settings).

---

## Navigation (chrome)

| Control | Role |
|---------|------|
| **Task** (tab `today`) | Primary home — due work, energy sort, complete/swipe |
| **Life** (tab + flyout) | Schedule, Grocery, Bills, Subscriptions, Budget (Pro/sandbox) |
| **Library** | Ready-made habits/chores to add to Task |
| **Streaks** | Streak fires, Harbor Day / rest rewards, outlook |
| **⚓ FAB** | **Daily Brief** (not a fifth “home” for chores — a day dashboard) |
| **Menu (☰)** | Settings, account/cloud, backup/export, Quick tour, What’s New, etc. |

**Life panels order:** `schedule` → `grocery` → `bills` → `subscriptions` → `budget`.

---

## Settings (what actually exists)

`showSettings()` sections:

1. **Color palette** — mint/night free; more = Pro  
2. **Preferences** — Smart Suggestions on/off · Harbor Day on/off  
3. **Your day** — **Bedtime** + **Morning window** only  
   - These shape habit *ranking*, quiet nudges, Brief timing  
   - Explicit UI copy: *“not a second checklist”*  
4. **Reminders** — notifications, appointments, bills, morning check-in, quiet routine *nudges* (timing hints, not editable checklists)  
5. **Calendar** — sync device calendars / refresh feeds  
6. **Tools** — weather; Advanced = Pro sandbox, network helper, voice tips  
7. **Reset** — factory reset  

### Removed (do not re-document as live)

- **Morning / evening routine checklists** in Daily Brief  
- **Routine step editors** in Settings → Your day  
- Release note (build **396**): *“Morning & evening routine cards removed from Brief and Settings”*

### Naming traps

| Phrase | Means |
|--------|--------|
| **Your day** (Settings) | Bedtime + morning window only |
| **Coming up** (Task) | Weekly/monthly/parked *tasks* not on Today — not Settings routines |
| **Quiet routine nudges** | Notification timing (floss window, free-gap walk) — not a checklist UI |
| **Starters** | Onboarding seed tasks |
| **Library** | Preset catalog |

**Dead code may remain** (`morningRoutineSteps`, `eveningRoutineSteps`, `.hv-ritual*`, `.settings-routine-*` CSS).  
If UI entry points are gone, treat as **legacy leftovers to delete**, not product features.

---

## Daily Brief (⚓)

One dashboard (`showSummaryModal` → day mode):

- Greeting + **day load** (light / moderate / heavy)  
- **Quick links** / meta chips (tasks, events, grocery, bills, when-you-can)  
- **Calendar** remaining today  
- **Do this next** (energy/work-aware ranking)  

Not a place for morning/evening checklist cards (removed).

---

## Task tab concepts

- **Energy** Low / Med / High — reorders Task (core superpower)  
- **Smart banner** — contextual tip; may show **life chips** (due this week / renewing soon)  
- Sections: Habits / Chores / Tasks (when mixed), Completed today, **Coming up**  
- **Wind-down** strip after bedtime  
- **Harbor rest strip** when Harbor Day is on  

---

## Onboarding & teaching

**First-run wizard (5 steps):** Welcome → name → pick starters → day rhythm (bedtime/morning) → done (tour or dive in).

**Quick tour (~6 steps):** Task complete/swipe → Energy → Daily Brief → Life → Harbor Day → Library & Menu.  
Always skippable; Menu → Quick tour again.

---

## Data & platforms

- State: on-device (`localStorage` / app storage; key family around `harbor_state_v1`)  
- PWA + Capacitor **iOS/Android**; `webDir` = `native-www` via cap prepare  
- App ID: `com.sandetay.harbor`  
- Build: bump `HARBOR_BUILD_NUMBER` + `sw.js` `CACHE_NAME` together  

---

## Agent rules

1. **Re-read Settings / Brief / tabs before claiming a feature exists.**  
2. Do not say “edit routines in Settings” — that path was removed.  
3. Prefer plain language for users; product codenames in code only when needed.  
4. Edit **`index.html`** for app behavior; freemium HTML is sandbox only.  
5. Prefer this file + live code over `SESSION-SAVE.md` (often stale build numbers).
