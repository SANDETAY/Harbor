# Privacy Policy — Harbor

**Last updated:** 2026-07-10  
**Product:** Harbor (life management app — web / PWA / future store builds)  
**Contact:** Use in-app Feedback, or the support email listed on the App Store / Play listing when published.

This policy describes Harbor as it ships **today** (local-first). If cloud accounts or Pro sync ship later, this policy will be updated **before** those features go live.

---

## Short version

- Harbor is **local-first**. Your tasks, streaks, bills, groceries, and most settings live **on your device** (browser storage).  
- Harbor does **not** require an account in v1.  
- Harbor does **not** sell your personal data.  
- Harbor does **not** show ads.  
- Some optional features send limited data to **third-party services you choose to use** (weather, optional calendar helper, feedback).

---

## 1. Who we are

Harbor is operated by the independent publisher of the app (see store listing / repository owner).  
“We” means that publisher. “You” means the person using Harbor.

---

## 2. Data we store on your device

When you use Harbor, the app may store on **your device only** (e.g. `localStorage` / app storage):

- Tasks, habits, completions, skips, and streak data  
- Energy preferences and smart-suggestion state  
- Bills, grocery lists, meal presets, subscriptions  
- Calendar **events** you create or import  
- Calendar **feed URLs** you paste (stored locally)  
- Household profile labels/colors  
- Harbor Day / reward bank progress  
- Theme and UI preferences  
- Optional profile fields you enter (name, city, weight for estimates, etc.)

We do **not** operate a Harbor cloud database for this data in v1.  
If you clear site data, uninstall the app, or lose the device without a backup export, **this data can be lost**.

**Your control:** Export/import tools in the app (where available), Factory Reset, and browser/OS “clear data.”

---

## 3. Data that may leave your device

Only when you use these features:

### 3.1 Weather

If you allow location / live weather:

- Approximate location (or coordinates from the device) may be sent to a forecast provider (e.g. **Open-Meteo** or similar) to return weather data.  
- You can decline location permission and still use Harbor without live weather.

### 3.2 Calendar feeds (ICS URL)

If you add a calendar URL:

1. Harbor tries to fetch the feed **directly** from the calendar host (Google, Microsoft, etc.).  
2. **Network helper (optional):** Off by default (v1). If you turn **Allow Network Helper** **On** in Settings, Harbor may fetch the feed through a **third-party CORS helper**. That helper can see the **full feed URL**, which for secret Google calendars may include a private token.  
3. Imported events and URLs remain stored **on your device** after fetch.  
4. **Import File (.ics)** never requires a network helper.

See also `docs/CALENDAR-V1.md`.

### 3.3 Feedback

If you submit feedback:

- Message text, optional reply email, and basic technical context (app version, rough device type) may be sent via a feedback delivery provider (e.g. FormSubmit / Web3Forms or email).  
- Do not include passwords or secret calendar links in feedback.

### 3.4 App updates / hosting

When you load Harbor from a website (e.g. GitHub Pages) or update a store build:

- Standard web/server logs (IP address, user agent) may be processed by the **host** (GitHub, Netlify, Apple, Google, etc.) under their policies.  
- CDN libraries (if used in a web build) may receive ordinary request metadata.

Store builds should **bundle** assets when possible to reduce third-party CDN dependency.

---

## 4. What we do not do

- No sale of personal data  
- No advertising networks in the app  
- No hidden trackers for ad profiling  
- No requirement to create a Harbor account in v1  

---

## 5. Sharing with other people

**Household / spouse:** Export creates a file on your device. You choose how to share it (Messages, AirDrop, email). Import only runs when you select a file. v1 does not provide live cloud “couple sync.”

---

## 6. Children

Harbor is a general productivity/life app, not directed at children under 13. Do not use the app to collect data from children under 13.

---

## 7. Security

We use reasonable technical measures appropriate for a **local-first** app (data at rest on your device; HTTPS when loading the web app).  
No method of transmission or storage is 100% secure.  
Optional network helper and third-party weather/feedback services have their own security practices.

---

## 8. International users

Processing is primarily on your device. Third-party services (weather, optional helper, feedback, hosting) may process data in other countries.

---

## 9. Changes

We may update this policy. Material changes that affect calendar helpers, cloud sync, or accounts will be reflected in-app and in this document with a new “Last updated” date **before** those features ship.

---

## 10. Contact

Questions: use in-app **Feedback**, or the support contact on the public app listing.

---

## Store listing snippet (copy/paste)

> Harbor stores your tasks and plans on your device. Weather uses location only if you allow it. Calendar URLs are fetched directly by default; an optional network helper (off unless you enable it) may see a feed URL to load blocked calendars. No ads. No account required in v1.

---

*Public HTML mirror for store URLs: [`/privacy.html`](../privacy.html) when deployed with the site.*
