# 06 — Troubleshooting

## Quick triage

| What feels wrong | Start here |
|------------------|------------|
| UI change not on phone | Build number? TestFlight install? Hard refresh? |
| Widgets ugly / missing | Widget sources + Archive; open app once |
| Can’t sign in | `config.local.js` + Supabase redirects |
| Local preview old | Service worker cache (`sw.js`) |
| Xcode pod / sync errors | Use `.xcworkspace`, re-run `pod install` |

---

## Web / PWA

**Old UI after edit**  
- Hard refresh `Cmd+Shift+R`  
- Bump `HARBOR_BUILD_NUMBER` + `sw.js` `CACHE_NAME`  
- Application tab → Clear site data (browser)

**localhost won’t load**  
- Server running from **repo root**?  
- Correct port URL?

---

## iOS / TestFlight

**“I didn’t get the update”**  
- App Store Connect → TestFlight → build processed?  
- Phone on the right tester group?  
- Build number **higher** than previous upload?

**Widgets missing**  
- Extension embedded in App target?  
- Open Harbor once after install  
- Re-add widget from widget gallery  

**Widgets look wrong**  
- Sources under `ios/App/HarborWidgets/` (theme + `contentMarginsDisabled`)  
- Preview mock: `widget-preview.html`  
- Rebuild / Archive after Swift changes  

**Sign-in button does nothing**  
- `docs/supabase/config.local.js` included via `cap-prepare`  
- `packageClassList` / bridge healthy  

**cap sync wiped plugin**  
- Re-add `HarborWidgetsPlugin` to `capacitor.config.json`  

---

## Backend

**Supabase “Invalid API key”**  
- Wrong project URL or key in `config.local.js`  

**OAuth redirect mismatch**  
- Supabase Redirect URLs must list every return URL (web + `com.sandetay.harbor://…`)  

**SQL / invite failures**  
- Run the matching file in `docs/supabase/FIX-*.sql`  

---

## Git / two folders

You may have had **Desktop/Harbor** and **Projects/Harbor**.  
**Use Projects as source of truth.** Two diverging trees cause “I fixed it but the build doesn’t have it.”

---

## Still stuck?

1. Note **build number** (Settings in-app)  
2. Note **where** (web / Simulator / TestFlight)  
3. Note **exact symptom**  
4. Open the matching handbook guide + bookmarks  

[../START-HERE.md](../START-HERE.md)
