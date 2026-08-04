# 01 — How Harbor works

## In one sentence

Harbor is a **single web app** (`index.html`) wrapped for **iOS** with **Capacitor**, with optional **Supabase** cloud and **home-screen widgets**.

```
┌─────────────────────────────────────────────────────────┐
│  YOU (browser or iPhone)                                │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────▼─────────────┐
        │  index.html  (the app UI) │  ← edit here for product
        │  sw.js       (offline)    │
        └─────────────┬─────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     localStorage           Capacitor iOS
     (tasks etc.)           App + Widgets
                                  │
                                  ▼
                          App Group snapshot
                          → Home Screen widgets
                                  │
               optional ──────────▼──────── optional
                          Supabase (auth, household, OAuth)
```

Android (Capacitor + Play) is **parked** in `_archive/android/` — not part of active shipping.

## Layers (professional mental model)

| Layer | Folder / files | Job |
|-------|----------------|-----|
| **Product UI** | `index.html`, `sw.js`, icons | What users see and tap |
| **Web packaging** | `manifest.webmanifest`, `privacy.html` | PWA + legal |
| **Native shell (iOS)** | `ios/`, `capacitor.config.json` | TestFlight / App Store |
| **iOS widgets** | `ios/App/HarborWidgets/` | Home Screen widgets |
| **Bridge** | `HarborWidgetsPlugin.swift`, `js/harbor-cloud.js` | Web ↔ native / cloud |
| **Backend** | `docs/supabase/` | SQL, edge functions, config |
| **Ops docs** | `docs/` (this tree) | How *you* run the company of Harbor |
| **Android (archived)** | `_archive/android/` | Revive later when you have a device |

## Data

- **Default:** stays on the device (localStorage).  
- **Cloud:** only if `docs/supabase/config.local.js` is present and user signs in.  
- **Widgets:** app writes a JSON snapshot into the iOS App Group; widgets read it.

## Environments

| Environment | What it is | Who uses it |
|-------------|------------|-------------|
| **Local web** | Browser + local server | Daily product work |
| **GitHub Pages** | Live PWA URL | Testers, privacy URL |
| **Simulator / device debug** | Xcode run | Widget + native checks |
| **TestFlight** | Apple beta | Real-phone ship |
| **App Store / Play** | Public | Customers |

## What you “own” after ship

When Harbor is done, you still need:

1. Apple Developer account + App Store Connect  
2. (If cloud) Supabase project + OAuth provider consoles  
3. GitHub repo for web deploys  
4. This handbook + bookmarks folder  

Minor bugs → ask your coding agent. Architecture / logins / stores → use these docs + bookmarks.
