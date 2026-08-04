# 08 — Daily ops checklist

## Before coding

- [ ] Working folder is **`/Users/brittany/Desktop/Harbor`**  
- [ ] Know whether you’re changing **web**, **iOS widgets**, or **backend**  
- [ ] Android is **out of scope** for now (`_archive/android/`)  

## After product UI change (web only)

- [ ] Preview on http://localhost:3000/index.html  
- [ ] Check mobile frame if layout-sensitive  
- [ ] Hard refresh if UI looks stale  

## Before any TestFlight upload

- [ ] Bump `HARBOR_BUILD_NUMBER`  
- [ ] Bump `sw.js` cache name to match  
- [ ] Bump iOS `CURRENT_PROJECT_VERSION` **above** last upload  
- [ ] `bash scripts/cap-prepare.sh`  
- [ ] `npx cap sync ios`  
- [ ] `HarborWidgetsPlugin` still in `packageClassList`  
- [ ] Archive from **App.xcworkspace**  
- [ ] Upload → wait for processing → install → open app once  

## After ship

- [ ] Confirm in-app build number  
- [ ] Spot-check: tasks, sign-in (if cloud), one widget  
- [ ] Note anything broken in a short list for next session  

## Weekly (when cloud is live)

- [ ] Supabase project healthy (Dashboard)  
- [ ] Auth providers still enabled  
- [ ] Privacy URL still loads  

## Bookmarks to keep in a browser folder

Open [../bookmarks/open-bookmarks.html](../bookmarks/open-bookmarks.html) once and **bookmark each link** into a Chrome/Safari folder named **Harbor**.
