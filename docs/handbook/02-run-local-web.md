# 02 — Run Harbor locally (web)

Use this to see product changes instantly **without** Xcode.

## Prerequisites

- A terminal  
- Python 3 (already on macOS) **or** Node  

## Start a local server

```bash
cd /Users/brittany/Desktop/Harbor
python3 -m http.server 3000
```

Then open:

| Preview | URL |
|---------|-----|
| **Full app** | http://localhost:3000/index.html |
| **Phone frame** | http://localhost:3000/mobile.html |
| **Web + phone side-by-side** | http://localhost:3000/dual-preview.html |
| **Widgets mock (HTML)** | http://localhost:3000/widget-preview.html |

Stop the server with `Ctrl+C`.

## Rules

1. **Edit `index.html`** for almost all product work.  
2. Don’t rely on double-clicking the file — service worker and some APIs need `http://`.  
3. After big changes, hard-refresh (`Cmd+Shift+R`) so `sw.js` doesn’t show an old cache.  
4. Build number lives near the top of the app script: `HARBOR_BUILD_NUMBER`.

## Optional: Node scripts

```bash
cd /Users/brittany/Desktop/Harbor
npm install          # once
# cap scripts need Node; pure web preview does not
```

## Related

- [07-repo-file-map.md](./07-repo-file-map.md)  
- [06-troubleshooting.md](./06-troubleshooting.md)  
