# 04 — Ship Android

## Overview

Same web app (`index.html`) packaged with Capacitor into `android/`.

## Typical flow

```bash
cd /Users/brittany/Projects/Harbor
bash scripts/cap-prepare.sh
npx cap sync android
npx cap open android
```

Then build a signed release in Android Studio / Gradle and upload to **Play Console**.

## Docs

- [../shipping/PLAY-BETA.md](../shipping/PLAY-BETA.md)  
- [../shipping/SHIPPING.md](../shipping/SHIPPING.md)  

## Bookmarks

- [Play Console](https://play.google.com/console)  
- Internal testing link pattern: `https://play.google.com/apps/internaltest/...`  

## Notes

- Android does **not** use the iOS WidgetKit extension.  
- Keep privacy URL live: https://sandetay.github.io/Harbor/privacy.html  
