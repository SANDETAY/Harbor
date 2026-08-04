# Harbor public beta — readiness

**Goal:** Invite strangers (Reddit / TestFlight) without gutting the app.  
**Mission:** Help people with **analysis paralysis** — one next step that fits energy.

## What build 488+ does for public test

| Area | Behavior |
|------|----------|
| **First week** | New installs use `simpleMode: 'auto'` (Task + energy first) |
| **Light existing installs** | `< 10` completions, never graduated → re-enter First week once (`publicBetaV1Migrated`) |
| **Chrome** | Hides smart banner noise, rest strip, person filter, Coming up, Library “later” label |
| **Beta chip** | Header shows **Beta** when `HARBOR_CHANNEL === 'beta'` |
| **Pulse feedback** | Soft prompt after 2 opens or 2 completes: Too much / Just right / Confusing |
| **Menu** | **How does Harbor feel?** + full **Send feedback** (build # in payload) |

## Before you post a public TestFlight link

1. **Ship** current Desktop Harbor (`Ship Harbor`) so testers get 488+.  
2. **Supabase RLS** — confirm users can only read/write their own rows (profiles, snapshots, household_*, calendar_*).  
3. **Keys** — client must only ship **publishable/anon** key (not service role). `private/` stays off-device.  
4. **Auth** — email confirmation on; watch for spam signups after Reddit.  
5. **Privacy URL** — live (GitHub Pages `privacy.html` is fine).  
6. **Post text** — beta, analysis paralysis / overwhelmed home, ask for one-tap pulse or “too much?”  
7. **Do not post** household invite codes or admin links.

## Reddit / public invite (safe framing)

- Use **TestFlight external** link only (not a random household code).  
- Say it’s a **beta**; data is local-first; optional account.  
- Apple **Seller** may show your legal name (individual account) — normal until LLC/org.  
- Expect silence + a few real notes; pulse modal is for the silent majority who install.

## Flip to “stable” later

In `index.html`:

```js
const HARBOR_CHANNEL = 'stable';
```

Hides Beta chip; soft pulse only runs when channel is `beta`.

## Local check

1. Factory reset → onboarding → First week checklist visible.  
2. Complete 2 tasks → pulse may appear.  
3. Menu → **How does Harbor feel?** → send.  
4. Settings → First week toggle still works.
