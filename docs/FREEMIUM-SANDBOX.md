# Harbor freemium sandbox

**Production app:** `index.html` (unchanged)  
**Review sandbox:** `freemium.html`

## Purpose

Review free vs Premium UX without risking the shipping app. Same look and behavior as Harbor, plus a **Settings → Harbor Premium** toggle.

## Open it

```bash
# from Harbor repo
npm start
# then
open http://localhost:3000/freemium.html
```

Or dual preview header → **Freemium review**.

## What is gated (sandbox)

| Free | Premium (toggle on) |
|------|---------------------|
| Harbor Mint + Harbor Night | All palettes (Lilac, Blush, Peach, Lagoon) |
| Direct calendar / file import | Calendar network helper |
| Full daily core (tasks, bills, grocery, streaks…) | Same + locked extras unlocked |

Tapping a locked palette or turning on network helper while Free opens a **Harbor Premium** sheet. **Preview Premium** flips the same toggle as Settings.

## Storage isolation

| Key | Used by |
|-----|---------|
| `harbor_state_v1` | Production `index.html` |
| `harbor_state_freemium_v1` | `freemium.html` only |
| `harbor_freemium_premium_v1` | Premium on/off (`1` / `0`) |

On first freemium open, if freemium storage is empty, state is **copied once** from production so you can review with real data. Edits in freemium do **not** write back to production.

Service worker registration is **skipped** in the sandbox so it won’t fight production cache.

## Do not ship

Do not set Capacitor `webDir` / store entry to `freemium.html`. Store and TestFlight stay on `index.html` until freemium is merged deliberately.
