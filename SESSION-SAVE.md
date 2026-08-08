# Harbor session pointer

**Single home:** `/Users/brittany/Desktop/Harbor`

→ **[docs/START-HERE.md](docs/START-HERE.md)**

---

## ACTIVE MODE (until Brittany says otherwise)

| Rule | Meaning |
|------|---------|
| **TestFlight app only** | All product work is for the **iOS app** (Capacitor / TestFlight / App Store Connect). |
| **Website frozen** | Do **not** update, deploy, or co-ship `harborlife.app` / GitHub Pages. Live site stays as-is. |
| **No cojoining** | App changes do **not** get paired with website deploys. Shared `index.html` edits are for the **app binary** only until freeze lifts. |
| **No Android** | Android CI removed. Android stays parked under `_archive/android/` — do not restore workflows or build Android. |

| | |
|--|--|
| **Ship app → TestFlight** | Say **`Ship Harbor`** or `/ship-harbor` — **app only** (Xcode archive → App Store Connect). **Not** the website. |
| Xcode | `open ios/App/App.xcworkspace` |
| Bookmarks | [docs/bookmarks/open-bookmarks.html](docs/bookmarks/open-bookmarks.html) |
| Glossary | [docs/glossary/harbor-programming-terms.md](docs/glossary/harbor-programming-terms.md) |
| Secrets | `private/` (not in git) |
| Android | **Removed from CI.** Archive only: `_archive/android/` (do not revive) |

### Language: **Taskers**
**Taskers** = tasks + habits + chores (anything on the Task list).  
If Brittany says “Taskers,” change **all three** unless she names only one kind.

### Language: **website** vs **app** (do not mix)
| She says | Scope | Meaning |
|----------|--------|---------|
| **website** | Web only | **FROZEN** — do not change or deploy until she unfreezes. |
| **app** | Native only | **Active path** — iPhone / Capacitor / TestFlight / App Store. |

**Conflict rule:** Website is frozen. Default every request to **app / TestFlight** unless she explicitly unfreezes the website or says **both**.

**`Ship Harbor` / `/ship-harbor`:** **App only** — prepare → Xcode archive → upload → TestFlight. Never means deploy `harborlife.app` / GitHub Pages.
