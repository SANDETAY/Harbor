# Fix now — Invite + Google/Microsoft login (build 443)

Two separate issues. Do both.

---

## 1. Invite for your wife (can fix without reinstalling)

Harbor does **not** create a website link. It creates a **one-time invite code** you text/share.

### A. Run this SQL in Supabase (most common fix)

1. Open [Supabase Dashboard](https://supabase.com/dashboard) → your Harbor project  
2. **SQL Editor** → New query  
3. Open this file on your Mac and paste **all** of it:

   `Desktop/Harbor/docs/supabase/FIX-invite-gen-random-bytes.sql`

4. Click **Run** (should succeed with no error)  
5. In Harbor (signed in with Apple is fine):  
   **Menu → Household → Create household** (if you don’t have one) → **Create invite for partner**  
6. Use **Share via Messages / text** to send her the code  
7. She: installs Harbor → signs in → **Household → paste code → Join**

If the toast still mentions `gen_random_bytes` or “function does not exist”, the SQL did not apply — re-run it.

### B. If it says “Only the household owner”

You joined someone else’s household, or you’re not the creator. Leave household, then **Create household** yourself, then invite.

---

## 2. Google login (native / TestFlight)

Apple often works in-app. Google blocks the WebView, so Harbor opens Safari and must **return to the app**.

**Microsoft / Azure account sign-in is not used** — leave Azure **disabled** in Supabase.

### A. Supabase Redirect URLs (required)

**Authentication → URL configuration → Redirect URLs** — add **all** of these:

```text
com.sandetay.harbor://auth/callback
com.sandetay.harbor://**
Harbor://**
capacitor://localhost
capacitor://localhost/**
```

Also keep your web URLs if you test on desktop.

### B. Providers enabled

- **Google** — Enabled, with **Web application** Client ID + secret  
- **Apple** — Enabled  
- **Email** — Enabled  
- **Azure** — **Off**

Google Cloud redirect URI must be:

```text
https://dyaicsnoefkfshesyogk.supabase.co/auth/v1/callback
```

### C. Ship a current TestFlight build

Use **Ship Harbor** so the phone has the latest Account & cloud UI (Apple + Google + email only).

---

## Prepare + archive (Mac)

```bash
cd ~/Desktop/Harbor
bash scripts/cap-prepare.sh
npx cap sync ios
open ios/App/App.xcworkspace
```

Then Product → Archive → distribute to TestFlight.

---

## Quick test checklist

| Step | Expected |
|------|----------|
| Run FIX SQL | Success in SQL Editor |
| Create invite | Code appears + Share sheet |
| Wife pastes code | Joins household |
| Google login | Safari opens → returns to Harbor signed in |

If Google opens Safari, you log in, but Harbor never shows signed in: Redirect URLs (section 2A) are almost always wrong/missing.
