# Harbor session pointer

**Single home:** `/Users/brittany/Desktop/Harbor`

→ **[docs/START-HERE.md](docs/START-HERE.md)**

---

## ACTIVE MODE (until Brittany says otherwise)

| Rule | Meaning |
|------|---------|
| **Preview in `mobile.html`** | Day-to-day checks: local server → **http://localhost:3000/mobile.html**. Edit product UI in **`index.html`** (mobile frame loads it). |
| **Ship app on “archive” / Ship Harbor** | Xcode archive → TestFlight when she says **archive** or **Ship Harbor**. |
| **Website live** | `harborlife.app` / GitHub Pages deploys on push to `main` (unfrozen 2026-08-12). |
| **No Android** | Android CI removed. Android stays parked under `_archive/android/` — do not restore workflows or build Android. |

| | |
|--|--|
| **Ship app → TestFlight** | Say **`Ship Harbor`** or `/ship-harbor` — **app only** (Xcode archive → App Store Connect). |
| **Ship website** | Push to `main` (or workflow_dispatch **Deploy GitHub Pages**). |
| Xcode | `open ios/App/App.xcworkspace` |
| Bookmarks | [docs/bookmarks/open-bookmarks.html](docs/bookmarks/open-bookmarks.html) |
| Glossary | [docs/glossary/harbor-programming-terms.md](docs/glossary/harbor-programming-terms.md) |
| Secrets | `private/` (not in git) |
| Android | **Removed from CI.** Archive only: `_archive/android/` (do not revive) |
| **Current ship train** | Product **1.0** · build **587** (TestFlight + web) |

### Language: **Taskers**
**Taskers** = tasks + habits + chores (anything on the Task list).  
If Brittany says “Taskers,” change **all three** unless she names only one kind.

### Language: **website** vs **app** (do not mix)
| She says | Scope | Meaning |
|----------|--------|---------|
| **website** | Web only | Live PWA — deploy via `main` / Pages. |
| **app** | Native only | iPhone / Capacitor / TestFlight / App Store. |
| **both** / **Ship Harbor + website** | App + web | Archive app **and** push/deploy Pages. |

**`Ship Harbor` / `/ship-harbor`:** **App only** — prepare → Xcode archive → upload → TestFlight. Does **not** deploy the website by itself; push `main` for the site.
