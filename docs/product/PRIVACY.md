# Privacy Policy — Harbor

**Last updated:** 2026-07-30  
**Product:** Harbor (life management app — web / PWA / store builds)  
**Contact:** Use in-app Feedback, or the support email listed on the App Store / Play listing when published.

This policy describes Harbor as it ships **today**: **local-first by default**, with **optional** account/cloud features when you sign in.

---

## Short version

- Harbor is **local-first**. Tasks, energy, Life data, streaks, and most settings live **on your device**.  
- An account is **not required**. **Account & cloud** is optional (when configured).  
- Harbor does **not** sell your personal data.  
- Harbor does **not** show ads.  
- Optional features may send limited data to **services you choose to use** (weather, calendar helper, feedback, or cloud if you sign in).

---

## 1. Who we are

Harbor is operated by the independent publisher of the app (see store listing / repository owner).  
“We” means that publisher. “You” means the person using Harbor.

---

## 2. Data we store on your device

When you use Harbor, the app may store on **your device only** (e.g. `localStorage` / app storage):

- Tasks, habits, chores, **Morning / Evening** list items, completions, skips, and streak data  
- Energy preference and smart-suggestion / first-week state  
- Bills, grocery lists, meal presets, subscriptions  
- Calendar **events** you create or import  
- Calendar **feed URLs** you paste (stored locally)  
- Local household **color tags** / schedule labels  
- Harbor Day / reward bank progress  
- Theme and UI preferences  
- Optional profile fields you enter (name, city, etc.)

If you clear site data, uninstall the app, or lose the device without a backup export, **this data can be lost**.

**Your control:** Export/import tools, Factory Reset, sign-out of cloud (if used), and browser/OS “clear data.”

---

## 3. Optional Account & cloud (Supabase)

If you open **Account & cloud** and the app is configured with backend credentials, Harbor may use **Supabase** (or a similar host) for:

1. **Authentication** — email and password (or related auth the product enables).  
2. **Backup snapshots** — data you explicitly **push** or **pull** (not silent full-device surveillance).  
3. **Household linking** — invite codes, membership, and related rows (structure for sharing). This is **not** the same as automatically uploading every local task unless you use backup/sync features that do so.

If **Account & cloud** is not configured or you never sign in, this path is unused and your day stays fully local.

Auth and cloud traffic use **HTTPS** to the backend host. That host processes account and snapshot data under their infrastructure and our configuration (row-level security where implemented).

---

## 4. Data that may leave your device (other features)

### 4.1 Weather

If you allow location / live weather:

- Approximate location may be sent to a forecast provider (e.g. **Open-Meteo**) to return weather data.  
- You can decline location and still use Harbor without live weather.

### 4.2 Calendar feeds (ICS URL)

1. Harbor tries to fetch the feed **directly** from the calendar host.  
2. **Network helper (optional):** Off by default. If you enable it in Settings, a **third-party CORS helper** may see the **full feed URL** (including private tokens on secret calendars).  
3. Prefer **Import file (.ics)** for maximum privacy.  
4. Device calendars (store app) are read on-device; event copies stay local.

### 4.3 Feedback

Message text, optional reply email, and basic technical context (app version, rough device type) may be sent via a feedback provider. Do not include passwords or secret calendar links.

### 4.4 Camera / microphone

Only when you use recipe camera/OCR or voice add. Not used for advertising. Prefer typed entry if you prefer not to grant access.

### 4.5 Local notifications & widgets

Bill/task reminders (store app) are scheduled **on device**. iOS widgets use an on-device app-group snapshot — not a Harbor ad network.

### 4.6 App updates / hosting

Loading the web app or store updates may create ordinary host/CDN logs (IP, user agent) under those providers’ policies.

---

## 5. What we do not do

- No sale of personal data  
- No advertising networks in the app  
- No hidden trackers for ad profiling  
- No **requirement** to create a Harbor account for core Task / Life use  

---

## 6. Sharing with other people

- **Export Profile** creates a file on your device; you choose how to share it.  
- **Cloud household invites** (when signed in) use invite codes you generate.  
- Local household color tags on Schedule are on-device unless you also use cloud household features.

---

## 7. Children

Harbor is a general productivity/life app, not directed at children under 13. Do not use the app to collect data from children under 13.

---

## 8. Security

We use reasonable technical measures appropriate for a local-first app with optional cloud:

- **HTTPS** for network traffic to our backend and providers  
- **On-device storage** for core data by default (protected primarily by your device lock)  
- **Optional cloud (Supabase):** authentication (Apple / Google / email when enabled), **row-level security (RLS)** so authenticated users can only access their own rows (e.g. backup snapshots under their user id; household membership only for households they belong to)  
- **Optional calendar OAuth (Google Calendar):** separate from account login; refresh tokens are designed to stay **server-side** (Edge Functions + restricted column grants); the client app is not meant to read refresh tokens  
- Cloud backups are **account-scoped snapshots**, not end-to-end encrypted vaults — protect your sign-in like any cloud account  

No method of transmission or storage is 100% secure. Third-party weather, helper, feedback, Apple/Google/Microsoft, and cloud infrastructure providers have their own practices.

---

## 9. Changes

We may update this policy. Material changes to cloud sync scope, household sharing, or calendar networking will be reflected in-app and here with a new “Last updated” date **before** those changes ship.

---

## 10. Contact

Questions: use in-app **Feedback**, or the support contact on the public app listing.

---

## Store listing snippet (copy/paste)

> Harbor is local-first: tasks and plans stay on your device. Weather uses location only if you allow it. Calendar URLs fetch directly by default; an optional network helper is off unless you enable it. Optional Account & cloud (when configured) is for sign-in, backup you control, and household invites. No ads. No required account for core use.

---

*Public HTML mirror: [`/privacy.html`](../privacy.html).*
