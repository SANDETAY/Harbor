# Harbor session save — pick up later

**Saved:** 2026-07-10  
**Product version:** **0.9.3** (beta, pre-1.0)  
**Build:** **184** (`HARBOR_BUILD` / SW cache `harbor-preview-v184`)  
**Repo:** https://github.com/SANDETAY/Harbor  
**Local path:** `C:\Users\Taylor\Rythm`  
**Live PWA:** https://sandetay.github.io/Harbor/

## What’s in this save

| Area | Status |
|------|--------|
| Student status toggle → discounted sub prices | Done (v180) |
| Bills: weekly / biweekly / monthly / quarterly / yearly | Done (v180) |
| Multi pay-date bills: amount × days selected | Done (v180) |
| Product version **0.9.x** + subtle Today footer | Done (v181) |
| Menu **What’s New** / release notes viewer | Done (v181) |
| Smart Suggestions free time in **hours** (not minutes) | Done (v182) |
| Feedback: honest send status, queue + retry, mailto backup | Done (v182) |
| **Web3Forms** primary feedback email | Done (v183) |
| Summary KPI boxes open full Tasks / Events / Bills / Grocery lists | Done (v184) |
| Weekly chores visible mid-period (no vanish after add) | Done (v184) |
| Family event tags: name chip without extra swatch circle | Done (v184) |

### Feedback (important)

- **Primary:** Web3Forms access key in `FEEDBACK_CONFIG.web3formsAccessKey`  
- **Inbox:** `Taylorsanders12360@gmail.com`  
- **Fallbacks:** FormSubmit → mail app + local queue  
- Key is **public by design** (not a secret API key). Domain for forms: `sandetay.github.io`  
- Test after hard-refresh: Menu → Send Feedback → check Gmail (and spam)

### Versioning convention

| Layer | Value | Role |
|--------|--------|------|
| Product | `0.9.3` | User-facing semver (reserve `1.0.0` for store launch) |
| Build | `184` | Cache bust + support |
| Channel | `beta` | Until stable 1.0 |

## How to resume

```powershell
cd C:\Users\Taylor\Rythm
git pull origin main
# optional local server
# npm start
# or: python -m http.server 8765
```

In chat: **“Load harbor”** (or open this repo) and continue from this save.

Hard-refresh the live site (or reinstall PWA) so SW cache **`harbor-preview-v184`** loads. Footer / menu should show **Harbor 0.9.3**.

## Untracked local files (not committed)

- `Harbor-debug.apk` — Android debug build (keep local; don’t commit APKs)
- `package-lock.json` — optional to commit later
- `scripts/check-js-balance.py` — optional tidy

## Optional next session ideas

- Confirm Web3Forms test email lands after hard-refresh
- Ship more polish from device feedback
- Capacitor / TestFlight path when ready for stores
- Commit `package-lock.json` if you want reproducible npm installs

## Tag

Git tag: create `save/v0.9.3-184-2026-07-10` after push if you want a resume anchor
