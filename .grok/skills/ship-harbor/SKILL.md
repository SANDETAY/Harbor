---
name: ship-harbor
description: >
  App-only: archive Harbor in Xcode and upload to App Store Connect for TestFlight.
  Use when the user says "Ship Harbor", "ship harbor", "Ship Harbor to TestFlight", "archive and
  distribute Harbor", "upload Harbor to App Store Connect", or runs /ship-harbor.
  Single home is always ~/Desktop/Harbor. Does NOT deploy the website (harborlife.app / GitHub Pages).
  Prepares web assets into the native shell, bumps app build if needed, archives, and uploads for TestFlight.
---

# Ship Harbor (app / TestFlight only)

**Trigger phrases:** `Ship Harbor`, `/ship-harbor`, ship to TestFlight, archive + distribute Harbor.

## Scope (critical)

| In scope | Out of scope |
|----------|----------------|
| iOS Capacitor app | **Website** (`harborlife.app`, GitHub Pages) |
| `cap prepare` / `cap sync ios` → `native-www` + Xcode | Pushing `main` for Pages deploy |
| Archive → App Store Connect → **TestFlight** | Android / Play (parked) |

**Ship Harbor means the phone app only.** Brittany’s **website** work is separate — never treat “Ship Harbor” as a web deploy. Copying `index.html` into the app shell for the archive is expected; that is not publishing the live site.

When this skill is invoked, **execute the full app ship** (do not only print the checklist) unless the user said “dry run” or “don’t upload yet”.

## Absolute home (never use Projects)

```text
/Users/brittany/Desktop/Harbor
```

- Open Xcode via: `ios/App/App.xcworkspace` (workspace only, not `.xcodeproj`)
- Bundle ID: `com.sandetay.harbor`
- Widgets: `com.sandetay.harbor.widgets`
- App Group: `group.com.sandetay.harbor`

## Goal

1. Prepare Desktop Harbor for a store build  
2. **Archive** (Release, Any iOS Device)  
3. **Distribute / upload** to **App Store Connect** (TestFlight path)  
4. Report build number + next human steps (install on phone, open app once for widgets)

## Before you start

1. Confirm working directory is `/Users/brittany/Desktop/Harbor` (or `cd` there for all commands).  
2. Confirm `ios/App/App.xcworkspace` exists.  
3. Note current `HARBOR_BUILD_NUMBER` in `index.html` and `CURRENT_PROJECT_VERSION` in `ios/App/App.xcodeproj/project.pbxproj`.  
4. If the user already specified a build number, use it; otherwise **bump both web and iOS build numbers by +1** so App Store Connect accepts the upload (must exceed last uploaded CFBundleVersion).

## Procedure (do these in order)

### 1) Bump build numbers (same integer everywhere)

| Place | Field |
|-------|--------|
| `index.html` | `const HARBOR_BUILD_NUMBER = N;` |
| `sw.js` | `const CACHE_NAME = 'harbor-vN';` |
| `ios/App/App.xcodeproj/project.pbxproj` | every `CURRENT_PROJECT_VERSION = N;` (App + HarborWidgets Debug/Release) |

`MARKETING_VERSION` stays on the product train (usually `1.0.0`) unless the user asks to change it.

### 2) Prepare web → native

```bash
cd /Users/brittany/Desktop/Harbor
bash scripts/cap-prepare.sh
npx cap sync ios
```

### 3) Widgets plugin must stay registered

After sync, ensure `ios/App/App/capacitor.config.json` → `packageClassList` includes:

```json
"HarborWidgetsPlugin"
```

Re-add if wiped. `HarborBridgeViewController` should still register the plugin type.

### 4) Archive

Prefer CLI when possible (less manual clicking):

```bash
cd /Users/brittany/Desktop/Harbor/ios/App
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -archivePath "$HOME/Library/Developer/Xcode/Archives/Harbor/Harbor-N.xcarchive" \
  clean archive \
  DEVELOPMENT_TEAM=4AY5ZRN2R7 \
  -allowProvisioningUpdates
```

Notes:

- Use the real team ID from the pbxproj if different (`DEVELOPMENT_TEAM`).  
- Create parent Archives dir if missing.  
- If signing fails, open the workspace and fix signing, then retry — do not invent certificates.

If CLI archive is blocked, open Xcode and complete **Product → Archive**:

```bash
open /Users/brittany/Desktop/Harbor/ios/App/App.xcworkspace
```

Scheme **App**, destination **Any iOS Device (arm64)**.

### 5) Distribute → App Store Connect (upload)

Preferred export/upload when altool/notary or export options work. Typical path:

```bash
# After successful .xcarchive exists:
xcodebuild -exportArchive \
  -archivePath "$HOME/Library/Developer/Xcode/Archives/Harbor/Harbor-N.xcarchive" \
  -exportOptionsPlist /Users/brittany/Desktop/Harbor/.grok/skills/ship-harbor/references/ExportOptions-AppStore.plist \
  -exportPath "$HOME/Library/Developer/Xcode/Archives/Harbor/export-N" \
  -allowProvisioningUpdates
```

Then upload the IPA (example with `xcrun altool` or Transporter / `xcrun notarytool` equivalents as available on the Mac). On modern Xcode, **Organizer → Distribute App → App Store Connect → Upload** is valid if CLI upload is not configured.

**User-visible requirement:** if Apple ID / 2FA / App Store Connect login is required, **pause and ask the user** to complete auth — then continue.

Never use a lower build number than a build already on App Store Connect.

### 6) Confirm success

Tell the user:

1. Build **N** uploaded (or archive path if upload needs their click)  
2. Wait for App Store Connect processing  
3. On phone: TestFlight → install Harbor  
4. Open Harbor once (widget snapshot)  
5. Confirm Settings shows build **N**

## Safety rules

- **Do not** deploy GitHub Pages / harborlife.app as part of Ship Harbor (app-only).  
- **Do not** run hard-reset / git wipe scripts as part of ship.  
- **Do not** delete `private/` or `docs/supabase/config.local.js`.  
- **Do not** ship from any path except Desktop Harbor.  
- Prefer confirming before a destructive clean if the tree looks unexpected.  
- If `config.local.js` is missing, warn that cloud sign-in may be off in the build — still ship unless user aborts.

## Reference docs (read if stuck)

- `docs/handbook/03-ship-ios-testflight.md`  
- `docs/shipping/APP-STORE-IOS.md`  
- `docs/START-HERE.md`  

## Done definition

Harbor **app** is shipped when an archive for build **N** has been **uploaded to App Store Connect** for TestFlight (or the user has Organizer open on a successful archive with clear “click Upload” if auth blocked you). Partial prepare without archive is **not** done. Website status is irrelevant to this skill.
