# Harbor — START HERE

**Single home for Harbor:** `/Users/brittany/Desktop/Harbor`

Open this file whenever you need to run, ship, or troubleshoot Harbor.

| | |
|--|--|
| **This folder** | `/Users/brittany/Desktop/Harbor` |
| **Repo** | https://github.com/SANDETAY/Harbor |
| **Live PWA** | https://sandetay.github.io/Harbor/ |
| **Product version** | 1.0 |
| **Current build** | See `HARBOR_BUILD_NUMBER` in `index.html` (also `sw.js`) |

---

## What is Harbor?

Calm life app (tasks, Life, streaks, grocery, bills, calendar).

Ships two ways **now**:

1. **Web / PWA** — `index.html`  
2. **iOS** — Capacitor + widgets → TestFlight / App Store  

**Android is archived** under `_archive/android/` until you have a physical device.

Data is **on-device** by default. Cloud (Supabase) is optional via `docs/supabase/config.local.js`.

---

## Folder map

| Folder | What |
|--------|------|
| [**handbook/**](./handbook/) | How to **run** Harbor (local, iOS, backend, troubleshoot) |
| [**bookmarks/**](./bookmarks/) | Websites to bookmark |
| [**glossary/**](./glossary/) | Chips, toast, splash, build numbers… |
| [**product/**](./product/) | Product rules |
| [**shipping/**](./shipping/) | TestFlight / App Store |
| [**auth/**](./auth/) | Sign-in providers, calendar OAuth |
| [**supabase/**](./supabase/) | SQL, edge function sources, **config.local.js** |
| [**backend/**](./backend/) | Backend overview |
| [**archive/**](./archive/) | Old notes |
| **`../private/`** | Secrets (never commit) |
| **`../_archive/`** | Android + old prototypes/history |
| **`../ios/`** | Xcode project — open `ios/App/App.xcworkspace` |
| **`../index.html`** | The app UI (edit here) |

---

## Do this first

### A) Run web locally

```bash
cd /Users/brittany/Desktop/Harbor
python3 -m http.server 3000
```

→ http://localhost:3000/index.html  
→ http://localhost:3000/widget-preview.html  

### B) Ship TestFlight

**Command (preferred):** say **`Ship Harbor`** or run **`/ship-harbor`**

That locks the full process: bump build → prepare → archive → distribute to App Store Connect / TestFlight.

Manual checklist: [handbook/03-ship-ios-testflight.md](./handbook/03-ship-ios-testflight.md)

```bash
cd /Users/brittany/Desktop/Harbor
bash scripts/cap-prepare.sh
npx cap sync ios
# ensure HarborWidgetsPlugin in ios/App/App/capacitor.config.json packageClassList
open ios/App/App.xcworkspace
```

### C) Cloud / login broken

[handbook/05-backend-and-cloud.md](./handbook/05-backend-and-cloud.md)  
[bookmarks/open-bookmarks.html](./bookmarks/open-bookmarks.html)

### D) Something broke

[handbook/06-troubleshooting.md](./handbook/06-troubleshooting.md)

---

## Golden rules

1. Edit product UI in **`index.html`** only.  
2. Ship: bump `HARBOR_BUILD_NUMBER` + `sw.js` cache + Xcode build number.  
3. After `cap sync`, keep **`HarborWidgetsPlugin`** in `packageClassList`.  
4. Never commit **`private/`** or **`config.local.js`**.  
5. One home only: **Desktop Harbor** — do not keep a second full copy under Projects.

---

## Learn Harbor

1. [handbook/01-how-harbor-works.md](./handbook/01-how-harbor-works.md)  
2. [handbook/07-repo-file-map.md](./handbook/07-repo-file-map.md)  
3. [glossary/harbor-programming-terms.md](./glossary/harbor-programming-terms.md)  
4. [bookmarks/open-bookmarks.html](./bookmarks/open-bookmarks.html)  
