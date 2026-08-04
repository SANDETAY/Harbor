# Harbor — product truth (agent / builder memory)

**Last verified:** 2026-08-01 (build **488**)  
**Source of truth for UI/logic:** `index.html` (monolith). Do not invent features from old release notes or prior chat.

When in doubt: **grep the live `index.html`**, don’t trust memory.

**Public beta:** See [docs/PUBLIC-BETA.md](../PUBLIC-BETA.md). Channel flag `HARBOR_CHANNEL` (`beta` | `stable`). First week defaults to `simpleMode: 'auto'` for new installs.

---

## What Harbor is

Calm, **local-first** life OS: energy-aware **Task** list + **Daily Brief** + **Life** (schedule/grocery/bills/subs) + **Streaks** + **Library**.  
Core promise: *Your day, matched to your energy* — especially for **analysis paralysis** (one next step, not more menus).

- **No account required** for solo local use.
- **Optional cloud** (when Supabase is configured): Account (Apple / Google / email), Pro cloud backup/restore, Pro household share (invite + selective Life/tasks/recipes + delete tombstones), Pro Google Calendar OAuth. Menu → **Feature guide** documents these live.
- **Recipe share (text):** Recipe detail → Share recipe (or Share recipe + cooking card) — native share sheet / clipboard. Not the same as household sync.
- **Household recipes:** Custom recipe book merges by id when the **Recipes** share category is on (default). Built-in weeknight dinners stay local.
- Free first; Pro is sandbox-friendly in TestFlight (themes/budget + cloud gates).

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
| **Morning / Evening** (Create Task type) | Task-tab **list categories** for day-part items — not Settings checklists |
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
Door copy: energy-first / one next step (not module cafeteria). See [DOOR-HOME-HOUSE.md](./DOOR-HOME-HOUSE.md).

**First week checklist:** Core three (complete → energy → add). Brief + Life rows unlock after a start; empty Life is optional, not a setup assignment.

**Quiet Life empty:** When Life has no data, tab shows a calm intro (Back to Task / Browse Life areas) instead of empty multi-panel suite. `lifeEmptyBrowseSeen` after Browse.

**Focus area (Phase B):** After first real task completion in First week, optional sheet *What’s one thing you need help tracking?* → `settings.focusArea` (`tasks`|`money`|`home`|`time`|`unsure`). Settings → Preferences → **Help tracking**. Soft Task invite chip for money/home/time until dismissed or that Life domain has data.

**Create task types:** Task · Habit · Chore only (Morning / Evening list types removed from the form).

**Simple Add (First week):** `showQuickTaskModal` opens name + energy + Add; type / repeats / reminders under **More options**. Edit & Library always full. Session flag `__harborQuickAddFull` after expanding. After First week ends, full form by default.

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
