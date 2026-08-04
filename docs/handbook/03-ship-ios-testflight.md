# 03 — Ship iOS / TestFlight

## Preferred command

Say **`Ship Harbor`** or **`/ship-harbor`**.

That runs the locked skill: prepare Desktop Harbor → archive → distribute to App Store Connect (TestFlight).

Skill file: `.grok/skills/ship-harbor/SKILL.md`

---

## What you’re doing

1. Copy web app into the iOS shell  
2. Archive in Xcode  
3. Upload to App Store Connect  
4. TestFlight installs on your iPhone  

## One-time setup

- Mac with **Xcode**  
- **Apple Developer Program** (~$99/year)  
- Bundle ID: `com.sandetay.harbor`  
- Widgets: `com.sandetay.harbor.widgets`  
- App Group: `group.com.sandetay.harbor`  

Deep detail: [../shipping/APP-STORE-IOS.md](../shipping/APP-STORE-IOS.md)

## Every TestFlight ship (checklist)

### 1) Bump build numbers

| Place | What |
|-------|------|
| `index.html` | `HARBOR_BUILD_NUMBER` (e.g. 458) |
| `sw.js` | `CACHE_NAME = 'harbor-v458'` |
| Xcode / pbxproj | `CURRENT_PROJECT_VERSION` (must be **higher** than last upload) |

### 2) Prepare web → native

```bash
cd /Users/brittany/Desktop/Harbor
bash scripts/cap-prepare.sh
npx cap sync ios
```

### 3) Re-register widgets plugin (if wiped)

Open `ios/App/App/capacitor.config.json` → `packageClassList` must include:

```json
"HarborWidgetsPlugin"
```

(`HarborBridgeViewController` also registers it — keep both healthy.)

### 4) Open Xcode

```bash
open ios/App/App.xcworkspace
```

Use the **workspace** (not `.xcodeproj`) so CocoaPods load.

### 5) Archive

1. Scheme: **App**  
2. Destination: **Any iOS Device**  
3. **Product → Archive**  
4. **Distribute App → App Store Connect → Upload**

### 6) After install on phone

1. Open Harbor once (so widgets get a snapshot)  
2. Long-press Home Screen → add Harbor widgets if missing  
3. Confirm Settings shows the new build number  

## Widgets path (professional)

| Piece | Path |
|-------|------|
| Widget UI (SwiftUI) | `ios/App/HarborWidgets/*.swift` |
| Plugin (write snapshot) | `ios/App/App/HarborWidgetsPlugin.swift` |
| HTML mock preview | `widget-preview.html` |

## Do not

- Run hard-reset deploy scripts that discard uncommitted work unless you mean it  
- Upload a **lower** CFBundleVersion than an existing TestFlight build  

## Related

- [../shipping/SHIPPING.md](../shipping/SHIPPING.md)  
- [06-troubleshooting.md](./06-troubleshooting.md)  
- [../bookmarks/BOOKMARKS.md](../bookmarks/BOOKMARKS.md)  
