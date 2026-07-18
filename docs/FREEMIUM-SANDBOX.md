# Harbor freemium sandbox

**Production app:** `index.html` (unchanged)  
**Review sandbox:** `freemium.html` (phone shell) → loads `freemium-app.html` (mobile UI)

## Open it

```bash
npm start
open http://localhost:3000/freemium.html
```

## Free vs Premium (what is gated)

| Free | Premium |
|------|---------|
| Harbor Mint + Harbor Night | Lilac, Blush, Peach, Lagoon |
| Tasks, habits, streaks (fires) | **Harbor Day** rewards |
| Bills, Subscriptions, Grocery, Schedule | **Budget** (lock on Life menu) |
| Calendar: **.ics file** + **secret link** | **Sync iPhone / phone calendars** |
| **Personal** Library tasks (your own) | **Preset** Library chores (+ hire-a-pro) |
| Daily Brief (full — not gated) | Same |
| Direct calendar feeds (no network helper) | Calendar network helper |

Toggle: **Settings → Harbor Premium → Premium unlocked**

## Daily Brief

Left **fully free** on purpose: it’s the “plan before you execute” hub. Paywalling it would make Free feel broken. Premium differentiates with Budget, phone calendar, Harbor Day, and presets instead.

## Storage isolation

| Key | Used by |
|-----|---------|
| `harbor_state_v1` | Production `index.html` |
| `harbor_state_freemium_v1` | `freemium-app.html` |
| `harbor_freemium_premium_v1` | Premium on/off |

## Do not ship

Store / TestFlight stay on `index.html`.
