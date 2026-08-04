# Android — archived (on ice)

**Status:** Parked until you have a physical Android device to validate Play / Android Studio.

Harbor ships **web (PWA) + iOS (TestFlight / App Store)** for now. Nothing here is required for day-to-day Harbor work.

## What’s in this folder

| Path | What it is |
|------|------------|
| `android-project/` | Former repo-root `android/` Capacitor project |
| `docs/PLAY-BETA.md` | Play Console beta guide |
| `docs/04-ship-android.md` | Short ship runbook |
| `scripts/create-android-keystore.ps1` | Keystore helper |
| `github-workflows/build-android-apk.yml` | CI workflow that built debug APKs |

## When you’re ready to restore

From the **Harbor repo root** (`/Users/brittany/Projects/Harbor`):

```bash
# 1) Put the project back
mv _archive/android/android-project android

# 2) Optional: restore docs into the live handbook/shipping tree
mv _archive/android/docs/PLAY-BETA.md docs/shipping/PLAY-BETA.md
mv _archive/android/docs/04-ship-android.md docs/handbook/04-ship-android.md

# 3) Optional: restore keystore script + CI
mv _archive/android/scripts/create-android-keystore.ps1 scripts/
mv _archive/android/github-workflows/build-android-apk.yml .github/workflows/

# 4) Sync native project
bash scripts/cap-prepare.sh
npx cap sync android
npx cap open android
```

Also re-enable `cap:android` in `package.json` if you removed or commented it.

## Why archive instead of delete

So you can revive Play shipping later without rebuilding Capacitor Android from scratch.
