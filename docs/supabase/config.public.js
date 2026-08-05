/**
 * Production / GitHub Pages cloud config (safe to commit).
 * Uses the Supabase publishable (anon) key — public by design when RLS is on.
 *
 * Local overrides: copy config.example.js → config.local.js (gitignored).
 * Load order: config.public.js then config.local.js (local wins when present).
 */
window.HARBOR_SUPABASE = {
  url: 'https://dyaicsnoefkfshesyogk.supabase.co',
  anonKey: 'sb_publishable_NZrMg-ECCTtmrt2zX0cVJg_eDs-B-yT',
  debug: false
};
