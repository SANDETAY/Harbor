# Harbor widgets & day rhythm (build 396+)

## Home Screen widgets

Four WidgetKit widgets ship with the iOS app (Apple-style system backgrounds):

| Widget | Sizes | Shows |
|--------|-------|--------|
| **Day** | M / L | Greeting, free window, next event, top tasks, grocery/bills counts |
| **Tasks** | S / M / L | Open Today tasks + count |
| **Next up** | S / M | Next calendar event + free time |
| **Lists** | S / M | Grocery · tasks · bills · streak pulse |

### How data reaches widgets

1. Web app builds a JSON snapshot (`buildHarborWidgetSnapshot`) on every `saveState()`, app resume/background, and boot.
2. Capacitor plugin `HarborWidgets` dual-writes to App Group UserDefaults **and** a shared container file  
   (`group.com.sandetay.harbor` / `harbor-widget-snapshot.json`).
3. Widget extension reads that snapshot and redraws (~15 min + on app save).

### Native registration (Capacitor 6)

Local plugins are **not** auto-registered. Harbor does both:

- `packageClassList` includes `HarborWidgetsPlugin` in `ios/App/App/capacitor.config.json`
- `HarborBridgeViewController.capacitorDidLoad()` calls `bridge?.registerPluginType(HarborWidgetsPlugin.self)`

After `npx cap sync`, re-check `packageClassList` still has `HarborWidgetsPlugin` (sync can overwrite it). The bridge subclass keeps registration working even if the list is wiped.

### One-time Apple setup (required for live data)

In [Apple Developer](https://developer.apple.com) → Identifiers:

1. App ID `com.sandetay.harbor` → enable **App Groups** → add  
   `group.com.sandetay.harbor`
2. App ID `com.sandetay.harbor.widgets` → same App Group
3. In Xcode: App target **Signing & Capabilities** → App Groups checked  
   Widget target **Signing & Capabilities** → same group

Then: **rebuild & reinstall** the app (not just web refresh) → open Harbor once so a snapshot is written → long-press Home Screen → **+** → **Harbor** → add widgets.

---

## Daily Brief (build 396+)

Morning/evening **checklist rituals were removed** from Brief and Settings.

**Brief stack (top → bottom):**

1. **Greeting** — `Good Morning, {name}` (period + optional first name)
2. **Load line** — Morning/Afternoon/Evening looking light / moderate / heavy · free until / free after work
3. **Quick links** — Task · Schedule · Grocery · Bills · Streaks · Library
4. **Calendar** — remaining timed events for today (+ empty state / add event)
5. **Do this next** — smart-ranked Task items (energy, work hours, free gaps)

### Work hours

`state.settings.workSchedule` (Life → Schedule → Hours):

| Mode | Effect on Brief |
|------|-----------------|
| **preset / custom** (e.g. 9–5) | Free clause can say “Free after work · 5 PM”; Do this next demotes outdoor/errands mid-block |
| **flexible / off** | No invented work block; load uses events + tasks only (stay-at-home friendly) |

Bedtime + morning window remain under **Settings → Your day** for habit ranking (floss / wind-down), not as checklists.

### Ranking (Do this next)

Uses `rankHabitsForNow` + `isSmartSuggestable` + `isHabitSensibleNow` on Task-due habits (`belongsOnTodayTab`).  
Work hours, energy, free gaps, and optimal-time boosts (hygiene windows) still apply.

---

## Explicitly not this feature

- **Coming up** on Task (weekly/monthly habits) — still shipped  
- **Harbor Day** rest meter — separate product  
