# Harbor Calendar — v1 locked story

**Effective:** Harbor build **v177+**  
**Goal:** No surprise third-party proxy. Privacy matches the UI.

---

## User-facing promise (v1)

> **Schedule stays on your device.**  
> Add events by hand, or import a calendar **file** (`.ics`).  
> You can paste a secret iCal URL — Harbor will only talk to **that calendar host**.  
> A **network helper** (third-party proxy) is **off unless you turn it on** in Settings.

---

## What works in v1

| Method | Needs internet | Leaves device | Notes |
|--------|----------------|---------------|--------|
| Manual events | No | No | Always works |
| **Import .ics file** | No (file from user) | No | **Recommended** for Google/Outlook privacy |
| ICS URL — **direct fetch** | Yes | Calendar host only | Fails if host blocks browser CORS (common for Google) |
| ICS URL — **network helper** | Yes | Host **+** helper | **Opt-in only** in Settings |

---

## What is locked out of “default” behavior

| Behavior | v1 rule |
|----------|---------|
| Auto-retry via allorigins / corsproxy / etc. | **Only if** Settings → Allow Network Helper = **On** |
| New installs | Helper **Off** |
| Existing installs (upgrade to v177) | One-time migration sets helper **Off** (user can re-enable) |
| Surprise proxy with no UI | **Forbidden** |

---

## Settings copy (source of truth)

- **Primary path:** Import File  
- **URL path:** Secret address in iCal format (`basic.ics`)  
- **Helper:** Off by default; clear warning that a third party may see the feed URL when On  

---

## Why Google secret ICS often fails without a helper

Browsers enforce **CORS**. Many calendar hosts do not allow a website to read the ICS feed with JavaScript.  
That is a browser security rule — not a Harbor bug.

**v1 answer:** Use **Import File**, or enable helper knowingly, or wait for **Pro OAuth** later.

---

## Device calendars (TestFlight / store — build 319+)

| Method | Notes |
|--------|--------|
| **On this phone** | Reads calendars already on the device (EventKit). Permission required. No Google OAuth. |
| Works in | Native Harbor app only — not the browser PWA |
| Scope | Read events into Schedule (~2 weeks back → ~4 months ahead). Hide in Harbor does not delete from Apple Calendar. |

## Future (not v1)

| Later | Notes |
|-------|--------|
| Google Calendar API / Microsoft Graph | Real account sync; needs OAuth + backend |
| Write-back to device calendar | Optional later |
| Your own CORS proxy | Still a middleman — document it; better if you operate it |

---

## QA checklist

- [ ] Fresh install: helper switch Off  
- [ ] Direct ICS that supports CORS still works  
- [ ] Google secret ICS without helper: clear error + suggest Import File  
- [ ] Helper On: feed can load via proxy; toast/privacy mention risk  
- [ ] Privacy modal + privacy.html match this doc  

---

*Related: [PRIVACY.md](./PRIVACY.md) · [FREE-VS-PRO.md](./FREE-VS-PRO.md)*
