# Harbor — Sign in with Apple, Google, or email

Users can create a Harbor cloud account with **Apple**, **Google**, or **email + password**.

**Microsoft / Azure account sign-in is not offered** (disabled in product and Supabase).

**In-app:** Menu → **Account & cloud** → Continue with Apple / Google, or email  
**Code:** `HarborCloud.signInWithOAuth('apple' | 'google')`

Leave **Azure**, **SAML**, and **Web3** off.

---

## 1. Supabase — Site URL & redirects

**Authentication → URL configuration**

| Field | Example |
|-------|---------|
| **Site URL** | Your live app URL, e.g. `https://sandetay.github.io/Harbor/` or local `http://localhost:3000` |
| **Redirect URLs** | Add every place users return after login |

Add all of these that you use:

```text
http://localhost:3000/**
http://127.0.0.1:3000/**
http://localhost:5500/**
https://YOUR_PRODUCTION_DOMAIN/**
https://YOUR_PRODUCTION_DOMAIN/index.html
```

**Required for TestFlight / native app (especially Google):**

```text
com.sandetay.harbor://auth/callback
com.sandetay.harbor://**
Harbor://**
capacitor://localhost
capacitor://localhost/**
```

Google blocks login inside the app WebView. Harbor opens Safari (Browser plugin) and returns via  
`capacitor://localhost` (or the custom scheme). If those redirect URLs are missing, **Apple may still work** while Google fails to return to the app.

Build **443+** registers URL schemes in Info.plist (`com.sandetay.harbor`, `Harbor`, `capacitor`).

Copy the **Callback URL** shown on each provider page in Supabase (looks like):

```text
https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback
```

You’ll paste that into Google Cloud and Apple Developer as the authorized redirect.

---

## 2. Enable providers

### Google

1. [Google Cloud Console](https://console.cloud.google.com/) → create/select a project.  
2. **APIs & Services → OAuth consent screen** → External (or Internal).  
3. **Credentials → Create credentials → OAuth client ID → Web application** (not iOS).  
4. **Authorized redirect URIs** → paste Supabase callback:  
   `https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback`  
5. **Authorized JavaScript origins** (no path):  
   `https://YOUR_PROJECT_REF.supabase.co` and `http://localhost:3000`  
6. Copy **Client ID** + **Client secret**.  
7. Supabase → **Authentication → Providers → Google** → Enable → paste ID + secret → Save.

### Apple (required if you ship social login on the App Store)

1. [Apple Developer](https://developer.apple.com/) → **Certificates, Identifiers & Profiles**.  
2. **Identifiers → Services IDs** → register a Services ID (e.g. `com.sandetay.harbor.auth`).  
3. Enable **Sign in with Apple** → Configure:  
   - Domains: your Supabase domain `YOUR_PROJECT_REF.supabase.co`  
   - Return URL: `https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback`  
4. Create a **Key** with Sign in with Apple → download `.p8` once.  
5. Note **Team ID**, **Key ID**, Services ID, and generate the JWT secret for Supabase.  
6. Supabase → **Providers → Apple** → Enable → fill fields.

### Email

Supabase → **Providers → Email** → Enable (password sign-in).  
In-app: Sign in / Create account / Forgot password.

---

## 3. What to enable vs leave off

| Provider | Enable? |
|----------|---------|
| **Email** | Yes |
| **Google** | Yes |
| **Apple** | Yes (especially for iOS store) |
| **Azure** | **No** (Microsoft account login removed from Harbor) |
| **SAML 2.0** | No |
| **Web3 Wallet** | No |
| Phone / Twitter / etc. | No unless you have a reason |

---

## 4. Email / password (industry-standard UX in-app)

| Action | Behavior |
|--------|----------|
| **Sign in** | Email + password |
| **Create account** | Email + password + confirm password (min 8 chars) |
| **Already registered** | Create account is denied with a clear toast → switch to Sign in |
| **Forgot password** | Sends Supabase reset email (`resetPasswordForEmail`) |
| **Sign out** | Clears session; **no** cloud backup / household push until sign-in again |
| **Factory reset** | Wipes local data **and** signs out of cloud |

For password reset links to work, keep the same **Redirect URLs** as OAuth (including `capacitor://localhost/**` and your web origin).

## 5. Test order

1. Enable **Google** + redirect URLs → Account & cloud → Continue with Google.  
2. Enable **Apple** → Continue with Apple (real device / TestFlight best).  
3. Email: create account → sign out → sign in → forgot password.  
4. Confirm rows under **Authentication → Users** (and `profiles` after FIX-profiles-ensure.sql).  

### Important: do not test only inside `mobile.html` iframe

`mobile.html` embeds Harbor in a phone **iframe**. Apple / Google **block** OAuth inside iframes.

Best first test: open **`index.html` full page** (Web), not the phone frame.

---

## 6. Auth login vs calendar OAuth

| Feature | Where |
|---------|--------|
| **Create Harbor account** (this doc) | Supabase Auth: Google / Apple / Email |
| **Connect Google Calendar** | Separate Edge Functions + `schema-d-calendar-oauth.sql` ([CALENDAR-OAUTH.md](./CALENDAR-OAUTH.md)) — optional later |

Signing in with Google does **not** automatically connect their calendar.

---

## 7. Privacy / App Store notes

- Optional account via Apple / Google / email.  
- If the app offers Google login on **iOS**, offer **Sign in with Apple** too (Harbor does).  
- Social login only when the user opens Account & cloud — core Harbor stays local-first.

---

*Related: [CALENDAR-OAUTH.md](./CALENDAR-OAUTH.md) · [FREE-VS-PRO.md](../product/FREE-VS-PRO.md) · [PRIVACY.md](../product/PRIVACY.md)*
