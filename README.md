# Rhythm Web App (Design Preview)

Shareable **full-width responsive website** of **Rhythm** for design review and user testing before the native iOS/Android build. Fills your browser on desktop; still works great on phones.

## Quick Start (Local)

```powershell
cd "P:\App Projects\Projects\webapp"
powershell -ExecutionPolicy Bypass -File scripts\start-server.ps1
```

Open **http://localhost:3000** in Chrome or Edge (best for voice + location features).

Or double-click `index.html` to open directly in your browser (some features like service worker require a local server).

## Share With Testers

### Option A — Netlify Drop (fastest, free)

1. Run `npm run zip` to create `rhythm-webapp-deploy.zip`
2. Go to [https://app.netlify.com/drop](https://app.netlify.com/drop)
3. Drag the zip onto the page
4. Copy the URL Netlify gives you and send it to testers

### Option B — Netlify connected site

1. Push this folder to a GitHub repo
2. Connect the repo in Netlify (build command: none, publish directory: `.`)
3. Every push auto-deploys

### Option C — Add to iPhone home screen

1. Open the deployed URL in Safari
2. Tap Share → **Add to Home Screen**
3. Rhythm launches full-screen like a native app

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
| Calendar sync (Google/Outlook/Apple) | Simulated — connects in UI, mock data |
| Garmin / Apple Health sync | Simulated — UI placeholder |
| Subscriptions tracker | Live (manual + CSV import) |

Data is stored in the browser (`localStorage`). Each tester gets their own isolated data on their device.

## Reset for Fresh Test

Settings → **Factory Reset** restores the first-time experience.

## Project Structure

```
webapp/
  index.html              # Full Rhythm prototype
  manifest.webmanifest    # PWA install config
  sw.js                   # Offline cache for assets
  rythm-r-mark.png        # App icon
  rythm-wordmark.png      # Onboarding wordmark
  netlify.toml            # Deploy headers
  package.json            # Local dev server
  scripts/
    create-deploy-zip.ps1 # One-click Netlify Drop zip
```

## Next Step: Native App

When testing feedback is solid, the prototype logic ports to **Expo + React Native** per the architecture plan in `habit-ease/ARCHITECTURE.md`.