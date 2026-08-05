# Harbor — all critical URLs

Bookmark these. Group names match a professional ops folder.

---

## 1. Product & code

| Name | URL | Why |
|------|-----|-----|
| **GitHub repo** | https://github.com/SANDETAY/Harbor | Source, PRs, issues |
| **Live PWA** | https://harborlife.app/ | Public web app / tester link |
| **Privacy policy (live)** | https://harborlife.app/privacy.html | Store listing + in-app |
| **GitHub Pages settings** | https://github.com/SANDETAY/Harbor/settings/pages | If deploy 404s |
| **Actions (deploys)** | https://github.com/SANDETAY/Harbor/actions | CI / Pages workflow status |

Local (not bookmarks, but memory):

- Project: `/Users/brittany/Desktop/Harbor`  
- Local app: http://localhost:3000/index.html  
- Widget mock: http://localhost:3000/widget-preview.html  

---

## 2. Apple (iOS / TestFlight / App Store)

| Name | URL | Why |
|------|-----|-----|
| **Apple Developer** | https://developer.apple.com/ | Certificates, identifiers, devices |
| **Developer Program** | https://developer.apple.com/programs/ | Membership status |
| **App Store Connect** | https://appstoreconnect.apple.com/ | Builds, TestFlight, listing, reviews |
| **Certificates, IDs & Profiles** | https://developer.apple.com/account/resources/identifiers/list | Bundle IDs, App Groups, capabilities |
| **TestFlight (on phone)** | App Store app → TestFlight | Install betas |
| **Human Interface Guidelines** | https://developer.apple.com/design/human-interface-guidelines/ | Design reference |
| **WidgetKit docs** | https://developer.apple.com/documentation/widgetkit | Widget API reference |

**IDs to remember**

- App: `com.sandetay.harbor`  
- Widgets: `com.sandetay.harbor.widgets`  
- App Group: `group.com.sandetay.harbor`  

---

## 3. Google (Sign in with Google)

| Name | URL | Why |
|------|-----|-----|
| **Google Cloud Console** | https://console.cloud.google.com/ | OAuth client for Google sign-in |
| **Google Auth Platform / credentials** | https://console.cloud.google.com/apis/credentials | Client ID + secret |

**Play Console** (Android store) is optional for now — Android platform is archived under `_archive/android/`. Bookmark later if you revive Play: https://play.google.com/console

---

## 4. Backend — Supabase

| Name | URL | Why |
|------|-----|-----|
| **Supabase Dashboard** | https://supabase.com/dashboard | Projects list |
| **Your project (if still this ref)** | https://supabase.com/dashboard/project/dyaicsnoefkfshesyogk | Tables, auth, SQL |
| [**Auth providers**](https://supabase.com/dashboard/project/dyaicsnoefkfshesyogk/auth/providers) | https://supabase.com/dashboard/project/dyaicsnoefkfshesyogk/auth/providers | Apple / Google / Email (Azure off) |
| **URL configuration** | https://supabase.com/dashboard/project/dyaicsnoefkfshesyogk/auth/url-configuration | Site URL + redirects |
| **SQL Editor** | https://supabase.com/dashboard/project/dyaicsnoefkfshesyogk/sql/new | Run schema / FIX scripts |
| **API settings** | https://supabase.com/dashboard/project/dyaicsnoefkfshesyogk/settings/api | Project URL + anon key |
| **Edge Functions** | https://supabase.com/dashboard/project/dyaicsnoefkfshesyogk/functions | Calendar OAuth functions |
| **Supabase docs** | https://supabase.com/docs | Official reference |
| **Auth callback (this project)** | https://dyaicsnoefkfshesyogk.supabase.co/auth/v1/callback | Paste into Google Cloud + Apple Developer |

If the project ref changes, replace `dyaicsnoefkfshesyogk` everywhere and update `config.local.js`.

---

## 5. Capacitor & web tech (reference)

| Name | URL | Why |
|------|-----|-----|
| **Capacitor docs** | https://capacitorjs.com/docs | Native shell |
| **Capacitor iOS** | https://capacitorjs.com/docs/ios | iOS specifics |
| **MDN Web Docs** | https://developer.mozilla.org/ | HTML/JS/CSS reference |
| **Can I use** | https://caniuse.com/ | Browser feature support |

---

## 6. Optional hosting

| Name | URL | Why |
|------|-----|-----|
| **Netlify Drop** | https://app.netlify.com/drop | Fast static host without Git |
| **Netlify dashboard** | https://app.netlify.com/ | If you use Netlify long-term |

---

## 7. Support / legal you publish

| Name | URL |
|------|-----|
| Privacy | https://sandetay.github.io/Harbor/privacy.html |
| Support email | *(your real inbox — put it here when fixed)* |

---

## Deep link schemes (not websites, but critical)

```
com.sandetay.harbor://auth/callback
Harbor://
capacitor://localhost
```

These must appear in **Supabase → Auth → Redirect URLs** for native login.
