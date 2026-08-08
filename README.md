# Harbor

**Home folder:** `/Users/brittany/Desktop/Harbor`  
**Start here:** [docs/START-HERE.md](docs/START-HERE.md)  
**Bookmarks:** [docs/bookmarks/open-bookmarks.html](docs/bookmarks/open-bookmarks.html)  
**Glossary:** [docs/glossary/harbor-programming-terms.md](docs/glossary/harbor-programming-terms.md)

> **Active mode:** TestFlight **iOS app only**. Website auto-deploy is **frozen**. Android CI is **removed** (archive only under `_archive/android/`). Secrets live in `private/` (gitignored).

---

Calm life management app: energy-based tasks, bills, grocery, streaks, calendar, and smart suggestions. **Data stays on the device** (`localStorage`).

This is a **Progressive Web App (PWA)** — one responsive `index.html` that works in the browser and can be **Add to Home Screen**’d like an app. You do **not** need to rewrite it into Swift/Kotlin to try it as an “app” today.

## Quick Start (Local)

```powershell
cd C:\Users\Taylor\Rythm
powershell -ExecutionPolicy Bypass -File scripts\start-server.ps1
```

Open in Chrome or Edge (best for voice + location features):

| Preview | URL |
|---------|-----|
| **Web** | http://localhost:3000/index.html |
| **Mobile** (phone frame) | http://localhost:3000/mobile.html |
| **Dual** (web + mobile side-by-side) | http://localhost:3000/dual-preview.html |

Edit **`index.html` only** — one responsive app powers web and mobile. Use `mobile.html` / `dual-preview.html` to verify layouts before you push. Do not double-click files for day-to-day testing (service worker + APIs need the local server).

## Share With Testers

### Option A — GitHub Pages (recommended if repo is on GitHub)

Your repo: **https://github.com/SANDETAY/Harbor**

1. On GitHub, open the repo → **Settings** → **Pages**
2. Under **Build and deployment**, set **Source** to **GitHub Actions**
3. Push to `main` — the workflow in `.github/workflows/deploy-pages.yml` deploys automatically
4. After 1–2 minutes, share: **https://harborlife.app/**

**Website freeze:** pushes to `main` do **not** update the live site until Brittany unfreezes GitHub Pages. Testers on web see the last deployed build; app work ships via TestFlight only.

**First-time setup (one click in GitHub UI):** If Pages shows 404, you must enable GitHub Actions as the Pages source once (step 2 above). The workflow file is already in the repo.

### Option B — Netlify Drop (fastest, no GitHub)

1. Run `npm run zip` to create `harbor-webapp-deploy.zip`
2. Go to [https://app.netlify.com/drop](https://app.netlify.com/drop)
3. Drag the zip onto the page
4. Copy the URL Netlify gives you and send it to testers

### Option C — Netlify connected site

1. Push this folder to a GitHub repo
2. Connect the repo in Netlify (build command: none, publish directory: `.`)
3. Every push auto-deploys

### Option D — Add to iPhone / Android home screen

1. Open the deployed URL in Safari (iOS) or Chrome (Android)
2. Share / menu → **Add to Home Screen** (or **Install app**)
3. Harbor launches full-screen like a native app

## What Works

| Feature | Status |
|---------|--------|
| Energy-based task prioritization | Live |
| Smart suggestions & tips | Live |
| Task library (preloaded chores) | Live |
| Bills, grocery, schedule | Live (local data) |
| Streaks | Live |
| Weather (hourly forecast) | Live (uses device location) |
| Voice commands | Chrome/Edge only |
| Calendar (ICS URL + file import) | Live — secret iCal URL and/or .ics file |
| Garmin / Apple Health sync | Simulated — UI placeholder (flagged off) |
| Subscriptions tracker | Live (manual + CSV import) |

Data is stored in the browser (`localStorage`). Each person gets their own isolated data on their device. Export/import from Menu for backups or sharing a household profile file.

## Making this a “real” store app

You **cannot** paste this HTML into Xcode/Android Studio and “import” it as native UI. Paths that *do* work:

| Path | Effort | Result |
|------|--------|--------|
| **PWA (now)** | Already done | Home-screen app, works offline for cached assets, no App Store required |
| **Capacitor / Cordova shell** | 1–3 days setup | Wraps this same web app in a native container → submit to App Store / Play Store |
| **Rebuild in React Native / Expo / Swift / Kotlin** | Weeks–months | True native UI; reimplement features, keep product logic/design |

**Recommended launch path:** ship the **PWA** for real use and feedback → when you want store listing / push / deeper device APIs, wrap with **[Capacitor](https://capacitorjs.com/)** (keeps `index.html` as the UI) *or* plan a native rebuild only if you need heavy native UX.

## Run Simulation Tests

```powershell
cd C:\Users\Taylor\Rythm
py -m pip install playwright
py -m playwright install chromium
py scripts\sim-test.py
```

Runs headless mobile-browser scenarios (onboarding, smart suggestions, Summary, energy sort, streaks, calendar ICS UI, fitness sync).

## Reset for Fresh Test

Settings → **Factory Reset** restores the first-time experience.

## Project Structure

```
Rythm/   (repo: SANDETAY/Harbor)
  index.html              # Full Harbor app
  privacy.html            # Public privacy policy (store URL)
  manifest.webmanifest    # PWA install config
  sw.js                   # Offline cache for assets
  capacitor.config.json   # Store shell config
  docs/                   # Free/Pro, calendar v1, privacy, shipping
  harbor-mark.svg         # Anchor mark (vector)
  harbor-icon-*.png       # PWA / home-screen icons
  netlify.toml            # Deploy headers
  package.json            # Dev server + Capacitor scripts
  scripts/
    create-deploy-zip.ps1
    cap-prepare.ps1       # Copy web assets for Capacitor
```

## Product & shipping

| Doc | Purpose |
|-----|---------|
| [docs/FREE-VS-PRO.md](docs/FREE-VS-PRO.md) | Free vs Pro matrix |
| [docs/CALENDAR-V1.md](docs/CALENDAR-V1.md) | Calendar v1 — helper off by default |
| [docs/PRIVACY.md](docs/PRIVACY.md) | Privacy policy (source) |
| [privacy.html](privacy.html) | Live privacy page for store listings |
| [docs/SHIPPING.md](docs/SHIPPING.md) | Capacitor, TestFlight, Play |

Privacy URL after Pages deploy: **https://harborlife.app/privacy.html**

### Capacitor (needs Node.js 20+)

```powershell
cd C:\Users\Taylor\Rythm
npm install
npm run cap:prepare
npx cap add android
# On a Mac: npx cap add ios
npm run cap:sync
```

TestFlight **before** ads or complex pricing — see [docs/SHIPPING.md](docs/SHIPPING.md).

## License

**Proprietary — All Rights Reserved.**

This project is **not** open source. You may **not** use, copy, modify, or share this code without written permission from the owner. See [`LICENSE`](./LICENSE) for the full terms.
