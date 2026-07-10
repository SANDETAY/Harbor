# Harbor — Free vs Pro

**Status:** Product decision doc (v1). Not all Pro items are built yet.  
**Rule:** Free must feel complete for **one person, one device, local-first**. Pro removes friction and unlocks multi-device / deep integrations.

---

## Positioning

| Tier | Promise |
|------|---------|
| **Harbor Free** | Calm daily life OS on *this* device. No account required. |
| **Harbor Pro** | Same calm UI — plus backup/sync, seamless calendars, household, and native power features. |

**Suggested price (indie starting point):**  
~$3.99/mo · ~$29.99/yr · optional early lifetime ~$49–$79  

Final numbers can wait until TestFlight feedback. **Do not build ads** until after a paid Pro path is clear.

---

## Free (base) — ship this first

### Core daily
| Feature | Free notes |
|---------|------------|
| Today list + complete tasks | Full |
| Energy Low / Medium / High sort | Full |
| Smart suggestions (muteable) | Full |
| Quick add + voice add (where supported) | Full |
| Summary / Overview FAB | Full |

### Life
| Feature | Free notes |
|---------|------------|
| Schedule — manual events | Full |
| Schedule — **Import .ics file** | Full (privacy-safe) |
| Schedule — ICS URL **direct fetch only** | Full (many hosts fail without helper) |
| Groceries + dinner lists | Full |
| Bills | Full |
| Subscriptions (manual + CSV) | Full |
| Household colors (local profiles) | Full |
| Profile export / import (file share) | Full |

### Streaks & rest
| Feature | Free notes |
|---------|------------|
| Streak fires (satisfaction-ranked list) | Full |
| Habit Outlook + metric log | Full |
| Harbor Day meter + claim | Full |
| Custom rewards | Full (reasonable cap already in app) |

### Library & chrome
| Feature | Free notes |
|---------|------------|
| Task library | Full |
| Weather (on-device permission → Open-Meteo) | Full |
| Themes (mint / coastal night) | Full |
| Privacy sheet + factory reset | Full |
| Local backup export | Full |

### Explicitly free forever (brand)
- No ads in Free or Pro  
- No selling personal data  
- Local-first core remains usable offline once assets are cached  

---

## Pro — paid unlocks (build in this order)

### P1 — Why people pay (build after store shell)

| Feature | Why Pro | Needs backend? |
|---------|---------|----------------|
| **Cloud backup / restore** | Survive phone loss; peace of mind | Yes |
| **Multi-device sync** | Phone + tablet + desktop | Yes |
| **Seamless Google / Outlook calendar** (OAuth) | Real sync without secret ICS + proxy | Yes |
| **Network helper for ICS** (optional) *or* native calendar read | Friction removal; keep opt-in | Proxy = no; OAuth/native = yes/native |

### P2 — Household & power

| Feature | Why Pro | Needs backend? |
|---------|---------|----------------|
| **Live household share** (spouse) | Beyond file export/import | Yes |
| **Push reminders** (bills, events, gentle nudges) | Store-native value | Capacitor + push service |
| **Home-screen widgets** | Glanceable Today / next event | Native |
| **Unlimited calendar feeds** (if Free caps at 1–2) | Power users | No (local) or yes if cloud |

### P3 — Later differentiators

| Feature | Why Pro | Needs backend? |
|---------|---------|----------------|
| Real Apple Health / Garmin style sync | Fitness truth | Native + APIs |
| Advanced analytics / year in review | Pride | Local OK |
| Priority support | Soft | Process |

---

## What stays free even after Pro exists

Do **not** paywall:

- Completing tasks  
- Basic streaks + Harbor Day  
- Grocery / bills / basic subs  
- .ics **file** import  
- Local export backup  
- Weather  

Paywalling these would break “calm daily OS” trust.

---

## Soft Free limits (optional, fair)

If you need a Free/Pro wedge without cloud yet:

| Limit | Free | Pro |
|-------|------|-----|
| ICS **URL** feeds | 1 feed, direct only | Unlimited + OAuth later |
| Network helper (proxy) | Off / not offered | Opt-in advanced **or** replaced by OAuth |
| Custom Harbor rewards | Cap ~12 (already) | Higher cap |
| Household profiles | 2–4 | Unlimited |

Prefer **value unlocks** over aggressive caps.

---

## Monetization path

1. **Now:** Free PWA only — no IAP  
2. **TestFlight / internal Play:** Free build, gather feedback  
3. **Store public:** Free app  
4. **Pro v1:** IAP (Apple/Google) for cloud backup + calendar OAuth  
5. **Never first:** Ads  

Store rule of thumb: digital Pro features → **in-app purchase**, not only a random website paywall (especially on iOS).

---

## Decision checklist (you)

- [ ] Confirm Free list feels “complete enough” for daily use  
- [ ] Pick first Pro wedge: **cloud backup** vs **calendar OAuth** (recommend backup first)  
- [ ] Pick price band after 10–20 real users  
- [ ] Legal name on privacy policy + store listings  

---

*Related: [CALENDAR-V1.md](./CALENDAR-V1.md) · [PRIVACY.md](./PRIVACY.md) · [SHIPPING.md](./SHIPPING.md)*
