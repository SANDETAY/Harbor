# First Week / Simple Mode — design

**Goal:** Make Harbor intuitive for the target audience without deleting power features.  
**Principle:** First session earns a win (add → energy → complete). Complexity unlocks after trust.

**Status:** Implemented (build 417+) — test via mobile.html. Aligns with `docs/PRODUCT-TRUTH.md`.

---

## Problem

Harbor is coherent for builders. New users face:

- Multiple “homes” (Task, Brief, Life, Streaks, Library)  
- Dense Task chrome (energy, smart banner, rest strip, Coming up, multi-kind sections)  
- Product language (Harbor Day, Coming up, Brief) before they’ve felt value  

Morning/evening **checklist** routines are **already removed** — don’t reintroduce them in Simple Mode.

---

## Product definition

### Simple Mode = default for first ~7 days (or until graduation)

A **presentation + prioritization layer**, not a separate app fork.

| | Simple Mode | Full Mode |
|---|-------------|-----------|
| Primary home | **Task only** | Task + free exploration |
| Energy | **Prominent** (always visible) | Compact OK |
| Smart banner | Tips for Task + energy only | Full catalog + life chips |
| Life chips on banner | Optional / muted | On when relevant |
| Coming up | Collapsed; show only if empty Today *or* user expands | Current behavior |
| Harbor Day / rest strip | **Hidden or single quiet line** | Full strip + Streaks depth |
| Streaks tab | Reachable but not pushed | Full |
| Life | Reachable; no “setup everything” push | Full |
| Daily Brief | Soft invite after day 2+ *or* after N completions | Full FAB presence |
| Onboarding end CTA | “Start with Task” primary; tour secondary | Same |

### Graduation (exit Simple Mode)

Any of:

- 7 calendar days after `onboardedAt`, **or**  
- 10 task completions, **or**  
- User taps **“Show full Harbor”** / turns off Simple Mode in Settings  

Persist: `state.settings.simpleMode` = `'auto' | 'on' | 'off'`  
- Default after onboarding: `'auto'` (on until graduation)  
- Explicit off stays off; explicit on stays on  

---

## User-facing name

Prefer **“First week”** in UI (friendly), not “Simple Mode” (can sound dumbed-down).

- Banner/checklist: **First week**  
- Settings: **First week layout** — *Focus on Task & energy; full tools unlock as you go*  
- Graduation toast: **Full Harbor is ready** — Life, Streaks, and rest rewards are easier to find  

---

## Concrete UI changes

### A. First-week checklist card (Task, top)

Dismissible card under smart banner (or replacing empty-state essays):

1. ☐ Complete a task (tap the circle)  
2. ☐ Set energy once (Low / Med / High)  
3. ☐ Add something of your own  
4. ☐ Open Daily Brief once *(unlocked after step 1–2)*  
5. ☐ Peek at Life *(optional)*  

Not a tour monologue — **progress**. Menu can reopen checklist.

### B. Chrome dimming (not deletion)

While First week **auto/on**:

- **Streaks** tab: slightly muted label or “later” badge; no rest-meter pressure on Task  
- **Harbor Day** strip: hidden until graduation *or* until Harbor Day toggle is on **and** user has 3+ completions  
- **Library**: still available (helps “add”); tour can mention lightly  
- Smart suggestions: suppress Harbor Day / streak-risk / sub-tier tips; keep overdue, energy, empty, weather  
- Life chips: show only if user already has bills/subs data (don’t invent clutter for empty Life)

### C. Daily Brief

- FAB stays (anchor identity)  
- First open during First week: short lead-in line — *“Your day at a glance — not another list.”*  
- Do **not** teach removed morning/evening checklists  

### D. Onboarding alignment

Done step currently offers tour vs dive in. Adjust copy:

- Primary: **Go to Task**  
- Secondary: **60-second tour**  
- Rhythm step stays (bedtime / morning window) — still valid; it’s ranking, not checklists  

### E. Settings

Under Preferences:

- **First week layout** switch (maps to `simpleMode` on/off; auto not exposed as third radio unless needed)  
- Help: *Hides rest rewards pressure and quiets extra chrome until you’ve used Task a bit.*

### F. Quick tour (when First week)

Shorten order:

1. Task complete  
2. Energy  
3. Add  
4. Brief (optional skip)  
5. Menu → Settings  

Defer Life / Harbor Day steps until Full mode (or mark “when you’re ready”).

---

## What we will **not** do in v1 of this

- Separate codebase or freemium shell as the “simple” app  
- Re-add morning/evening checklist builders  
- Hide Life entirely (partners need grocery path; keep one tap away)  
- Force account/household in week one  

---

## Success metrics (manual TestFlight)

Give app to 3 people who didn’t build it. After 10 minutes, without help:

| Check | Pass |
|-------|------|
| Completed ≥1 task | Required |
| Can explain energy in their words | Required |
| Finds Life grocery or bills if asked | Required |
| Doesn’t ask “what is Harbor Day?” unprompted | Nice |
| Feels “set up enough for tomorrow” | Required |

---

## Implementation sketch (when building)

1. `state.settings.simpleMode` + `onboardedAt` / `completionCount` helpers  
2. `isFirstWeekMode()` used by: Task feed chrome, smart banner filters, rest strip, tour step filter, checklist card  
3. Checklist UI + graduation toast  
4. Settings toggle  
5. Fix **stale copy** still claiming routines in Settings (tour/menu)  
6. Bump build + SW  

Estimated scope: focused patch in `index.html` only (~1–2 sessions), no schema.

---

## Open choices (confirm before code)

1. **Default:** First week on for everyone new — yes?  
2. **Existing users / TestFlight builds already onboarded:** leave Full (`simpleMode: 'off'`) so power users aren’t regressed?  
3. **Harbor Day:** hide strip entirely in First week, or keep tiny passive meter?  
4. **Life chips on smart banner:** keep as in 415, or First-week-hide until user opened Life once?  
