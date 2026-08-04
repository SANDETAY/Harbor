# 07 — Repo file map

**Root:** `/Users/brittany/Desktop/Harbor`

Think in **layers**, not a random pile of files.

```
Harbor/
├── docs/                    ← YOU ARE HERE (ops + learning)
│   ├── START-HERE.md
│   ├── handbook/            ← how to run & ship
│   ├── bookmarks/           ← websites to bookmark
│   ├── glossary/            ← terms (chip, toast, splash…)
│   ├── product/             ← product rules
│   ├── shipping/            ← store docs
│   ├── auth/                ← OAuth / sign-in docs
│   ├── supabase/            ← SQL + edge functions + local config
│   ├── backend/             ← backend overview
│   └── archive/             ← old notes
│
├── index.html               ← MAIN APP (edit product here)
├── sw.js                    ← service worker / offline cache
├── manifest.webmanifest     ← PWA install metadata
├── privacy.html             ← privacy policy page
├── mobile.html              ← phone-frame preview shell
├── dual-preview.html        ← web + phone preview
├── widget-preview.html      ← HTML mock of iOS widgets
│
├── js/
│   └── harbor-cloud.js      ← Supabase client helper
│
├── scripts/                 ← prepare, patch, ship helpers
│   ├── cap-prepare.sh       ← Mac: copy web → native-www
│   └── …
│
├── capacitor.config.json    ← Capacitor app id & plugins
├── package.json             ← npm scripts + Capacitor deps
│
├── native-www/              ← generated web copy for native (don’t hand-edit)
├── ios/                     ← Xcode / App Store (active)
│   └── App/
│       ├── App/             ← main iOS app (bridge, plugin)
│       ├── HarborWidgets/   ← home screen widgets
│       ├── App.xcworkspace  ← OPEN THIS in Xcode
│       └── Podfile
├── private/                 ← secrets (never commit)
├── _archive/                ← android + history + prototypes
│
├── build/                   ← export artifacts (archives, ipa helpers)
├── .github/                 ← CI / Pages deploy
└── README.md                ← short public intro → points here
```

## “I need to change…”

| Goal | Open |
|------|------|
| Button / screen / logic | `index.html` |
| Offline cache version | `sw.js` + build number in `index.html` |
| App icon / splash art | root `harbor-*.png` + `ios/.../Assets` |
| Widget look | `ios/App/HarborWidgets/*.swift` |
| Widget data bridge | `ios/App/App/HarborWidgetsPlugin.swift` |
| Cloud keys | `docs/supabase/config.local.js` |
| Database tables | `docs/supabase/schema*.sql` |
| Sign-in providers | `docs/auth/AUTH-PROVIDERS.md` + consoles |
| TestFlight steps | `docs/handbook/03-ship-ios-testflight.md` |

## Generated / don’t treat as source

| Path | Why |
|------|-----|
| `native-www/` | Output of `cap-prepare` |
| `ios/App/App/public/` | Copy from sync |
| `node_modules/` | npm packages |
| `ios/App/Pods/` | CocoaPods |

## Build artifacts

`build/ios-export-*` — past export folders. Safe to keep for history; not required to run.
