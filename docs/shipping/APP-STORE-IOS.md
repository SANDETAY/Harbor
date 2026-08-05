# Harbor → Apple App Store (TestFlight first)

You are packaging the **Capacitor iOS shell** around the existing Harbor web app.  
This machine (Windows) can **scaffold** the project; **building and uploading requires a Mac with Xcode** (or a cloud Mac CI).

---

## What is already set up in this repo

| Item | Value |
|------|--------|
| Bundle ID | `com.sandetay.harbor` |
| Display name | Harbor |
| Marketing version | `1.0.0` |
| Build number | `350` (bump each upload) |
| Capacitor | 6.x + SplashScreen, StatusBar, App, Geolocation |
| Native HTTP | `CapacitorHttp` enabled (needed for iCloud calendar URLs) |
| Privacy policy | https://harborlife.app/privacy.html |
| Location string | Weather-only purpose (in `Info.plist`) |
| Encryption export | `ITSAppUsesNonExemptEncryption = false` |
| App icon | 1024×1024 in `ios/App/App/Assets.xcassets/AppIcon.appiconset/` |

---

## Reality check

| Step | Where |
|------|--------|
| Edit web app / config | Windows or Mac |
| `npm run cap:sync` | Windows or Mac |
| `pod install` | **Mac only** |
| Archive + Upload | **Mac + Xcode only** |
| App Store Connect listing | Any browser |
| Apple Developer Program | **Required (~$99/year)** |

Without an active **Apple Developer Program** membership you cannot ship TestFlight or the App Store.

---

## One-time: Apple side

1. Enroll: https://developer.apple.com/programs/  
2. App Store Connect → **My Apps → +** → new app  
   - Platform: iOS  
   - Name: **Harbor** (if taken, e.g. Harbor Daily / Harbor Life)  
   - Bundle ID: **com.sandetay.harbor** (create in Certificates, Identifiers & Profiles if needed)  
   - SKU: `harbor-ios-001`  
3. Privacy Policy URL: `https://harborlife.app/privacy.html`  
4. Support URL / email: your real inbox  

---

## On a Mac (build + TestFlight)

**Preferred folder on this machine:** `~/Desktop/Harbor`

### Splash-safe workflow (do this)

```bash
cd ~/Desktop/Harbor

# One-time after you tune LaunchScreen / Splash.imageset on the Mac:
bash scripts/mac-push-splash.sh

# Every later upload — pulls origin/main but KEEPS Mac splash:
bash scripts/mac-update-for-upload.sh
```

`mac-update-for-upload.sh` backs up splash assets, runs `git reset --hard origin/main`,
then restores splash so launch art never regresses.

### Manual (only if you know what you’re doing)

```bash
cd ~/Desktop/Harbor
git pull
npm install
bash scripts/cap-prepare.sh   # or: npm run cap:prepare
npx cap sync ios
cd ios/App && pod install && cd ../..
npx cap open ios
# opens ios/App/App.xcworkspace  ← use the .xcworkspace, not .xcodeproj
```

**Avoid bare** `git reset --hard origin/main` **after local splash edits** unless you
already ran `mac-push-splash.sh` (or use `mac-update-for-upload.sh`).

### In Xcode

1. Select **App** target → **Signing & Capabilities**  
   - Team: your Apple Developer team  
   - Automatically manage signing: **ON**  
   - Bundle Identifier: `com.sandetay.harbor`  
2. Select a real device or **Any iOS Device (arm64)** (not a simulator) for Archive  
3. **Product → Archive**  
4. Organizer → **Distribute App** → **App Store Connect** → Upload  
5. Wait for processing in App Store Connect (5–30 min)  
6. **TestFlight** → add build → Internal testing (you) → then External if you want  

### Version numbers each upload

| Field | Where | Example |
|-------|--------|---------|
| Marketing (user-facing) | Xcode `MARKETING_VERSION` | `1.0.0` → `1.0.1` |
| Build (must increase every upload) | Xcode `CURRENT_PROJECT_VERSION` | `260` → `261` |
| In-app build label | `HARBOR_BUILD_NUMBER` in `index.html` | keep in sync when you care |

---

## On Windows (what you can do now)

```powershell
cd C:\Users\Taylor\Rythm
npm install
npm run cap:prepare
npx cap sync ios
git add -A   # commit ios scaffold + web
git push
```

Then on a Mac: pull, `pod install`, Archive.

**You cannot finish App Store packaging on Windows alone.** Options if you have no Mac:

| Option | Notes |
|--------|--------|
| Borrow / buy a Mac | Simplest for first ship |
| MacStadium / MacinCloud | Rent a Mac by the hour |
| Codemagic / GitHub Actions `macos-latest` | CI builds IPA; still need Apple certs |

---

## App Store Connect listing (minimum for TestFlight external / release)

- [ ] App name + subtitle  
- [ ] Privacy Policy URL  
- [ ] Category (e.g. Productivity / Lifestyle)  
- [ ] Age rating questionnaire  
- [ ] Screenshots (6.7" and 6.1" iPhone at minimum)  
- [ ] 1024×1024 app icon (already in asset catalog)  
- [ ] Description + keywords  
- [ ] Support URL  
- [ ] **App Privacy** nutrition labels:  
  - Data not collected for tracking  
  - Location: optional, on-device weather  
  - Calendar feed URLs: only if user pastes them; stored on device  
- [ ] Review notes: “No login required. Grant location only for weather. Calendar is file import or user-pasted ICS URL.”

---

## TestFlight QA (before public release)

- [ ] Cold start → Today (not blank)  
- [ ] Notch / home indicator safe areas  
- [ ] Pick color palette → header not stuck Mint  
- [ ] Weather: allow location once; deny still OK  
- [ ] Calendar: **Import .ics** works  
- [ ] Calendar: paste iCloud URL → native HTTP may load (helper not required on device)  
- [ ] Offline: app opens (degraded weather/calendar OK)  
- [ ] No service worker fighting WebView cache  

---

## Apple calendar URL (why native helps)

Safari **blocks** live iCloud ICS downloads (CORS).  
On device, **CapacitorHttp** fetches without that browser rule, so her `webcal://` / https share link can work in the **store app** after you rebuild.

Still keep **Import file** as fallback.

---

## Commands cheat sheet

```powershell
# Windows — prepare + sync only
npm run cap:sync
npx cap sync ios
```

```bash
# Mac — full path to TestFlight
npm install && npm run cap:prepare && npx cap sync ios
cd ios/App && pod install && cd ../..
npx cap open ios
# then Product → Archive
```

---

## If something fails

| Symptom | Fix |
|---------|-----|
| Blank white screen | `npm run cap:prepare` then `npx cap sync ios`; confirm `ios/App/App/public/index.html` exists |
| Signing errors | Unique bundle ID + paid Developer team |
| Pod errors | `sudo gem install cocoapods` then `pod repo update` |
| Location crash / reject | Confirm `NSLocationWhenInUseUsageDescription` in Info.plist |
| “Missing compliance” | ITSAppUsesNonExemptEncryption already false; answer export questionnaire in Connect |

---

*Related: [SHIPPING.md](./SHIPPING.md) · [PRIVACY.md](../product/PRIVACY.md) · [FREE-VS-PRO.md](../product/FREE-VS-PRO.md)*
