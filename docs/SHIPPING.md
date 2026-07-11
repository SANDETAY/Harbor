# Shipping Harbor — Capacitor, stores, TestFlight

This is the **runway** from today’s PWA to App Store / Play.  
Do **not** start ads or complex pricing before a **TestFlight** (iOS) / internal testing (Android) build feels good to real users.

**iOS App Store deep dive:** [APP-STORE-IOS.md](./APP-STORE-IOS.md) (bundle ID, Xcode, TestFlight, screenshots).

---

## 0. Prerequisites (you)

| Item | Notes |
|------|--------|
| **Node.js 20+** | Required for Capacitor CLI (`node` / `npm` on PATH) |
| **Apple Developer** | ~$99/year for TestFlight + App Store |
| **Mac + Xcode** | Required to archive iOS (or a cloud Mac CI later) |
| **Google Play Console** | ~$25 one-time for Android |
| **Privacy URL** | Use `https://sandetay.github.io/Harbor/privacy.html` (or your domain) after deploy |
| **Support email** | Real inbox you monitor |

**This machine snapshot:** Node was not available when the scaffold was added. Install Node, then run the setup steps below.

---

## 1. Product freezes before stores

Complete these (docs already in repo):

1. [FREE-VS-PRO.md](./FREE-VS-PRO.md) — free vs paid  
2. [CALENDAR-V1.md](./CALENDAR-V1.md) — no surprise proxy  
3. [PRIVACY.md](./PRIVACY.md) + live `privacy.html`  

Daily-drive the **PWA** until you would recommend it to a friend.

---

## 2. Capacitor scaffold (in this repo)

Layout:

```
Rythm/   (or Harbor repo root)
  index.html          # app UI
  capacitor.config.json
  package.json        # scripts: cap:sync, etc.
  native-www/         # optional built copy for native (see script)
  ios/                # created by `npx cap add ios` (on a Mac)
  android/            # created by `npx cap add android`
  docs/SHIPPING.md    # this file
```

### First-time setup (after installing Node)

```powershell
cd C:\Users\Taylor\Rythm
npm install
npm run cap:prepare
npx cap add android
# On a Mac:
# npx cap add ios
npm run cap:sync
```

| Script | Purpose |
|--------|---------|
| `npm run cap:prepare` | Copies web assets into the folder Capacitor serves |
| `npm run cap:sync` | prepare + `cap sync` |
| `npm run cap:android` | Open Android Studio |
| `npm run cap:ios` | Open Xcode (Mac) |

`capacitor.config.json` points `webDir` at the prepared web folder (see package scripts).

---

## 3. TestFlight path (iOS) — before pricing complexity

1. Enroll in **Apple Developer Program**  
2. On a Mac: open `ios/App.xcworkspace` via `npx cap open ios`  
3. Set **Bundle ID** (e.g. `com.yourname.harbor`) — unique forever  
4. Signing: your Team + automatic signing  
5. **Product → Archive**  
6. Distribute to **App Store Connect**  
7. In App Store Connect: create app record, privacy policy URL, screenshots  
8. Add build to **TestFlight** → Internal testing (you) then External (up to ~100, Beta review)  
9. Collect feedback for **1–2 weeks**  
10. Only then: Pro pricing, IAP, marketing push  

### TestFlight checklist

- [ ] App launches to Harbor, not blank WebView  
- [ ] Safe areas (notch) OK on modern iPhone  
- [ ] Today / Streaks / Life usable  
- [ ] Calendar: import file works; helper off by default  
- [ ] Weather permission string accurate in `Info.plist`  
- [ ] Privacy policy URL opens  
- [ ] No crash on cold start offline (degraded OK)  
- [ ] Version + build numbers increment each upload  

### Required privacy usage strings (examples)

When you add plugins, Xcode will need purpose strings, e.g.:

- **Location** (weather): “Harbor uses your location to show a local weather forecast.”  
- **Calendars** (only if you add native calendar later): honest purpose  

---

## 4. Play Console path (Android) — parallel

1. Create app in Play Console  
2. `npx cap open android` → generate signed **AAB**  
3. Internal testing track first  
4. Same privacy URL + data safety form (local storage, location optional, no sale of data)  

---

## 5. Pricing timing (explicit)

| When | What |
|------|------|
| PWA + TestFlight | **Free** only |
| After testers happy | Define Pro IAP products in App Store Connect / Play |
| Public launch | Free app + optional Pro |
| **Not yet** | Ads, complex tier trees, paywalling core Today |

---

## 6. What Capacitor does *not* give you

- Not a backend  
- Not Google OAuth by itself  
- Not multi-device sync  
- Not automatic App Store approval  

Those are separate projects after the shell works.

---

## 7. Suggested order of work (you)

1. Install **Node 20 LTS** on your PC  
2. Deploy latest `main` so `privacy.html` is live  
3. Use Harbor daily as PWA for a week  
4. `npm install` + `cap add android` (and ios on Mac)  
5. Internal TestFlight + Play internal  
6. Fix bugs from testers  
7. Revisit [FREE-VS-PRO.md](./FREE-VS-PRO.md) prices  
8. Public store release  

---

*Scaffold configs live at repo root: `capacitor.config.json`, `package.json` scripts, `scripts/cap-prepare.ps1`.*
