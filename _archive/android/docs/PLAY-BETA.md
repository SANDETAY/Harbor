# Harbor → Google Play (internal / closed beta)

**Goal:** Let a small group install Harbor from the Play Store (or opt-in link) without public launch.

**Package ID:** `com.sandetay.harbor`  
**Privacy:** https://sandetay.github.io/Harbor/privacy.html

---

## What you need

| Item | Notes |
|------|--------|
| Google account | Same one you’ll use for Play Console |
| **Play Console** | [play.google.com/console](https://play.google.com/console) — **$25 one-time** |
| This PC | Android SDK + JDK (already used for debug builds) |
| **Release keystore** | Created once, backed up forever (see below) |
| Signed **AAB** | Android App Bundle (not debug APK) |

---

## One-time: create signing keystore

```powershell
cd C:\Users\Taylor\Rythm
powershell -ExecutionPolicy Bypass -File scripts\create-android-keystore.ps1
```

That creates (all **gitignored**):

- `android/keystore/harbor-release.jks`
- `android/key.properties`
- `android/keystore/CREDENTIALS.txt` ← **print / save offline**

If you lose the keystore + passwords, you **cannot update** the same Play app.

---

## Every release: build the Play bundle

```powershell
cd C:\Users\Taylor\Rythm
npm run cap:prepare
npx cap sync android

$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot"
cd android
.\gradlew.bat bundleRelease
```

Output:

`android\app\build\outputs\bundle\release\app-release.aab`

Bump before next upload (in `android/app/build.gradle`):

- `versionCode` must **increase** every time (317 → 318 → …)
- `versionName` can match product (e.g. `0.9.318`)

---

## Play Console setup (browser)

### 1. Developer account
1. Open [Play Console](https://play.google.com/console)
2. Pay **$25**, complete identity if asked  
3. Wait until account is active

### 2. Create the app
1. **Create app**
2. App name: **Harbor**
3. Default language: English (US)
4. App or game: **App**
5. Free / paid: **Free**
6. Declarations: accept policies

### 3. Dashboard checklist (minimum for **internal testing**)
Complete enough of these to unlock testing (wording varies slightly):

| Section | What to enter |
|---------|----------------|
| **App access** | No login required (or “all features available without login”) |
| **Ads** | No |
| **Content rating** | Questionnaire (utility / lifestyle — answer honestly) |
| **Target audience** | 18+ or “not designed for children” if appropriate |
| **News / COVID / Data safety** | Fill forms |
| **Data safety** | Data collected: optional **location** (weather); **app activity** if you want to be thorough; storage is on-device. **Data is not sold**. No account. |
| **Privacy policy** | `https://sandetay.github.io/Harbor/privacy.html` |
| **Store listing** (can be draft-quality for internal) | Short description, full description, app icon (512×512), feature graphic (1024×500), 2+ phone screenshots |

Internal testing is lighter than production, but Google still blocks upload until critical policy items are done.

### 4. Internal testing track (best for “send to some people”)
1. **Test and release → Testing → Internal testing**
2. **Create new release**
3. Upload `app-release.aab`
4. Release name: e.g. `0.9.317 internal`
5. Save → **Review release** → **Start rollout to Internal testing**

### 5. Add testers
**Option A — email list (simplest)**  
1. Internal testing → **Testers** tab  
2. Create email list → add Gmail addresses  
3. Save  

**Option B — Google Group**  
Same idea with a group email.

### 6. Share the link
On the Internal testing page, copy the **opt-in URL** (looks like `https://play.google.com/apps/internaltest/...`).

Send that link + instructions:

> 1. Open the link on your Android phone (must use the **same Google account** we added as a tester)  
> 2. Accept to become a tester  
> 3. Install Harbor from Play Store  

First install can take **a few hours** after the release goes live while Play processes the build.

---

## Closed testing (optional later)
- Up to larger groups, may need more store listing polish  
- Use when internal list is too small  

**Production** = public. Skip until beta feedback is good.

---

## What *not* to send testers
- Debug APK from Drive (works, but not “Play beta”)  
- Unsigned release builds  

Use **Play internal testing** for a real store install experience.

---

## Checklist before first beta

- [ ] Play Console paid + active  
- [ ] Keystore + CREDENTIALS.txt backed up offline  
- [ ] `bundleRelease` produced `app-release.aab`  
- [ ] Privacy policy URL opens  
- [ ] Data safety form saved  
- [ ] Internal release uploaded + rolled out  
- [ ] Tester emails added  
- [ ] Opt-in link sent  

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| “You need to use a different package name” | `com.sandetay.harbor` already taken — change `applicationId` (rare) |
| Upload rejected: signing | Confirm release AAB, not debug |
| Testers don’t see app | Must open **opt-in link** first; wait for processing; same Google account |
| “Version code already used” | Increase `versionCode` |
| Missing privacy policy | URL must be public HTTPS |

---

*Related: [SHIPPING.md](./SHIPPING.md) · [PRIVACY.md](./PRIVACY.md)*
