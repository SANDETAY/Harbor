# Harbor session save — pick up tonight

**Saved:** 2026-07-09  
**Build:** v118  
**Commit:** `edf103e` on `main` (pushed to `origin/main`)  
**Repo:** https://github.com/SANDETAY/Harbor  
**Local path:** `C:\Users\Taylor\Rythm`

## What’s in this save

| Area | Status |
|------|--------|
| Add Event → **Add person** chip + manage household | Done |
| Add Event scroll / custom duration reachable | Done |
| Splash bottom black bar → mint `#d8e4de` match | Done |
| Sim tests (27 passed) + push | Done |

## How to resume

```powershell
cd C:\Users\Taylor\Rythm
git pull origin main
# optional local server
# powershell -File scripts\start-server.ps1
# or: python -m http.server 8765
```

Hard-refresh or reinstall PWA so SW cache `harbor-preview-v118` loads.

## Quick product notes (for you)

- **More users to schedule for:** Schedule → Add Event → **Who is this for?** → **Add person** (or manage household).
- **Custom duration:** Scroll the event sheet body; footer stays sticky.
- **Splash:** Underlay + fixed full-viewport splash; no black home-indicator strip.

## Next session ideas (optional)

- Anything you still notice on device after hard refresh
- Tidy/remove untracked `scripts/check-js-balance.py` if not needed
- Bump build when you ship the next batch of UI fixes

## Tag

Git tag: `save/v118-2026-07-09` (points at this commit)
