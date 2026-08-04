/**
 * Harbor cloud config — copy to config.local.js (do not commit secrets).
 *
 * 1. Create project at https://supabase.com
 * 2. Project Settings → API Keys → Project URL + Publishable key
 * 3. Run docs/supabase/schema.sql
 * 4. Auth → enable Email
 * 5. cp config.example.js config.local.js  and fill in your values
 *
 * URL format: https://YOUR_REF.supabase.co
 *   (do NOT add /rest/v1/ — the client adds API paths)
 *
 * Use the Publishable key (was called "anon"). Never put the Secret key here.
 */
window.HARBOR_SUPABASE = {
  url: 'https://YOUR_PROJECT.supabase.co',
  anonKey: 'YOUR_PUBLISHABLE_OR_ANON_KEY',
  /** Set true only while debugging */
  debug: false
};
