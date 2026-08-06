# Harbor session pointer

**Single home:** `/Users/brittany/Desktop/Harbor`

→ **[docs/START-HERE.md](docs/START-HERE.md)**

| | |
|--|--|
| **Ship app → TestFlight** | Say **`Ship Harbor`** or `/ship-harbor` — **app only** (Xcode archive → App Store Connect). **Not** the website. |
| Xcode | `open ios/App/App.xcworkspace` |
| Bookmarks | [docs/bookmarks/open-bookmarks.html](docs/bookmarks/open-bookmarks.html) |
| Glossary | [docs/glossary/harbor-programming-terms.md](docs/glossary/harbor-programming-terms.md) |
| Secrets | `private/` (not in git) |
| Android | `_archive/android/` (parked) |

### Language: **Taskers**
**Taskers** = tasks + habits + chores (anything on the Task list).  
If Brittany says “Taskers,” change **all three** unless she names only one kind.

### Language: **website** vs **app** (do not mix)
| She says | Scope | Meaning |
|----------|--------|---------|
| **website** | Web only | Changes for the live site (`harborlife.app` / PWA web). Prefer web-only paths, CSS/JS gates for `!isHarborNativeApp()`, docs/deploy for Pages — **do not** ship TestFlight-only / native package churn. |
| **app** | Native only | Changes for the iPhone (Capacitor / TestFlight / App Store). Prefer native gates, `ios/`, `native-www` via ship pipeline — **do not** treat as a website-only deploy. |

**Conflict rule:** Do not apply website work into the app binary (or app work into the live site) unless she explicitly says **both**, **everywhere**, or names both surfaces. Shared `index.html` is one codebase — use platform checks / separate files so web and native don’t fight each other.

**`Ship Harbor` / `/ship-harbor`:** **App only** — prepare → Xcode archive → upload → TestFlight. Never means deploy `harborlife.app` / GitHub Pages.
