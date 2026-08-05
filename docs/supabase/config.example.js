/**
 * Harbor cloud config — local override template (do not commit secrets).
 *
 * Production web (harborlife.app) loads config.public.js (publishable key only).
 * For local debug overrides:
 *   1. Create project at https://supabase.com
 *   2. Project Settings → API Keys → Project URL + Publishable key
 *   3. Run docs/supabase/schema.sql
 *   4. Auth → enable Email + Google; add Redirect URLs for your origin
 *   5. cp config.example.js config.local.js  and fill in your values
 *
 * URL format: https://YOUR_REF.supabase.co
 *   (do NOT add /rest/v1/ — the client adds API paths)
 *
 * Use the Publishable key (was called "anon"). Never put the Secret key here.
 *
 * Optional: authRedirectTo: 'https://harborlife.app/index.html'
 *   (web usually omits this — redirect defaults to the current origin)
 */
window.HARBOR_SUPABASE = {
  url: 'https://YOUR_PROJECT.supabase.co',
  anonKey: 'YOUR_PUBLISHABLE_OR_ANON_KEY',
  /** Set true only while debugging */
  debug: false
};
