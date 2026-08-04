# Harbor programming terms (beginner → advanced)

Words you’ll hear in Harbor, app stores, and with a coding agent.  
Skim the **Harbor-specific** notes; the rest is industry standard.

---

## A — App shell & shipping

| Term | Plain English | Harbor note |
|------|----------------|-------------|
| **PWA** | Progressive Web App — a website that can install and work offline-ish | Harbor’s core is a PWA (`index.html` + `sw.js`) |
| **Service worker** | Background script that caches files for offline / faster loads | `sw.js`; cache name must bump with builds |
| **Capacitor** | Toolkit that wraps a web app in a real iOS/Android app | Active: `ios/` + `capacitor.config.json`. Android parked in `_archive/android/` |
| **Native shell** | The thin real-app wrapper around the web UI | Xcode for iOS (Android Studio later) |
| **Bundle ID** | Unique app ID on Apple/Google | `com.sandetay.harbor` |
| **Marketing version** | User-facing version like `1.0.0` | “Product train” 1.0 |
| **Build number** | Integer that must increase every store upload | `HARBOR_BUILD_NUMBER` + Xcode `CURRENT_PROJECT_VERSION` |
| **Archive** | Xcode package ready to upload | Product → Archive |
| **TestFlight** | Apple’s beta install channel | Before App Store public |
| **App Store Connect** | Apple’s website for apps, builds, listings | Where uploads land |
| **Provisioning / signing** | Apple’s permission papers so a build can run on devices | Automatic signing with your team ID is fine for most Harbor work |
| **Entitlements** | Capabilities an app is allowed (App Groups, push, etc.) | Widgets need App Group |
| **App Group** | Shared storage between app and extension | `group.com.sandetay.harbor` |
| **Extension** | Mini-app bundled with the main app | HarborWidgets |
| **Widget / WidgetKit** | Home Screen glance UI | SwiftUI under `HarborWidgets/` |
| **Timeline** | How often WidgetKit refreshes entries | Provider in widget code |
| **Snapshot (widget)** | JSON picture of app state for widgets | Written by `HarborWidgetsPlugin` |
| **Deep link / URL scheme** | Custom link that opens the app | `com.sandetay.harbor://auth/callback` |
| **IPA** | iOS app package file | Produced by archive/export |
| **APK / AAB** | Android package formats | Play prefers AAB |

---

## B — UI pieces (what users see)

| Term | Plain English | Harbor note |
|------|----------------|-------------|
| **Splash screen** | Logo/color shown while the app boots | Capacitor SplashScreen + native launch image |
| **Toast** | Small temporary message (bottom/top), auto-dismisses | e.g. “Undo” after completing a task |
| **Chip** | Small rounded tappable label/filter pill | Energy, filters, categories |
| **Pill** | Synonym for chip / rounded button | Same idea |
| **Modal / sheet** | Overlay panel on top of the page | Settings panels, confirm dialogs |
| **Dialog / alert** | Focused “are you sure?” box | Destructive confirms |
| **Banner** | Persistent or semi-persistent message strip | Renewal / status messages |
| **Empty state** | Screen when there’s no data yet | “All clear” friendly copy |
| **Skeleton** | Grey placeholder shapes while loading | Not heavily used in Harbor monolith |
| **Tab bar** | Bottom navigation between main sections | Task / Life / etc. |
| **Nav bar / header** | Top title + actions | Section titles |
| **FAB** | Floating Action Button — round + button | Quick-add patterns |
| **Badge** | Tiny count on an icon | Unread / due counts |
| **Avatar** | Circular user image/initials | Account surfaces |
| **Icon button** | Tap target that is only an icon | Needs accessibility label |
| **Hit target** | How big the tappable area is | Apple likes ~44pt |
| **Safe area** | Screen region not covered by notch/home indicator | Capacitor `contentInset` |
| **Dark mode** | Dark color scheme | System + Harbor themes |
| **Theme / palette** | Color set (mint, night…) | Product freemium notes |
| **Typography** | Fonts, sizes, weights | System fonts on widgets |
| **Divider** | Thin line between list sections | Widgets use low-opacity dividers |
| **Card** | Contained rounded block of content | Life tiles, day cards |
| **List row** | One line in a scrollable list | Tasks, grocery items |
| **Swipe action** | Slide a row to reveal Edit/Delete | Recipe book, etc. |
| **Pull to refresh** | Pull list down to reload | Web patterns vary |
| **Scroll snap** | Scroll stops at neat positions | Carousels |
| **Gesture** | Swipe, long-press, pinch | Native + web differ |
| **Haptics** | Tiny vibration feedback | Native only |
| **Focus state** | Outline when keyboard/controller focuses a control | A11y |
| **Disabled state** | Control visible but not tappable | Careful with greyed Sign in |

---

## C — Product / data concepts

| Term | Plain English | Harbor note |
|------|----------------|-------------|
| **Monolith** | One big file/app instead of many modules | Harbor UI is largely `index.html` |
| **localStorage** | Browser storage on device | Default Harbor data home |
| **Offline-first** | Works without network; cloud optional | Core product promise |
| **Sync** | Keep multiple devices same data | Future/backend phase |
| **Auth / authentication** | Prove who you are | Supabase + OAuth |
| **OAuth** | “Sign in with Apple/Google…” protocol | See `docs/auth/` |
| **Session** | Signed-in period | Tokens managed by Supabase client |
| **Anon key** | Public Supabase key safe for client apps | Still don’t commit secrets carelessly |
| **RLS** | Row Level Security — DB rules per user | Supabase Postgres |
| **Schema** | Database table design | `docs/supabase/schema*.sql` |
| **Edge function** | Small server function near the DB | Calendar OAuth functions |
| **Webhook** | Server calls your URL on an event | Optional advanced |
| **CRUD** | Create, Read, Update, Delete | Basic data ops |
| **Idempotent** | Safe to run twice with same result | Good API design |
| **Cache** | Stored copy for speed | Service worker + HTTP |
| **Hard refresh** | Reload ignoring cache | Cmd+Shift+R |
| **Regression** | Old bug returns after a change | Why checklists matter |
| **Smoke test** | Quick “does it basically work?” pass | Open app, add task, check widget |
| **QA** | Quality assurance / testing | You + TestFlight testers |
| **Telemetry / analytics** | Usage metrics | Harbor is privacy-first — be careful |
| **Feature flag** | Switch a feature on/off without re-ship | Sometimes env/config based |
| **Freemium** | Free tier + paid Pro | `docs/product/FREE-VS-PRO.md` |
| **Entitlement (IAP)** | What a paying user unlocked | Store subscriptions later |

---

## D — Web / code basics

| Term | Plain English |
|------|----------------|
| **HTML** | Structure of the page |
| **CSS** | Visual style |
| **JavaScript (JS)** | Behavior / logic |
| **DOM** | Browser’s live tree of page elements |
| **Event listener** | Code that runs on click/type/etc. |
| **Callback** | Function run when something finishes |
| **Promise / async / await** | Handling work that takes time |
| **JSON** | Text format for structured data |
| **API** | How two programs talk |
| **REST** | Common style of HTTP APIs |
| **Endpoint** | One API URL action |
| **HTTP status** | 200 ok, 401 auth, 404 missing, 500 server error |
| **CORS** | Browser rule about cross-site requests |
| **CDN** | Fast file hosting network |
| **Git** | Version history |
| **Commit** | A saved snapshot in Git |
| **Branch** | Parallel line of work |
| **PR (pull request)** | Propose merging a branch |
| **main / master** | Default branch |
| **Merge conflict** | Two edits clash |
| **.gitignore** | Files Git should not track (secrets!) |
| **npm** | Node package manager |
| **Dependency** | Library your app uses |
| **CLI** | Command-line interface (Terminal) |
| **Path / directory** | Folder location |
| **Repo** | Repository — project + Git history |
| **Lint** | Auto-check for code issues |
| **Build** | Compile/package for running or shipping |
| **Environment variable** | Config value outside code |
| **localhost** | Your own computer as a server |

---

## E — iOS / Swift (widgets & shell)

| Term | Plain English | Harbor note |
|------|----------------|-------------|
| **Swift** | Apple’s programming language | Widgets + plugins |
| **SwiftUI** | Declarative UI framework | Widget layouts |
| **Xcode** | Apple’s IDE | Archive here |
| **.xcworkspace** | Project + CocoaPods | Open this, not only `.xcodeproj` |
| **CocoaPods / Pods** | iOS dependency manager | Capacitor plugins |
| **Scheme** | Which target Xcode builds | Usually **App** |
| **Target** | One build product (App, Widgets) | Two targets for Harbor iOS |
| **Info.plist** | App metadata & permission strings | Location purpose, etc. |
| **SF Symbols** | Apple’s icon set | Widget icons |
| **System background** | Light/dark adaptive surface | Widget chrome |
| **content margins** | System padding inside widgets | We disable + use our own |
| **Bridge / plugin** | Code connecting web JS to native | `HarborWidgetsPlugin` |
| **CAPPlugin** | Capacitor plugin base class | Same |

---

## F — Backend words

| Term | Plain English |
|------|----------------|
| **Postgres** | Database engine Supabase uses |
| **SQL** | Language to query/change the database |
| **Migration** | Versioned DB change script |
| **JWT** | Signed token proving login |
| **Redirect URL** | Where OAuth sends the user back |
| **Client ID / secret** | OAuth app credentials |
| **CSP** | Content Security Policy (what scripts may run) |
| **Rate limit** | Cap on how many requests |
| **Backup** | Copy of data for recovery |

---

## G — Soft skills on a “team of one”

| Term | Plain English |
|------|----------------|
| **Runbook** | Step-by-step ops guide (our handbook) |
| **Source of truth** | The one place that’s correct | Projects/Harbor, not a random Desktop copy |
| **Single source of truth** | Same idea for data or docs |
| **Incident** | Something broken in production |
| **Rollback** | Go back to last good build |
| **Postmortem** | Calm write-up of what broke and fix |
| **Scope creep** | Features expanding past the goal |
| **MVP** | Minimum viable product |
| **DoD (definition of done)** | “Shipped” means what exactly? |

---

## Harbor cheat phrases

| You say | They mean |
|---------|-----------|
| “Bump the build” | Increase web + iOS build numbers |
| “Prepare and sync” | `cap-prepare` then `cap sync` |
| “Archive” | Xcode → TestFlight path |
| “Open the app once” | Force widget snapshot write |
| “Config local” | `docs/supabase/config.local.js` |
| “Monolith” | `index.html` is the product |

---

## Keep learning

- [../handbook/01-how-harbor-works.md](../handbook/01-how-harbor-works.md)  
- [../bookmarks/open-bookmarks.html](../bookmarks/open-bookmarks.html)  
- [MDN](https://developer.mozilla.org/) · [Capacitor](https://capacitorjs.com/docs) · [Supabase](https://supabase.com/docs)  
