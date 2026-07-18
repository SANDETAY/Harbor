# Harbor freemium sandbox

**Production:** `index.html` (unchanged)  
**Review:** `freemium.html` → `freemium-app.html` (mobile)

## Free vs Premium (sandbox)

### Free — complete daily OS
| Keep free |
|-----------|
| Today, tasks, habits, complete flows |
| Streaks (fires / tracking) |
| Daily Brief (full) |
| Schedule, Grocery, Bills, Subscriptions |
| Calendar via **.ics file** or **secret link** |
| Themes: **Mint + Night** |
| Weather, notifications, local data |
| Library: **empty of presets** — can **Add personal** only |

### Premium — justify the upgrade
| Unlock |
|--------|
| **Full Library catalog** (presets populate) |
| **Budget** (bank CSV) — lock on Life menu |
| **Sync iPhone calendars** (one-tap device) |
| **Harbor Day** rewards |
| Extra palettes (Lilac, Blush, Peach, Lagoon) |
| Calendar network helper |

## Product principle

Free must feel calm and complete for one person, one device.  
Premium removes friction and adds depth — not a crippled Free app.

## Honest monetization note

Sandbox gates are enough to **review UX** and a **low-priced** Premium (e.g. yearly or lifetime).  
Stronger App Store justification later: **cloud backup**, **multi-device sync**, **seamless calendar OAuth** (see `FREE-VS-PRO.md`). Those need a backend or native work — not hopeless, just the next layer.

## Storage

| Key | App |
|-----|-----|
| `harbor_state_v1` | Production |
| `harbor_state_freemium_v1` | Freemium sandbox |
| `harbor_freemium_premium_v1` | Premium toggle |

Do not ship freemium files as the store entry.
