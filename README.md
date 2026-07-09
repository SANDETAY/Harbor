# Harbor Web App (Design Preview)

Shareable **full-width responsive website** of **Harbor** for design review and user testing before the native iOS/Android build. Fills your browser on desktop; still works great on phones.

## Quick Start (Local)

```powershell
cd "P:\App Projects\Projects\webapp"
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

Your repo: **https://github.com/SANDETAY/Rythm**

1. On GitHub, open the repo → **Settings** → **Pages**
2. Under **Build and deployment**, set **Source** to **GitHub Actions**
3. Push to `main` — the workflow in `.github/workflows/deploy-pages.yml` deploys automatically
4. After 1–2 minutes, share: **https://sandetay.github.io/Rythm/**

Every `git push` to `main` updates the live site. Testers can also **Add to Home Screen** on iPhone/Android for a full-screen app experience.

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

### Option D — Add to iPhone home screen

1. Open the deployed URL in Safari
2. Tap Share → **Add to Home Screen**
3. Harbor launches full-screen like a native app

## What Works in the Preview

| Feature | Status |
|---------|--------|
| Energy-based task prioritization | Live |
| Smart suggestions & tips | Live |
| Task library (preloaded chores) | Live |
| Bills, grocery, schedule | Live (local data) |
| Streaks & Cheat Day Fund | Live |
| Weather (hourly forecast) | Live (uses device location) |
| Voice commands | Chrome/Edge only |
| Calendar (ICS URL + file import) | Live — secret iCal URL and/or .ics file; direct fetch by default (optional network helper) |
| Garmin / Apple Health sync | Simulated — UI placeholder |
| Subscriptions tracker | Live (manual + CSV import) |

Data is stored in the browser (`localStorage`). Each tester gets their own isolated data on their device.

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
webapp/
  index.html              # Full Harbor prototype
  manifest.webmanifest    # PWA install config
  sw.js                   # Offline cache for assets
  harbor-mark.svg         # Anchor mark (vector)
  harbor-icon-*.png       # PWA / home-screen icons
  netlify.toml            # Deploy headers
  package.json            # Local dev server
  scripts/
    create-deploy-zip.ps1 # One-click Netlify Drop zip
```

## Next Step: Native App

When testing feedback is solid, the prototype logic ports to **Expo + React Native** per the architecture plan in `habit-ease/ARCHITECTURE.md`.