# Door · Home · House — simple for stuck, deep for stays

**Status:** Design + **Phase A + B implemented** (Door copy, quiet Life empty, soft “what’s heaviest?” after first win, Settings focus, Task invite chip). **Simple Add** in First week (name + energy; full form under More options). Phase C/D skipped unless beta asks.  
**Related:** [FIRST-WEEK-SIMPLE-MODE.md](./FIRST-WEEK-SIMPLE-MODE.md), [PRODUCT-TRUTH.md](./PRODUCT-TRUTH.md), [PUBLIC-BETA.md](../PUBLIC-BETA.md).

**Principle:** Feel simple for the stuck person; stay deep for the person who stays.  
**Not:** An app for everyone. **Not:** A module cafeteria on day one.

---

## The three layers

| Layer | Name | User state | What Harbor is |
|-------|------|------------|----------------|
| **1** | **Door** | Stuck / first session / First week | Task + energy + one next step. A complete calm app, not a teaser. |
| **2** | **Home** | Returning, a few wins | Task + Brief feel natural. Life/Streaks invite softly when relevant. |
| **3** | **House** | Stays, builds a life OS | Full Harbor: Life panels with data, Streaks, household, Pro depth. |

### Product rules (non-negotiable)

1. **Task + energy are always the core.** Never optional. Never hidden by a module picker.
2. **No multi-select “what do you want to track?” on first open.** That is analysis paralysis in a form.
3. **Empty Life stays quiet.** Full Life gets a louder seat.
4. **Depth is always findable** (tabs + Menu + “Show full Harbor”). We dim and de-prioritize; we don’t brick features.
5. **Every new feature asks: door, home, or house?** Door must earn a win in &lt;2 minutes. House never blocks door.

---

## What we already have (keep, tighten)

| Piece | Role |
|-------|------|
| First week (`simpleMode: 'auto'`) | Door chrome: hide smart banner, rest strip, Coming up, mute Streaks/Library labels |
| First week checklist | Progress path: complete → energy → add → Brief → peek Life |
| Graduation | Completions, days, checklist done, or “Show full Harbor” |
| Onboarding 5 steps | Welcome → name → starters → rhythm → done (tour / dive in) |

**Gaps to close:**

- Onboarding still feels like setup (starters + rhythm) before a win  
- No soft “what’s heaviest?” *after* first win  
- Life tab still looks like a full suite even when empty  
- “Peek Life” in checklist can open an empty Type-A dashboard  
- Graduation can feel like “baby mode ended” if copy is wrong  

---

## Onboarding flow (exact screens + copy)

**Goal:** Get to Task with a name and something to complete — not a configured life OS.

### Screen 0 — Welcome (keep, tighten copy)

**Title:** Harbor  
**Line:** Your day, matched to your energy.  
**Sub:** When everything feels like too much — one next step.  
**Primary:** Continue  

Avoid: “life OS,” “all-in-one,” feature laundry lists.

### Screen 1 — Name (keep)

**Title:** What should we call you?  
**Primary:** Next  

### Screen 2 — Starters (keep, reframe)

**Title:** A few things to start  
**Sub:** You can change these anytime. Just pick something you’ll actually do.  
**Primary:** Next  

Cap visual density: prefer 4–6 starters, not a wall. Default selection stays light (1–3).

### Screen 3 — Day rhythm (keep, one line of honesty)

**Title:** When does your day wind down?  
**Sub:** Helps rank habits quietly — not a second checklist.  
**Primary:** Next  

### Screen 4 — Done (keep structure, fix CTAs)

**Title:** You’re set  
**Sub:** Start with Task. Energy first, then one thing.  
**Primary:** **Go to Task**  
**Secondary:** 60-second tour (optional)  

No third CTA about Life/Bills/Subscriptions.

### Explicitly NOT in onboarding

- Module multi-select (Schedule, Bills, Subs…)  
- Household setup  
- Calendar connect (offer later, from Schedule or Settings)  
- Pro pitch  
- “What’s heaviest?” (that’s **after** first win — see below)

---

## Soft focus: “What’s heaviest?” (optional, post-win)

**When:** After first **real** task completion (not tour taps), once only, if First week still on.  
**Not:** During onboarding. **Not:** Blocking. Always skippable.

### Sheet copy

**Kicker:** One question  
**Title:** What’s one thing you need help tracking?  
**Options (single select):**

| id | Label | Hint (small) |
|----|--------|----------------|
| `tasks` | Stuff I need to do | Stay on Task (default) |
| `money` | Money / bills | We’ll surface Bills when you’re ready |
| `home` | Home / groceries | Grocery & recipes when useful |
| `time` | Calendar / appointments | Schedule & calendar later |
| `unsure` | Not sure yet | Just Task for now |

**Primary:** Save  
**Secondary:** Skip  

### What it does (gentle only)

Persist: `state.settings.focusArea` = one of above (or null if skipped).

| focusArea | Effect while Door/Home |
|-----------|-------------------------|
| `tasks` / `unsure` / null | No extra Life push. Default First week. |
| `money` | After 1+ completion: one quiet Task chip or empty-state line → “Bills live under Life when you’re ready.” Life open defaults toward bills *once* if they follow the chip. |
| `home` | Same pattern for grocery/recipes — not a forced Life tour. |
| `time` | Same for schedule; calendar connect stays opt-in in Schedule/Settings. |

**Never:** Hide Task. Never remove other Life panels permanently. Never empty the nav.

Later (House): focusArea can rank Life flyout order only; user can change in Settings → Preferences → **What feels heaviest** (optional).

---

## First week checklist (Door) — tighten

### Keep core three (required feel)

1. Complete a task  
2. Set energy once  
3. Add something of your own  

### Soften advanced rows

4. **Open Daily Brief** — unlock after 1–2 above; label: “See your day at a glance”  
5. **Peek at Life** — rename to **“When you’re ready: Life”** and only emphasize if:
   - `focusArea` is money/home/time, **or**
   - user already has any Life data  

If focus is tasks/unsure and Life is empty, row 5 can stay optional/muted or appear only after Brief.

### Card chrome (copy already close)

- **Kicker:** First week  
- **Title:** When you freeze — start here  
- **Sub:** energy + one next task  
- **Foot:** Show full Harbor  

---

## Life quiet until used (ruleset)

**Idea:** Life is one home with panels. Empty panels don’t recruit. Full panels do.

### Data helpers (concept)

```text
lifeHasSchedule   → events / calendar linked / user-added appointments
lifeHasGrocery    → any grocery items
lifeHasBills      → any bills
lifeHasSubs       → any subscriptions
lifeHasBudget     → budget configured (Pro)
lifeHasAny        → any of the above
```

### While First week (Door)

| Surface | Rule |
|---------|------|
| Life tab | Still exists (depth findable). Optional label treatment: normal, not “later,” **or** soft “Life” without badge spam. |
| Life open, `!lifeHasAny` | **Quiet empty state only** — not a grid of empty modules shouting setup. One line + one action. |
| Smart Life chips on Task | Already suppressed in First week — keep. |
| Checklist “peek Life” | Opens quiet empty state, not “set up Bills + Subs + Budget.” |

#### Quiet Life empty state (copy)

**Title:** Life is for the load outside today’s list  
**Body:** Bills, groceries, schedule — when you need them. Nothing to set up first.  
**Primary:** Back to Task  
**Secondary (small):** Browse Life areas  

“Browse” reveals panel list without requiring fill-in.

### After graduation (Home / House)

| Surface | Rule |
|---------|------|
| Life flyout order | Default: schedule → grocery → bills → subs → budget. If `focusArea` set, pin that domain first once, then restore natural order after first visit or always pin lightly. |
| Empty panel | Short empty state + single add CTA. No cross-sell of 4 other empty panels. |
| Panel with data | Full UI; can appear on smart chips / Brief when relevant. |
| Smart Life chips | Only for domains with data **or** overdue urgency (existing bill logic). Never invent empty chips for “setup Bills.” |

### Permanent hide of modules?

**No** as v1. Hiding creates support debt and “where did Schedule go?”  
Optional later (House power): Settings → **Life areas on flyout** checkboxes — default all on; uncheck only hides from flyout, not from deep links / search / household.

---

## Door chrome (First week) — keep list

Already in CSS/`applyFirstWeekChrome` — maintain:

- Hide: smart banner, life chips, rest strip, Harbor Day section, habit outlook, Coming up, person filter  
- Mute: Streaks + Library tab labels (“· later”)  
- Show: Task, energy, First week card, FAB Brief  

**Task empty / starters line:** Keep human: energy + tap when done. No feature tour in the list.

---

## Graduation (Home) — copy + behavior

| Trigger | Behavior |
|---------|----------|
| Checklist complete | Toast: **First week done — Full Harbor is ready** |
| Auto (completions / days) | Toast: **Full Harbor is ready** — Life & rest rewards are easier to find |
| User: Show full Harbor | Same as checklist path; respect choice |

After graduate:

- Remove `is-first-week` chrome  
- Pro invite stays **one quiet sheet** (existing)  
- Optional once: soft line on Task if `focusArea` money/home/time and that Life panel still empty — dismissible  

---

## Settings

| Control | Maps to |
|---------|---------|
| **First week layout** | `simpleMode` on/off (existing) |
| **What feels heaviest** (optional) | `focusArea` — same options as sheet; “Not sure” clears push |
| Feature guide | Documents full House for stays |

---

## Soft-prompt pacing (live)

**Max one pitch sheet per calendar day** + **~20 min cooldown** between sheets.

| Prompt | When | Notes |
|--------|------|--------|
| **What’s heaviest** | First week, after a real complete | Only First-week pitch |
| **First week done** | Graduate | Toast only — no sheet |
| **Harbor Pro** | Optional onboarding step + Menu / feature gates | Soft deferred invites **retired** |
| **Harbor Day intro** | First Streaks visit after First week (if Day enabled) | Day budget only; no Pro wait |
| **Beta check-in** | Open, day 2+, not on complete | Never stacks on First week completes |
| Harbor Day “i” tip | Inline on Streaks | Not a full-screen pitch |

Helpers: `canShowSoftPrompt`, `markSoftPromptShown`. `maybeFlushDeferredProInvite` only clears legacy flags.

---

## Implementation phases (when we build)

### Phase A — Copy & Door polish (low risk) — done

1. Onboarding welcome + done copy  
2. Checklist title/hints; mute Life row when empty + tasks focus  
3. Quiet Life empty state when `!lifeHasAny`  
4. Simple Add in First week  

### Phase B — Soft focus sheet — done

1. `state.settings.focusArea`  
2. Show sheet once after first non-tour completion  
3. Persist + Settings editor  
4. One dismissible Task invite chip by focusArea  

### Phase C — Life ranking & empty panels

**Skipped** unless beta asks.

### Phase D — Optional power (later)

**Skipped** unless beta asks.

---

## Success signals (beta)

| Signal | Good | Bad |
|--------|------|-----|
| Time to first completion | Down | Onboarding drop before Task |
| “Too much / Type A” pulse | Down in week 1 | Same or up |
| Life panel with data (day 14) | Up among stayers | Forced empty setup |
| “Show full Harbor” early | Some power users OK | Most users never leave Door and never complete a task |

---

## One-paragraph positioning (for beta / store)

> Harbor is for when everything feels like too much. You get one next step that fits your energy — not another dashboard to configure. Stay longer and Life, streaks, and household tools open up when you need them. Built for analysis paralysis; deep enough for a full home.

---

## Decision log

| Decision | Choice | Why |
|----------|--------|-----|
| Module picker at onboarding | **No** | Decision tax on stuck users |
| Soft “heaviest” after first win | **Yes** | Signal without homework |
| Hard-hide unselected modules | **No** (v1) | Brittle; empty shells |
| Quiet empty Life | **Yes** | Feels simple without deleting depth |
| Task always core | **Yes** | Product truth |

---

## Next step for engineering

Implement **Phase A** first (copy + quiet Life empty), then **Phase B** (focus sheet). Do not ship Phase D until beta asks for it.
