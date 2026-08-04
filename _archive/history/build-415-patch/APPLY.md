# Build 415 patch — apply on your Mac

macOS blocked this agent from overwriting your live `index.html` / `sw.js`.
Copy these files into the Harbor root:

```bash
cd ~/Desktop/Harbor
cp build-415-patch/index.html ./index.html
cp build-415-patch/sw.js ./sw.js
# optional: keep SQL docs in sync
cp build-415-patch/docs/supabase/FIX-invite-gen-random-bytes.sql docs/supabase/
```

Then for native TestFlight:
```bash
# prepare Capacitor www + archive as you usually do
npm run cap:prepare   # or your scripts/cap-prepare.sh
```

## Invite fix (do this in Supabase now — no app rebuild required)

1. Open Supabase → SQL Editor
2. Paste contents of `docs/supabase/FIX-invite-gen-random-bytes.sql` (also in this folder)
3. Run
4. In Harbor: Household → Create invite again

## What changed in the app

- **Due this week** + **Renewing soon** no longer take full Task feed space
- They appear as compact **chips under the smart banner**
- Tap a chip → Coming up / Subscriptions
