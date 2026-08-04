# Harbor TestFlight build 414 — internal

**Date:** 2026-07-29  
**Marketing version:** 1.0.0  
**iOS build (`CURRENT_PROJECT_VERSION`):** 414  
**In-app (`HARBOR_BUILD_NUMBER`):** 414  

## What’s in this build
- Local-first Harbor web shell (Capacitor iOS)
- Pro sandbox + cloud backup/restore (Supabase publishable key in app)
- Household C1: invite / join / leave / link person tags
- Display name (C1b)
- Device calendars (EventKit) on phone
- ICS file import + URL feeds (no Google OAuth yet — paused)

## Explicitly not in this build
- Google / Outlook OAuth calendars (paused)
- C2 shared tasks
- Budget sharing
- Android packaging (removed from tree for cleanliness; re-add with Capacitor if needed)

## Security pass (pre-ship)
| Check | Result |
|--------|--------|
| No `service_role` in client | Pass |
| Household writes via RPC only | Pass (server SQL) |
| Invite tokens hashed server-side | Pass |
| `profiles.is_pro` not client-writable | Pass (C1 trigger) |
| Publishable key in client | Expected for Supabase |
| `config.local.js` gitignored | Yes — still **bundled into native-www** for TestFlight cloud |

## Archive in Xcode
1. `cd ~/Desktop/Harbor`
2. `npm install` (if needed)
3. `bash scripts/cap-prepare.sh && npx cap sync ios`
4. `cd ios/App && pod install && cd ../..`
5. Open **`ios/App/App.xcworkspace`** (not `.xcodeproj`)
6. Target **Any iOS Device (arm64)**
7. Signing: your Team, bundle `com.sandetay.harbor`
8. **Product → Archive** → Distribute → App Store Connect → Upload
9. TestFlight → Internal testing

## Tester notes
- Enable **Harbor Pro (sandbox)** under Advanced to try Budget, themes, cloud, family link
- Cloud needs network + Supabase project already configured
- Two accounts needed to test household invite
