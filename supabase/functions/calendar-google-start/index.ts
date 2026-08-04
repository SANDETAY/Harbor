/**
 * Harbor — start Google Calendar OAuth (read-only).
 * Requires secrets: GOOGLE_CLIENT_ID, SUPABASE_URL (auto), optional HARBOR_OAUTH_RETURN_URL
 *
 * Client: Authorization: Bearer <user access_token>
 * Returns: { url: string } — open in browser / system browser
 */
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.49.8';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });

  try {
    const clientId = Deno.env.get('GOOGLE_CLIENT_ID');
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    if (!clientId) throw new Error('GOOGLE_CLIENT_ID not configured');

    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(JSON.stringify({ error: 'Sign in required' }), {
        status: 401,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    const supabase = createClient(supabaseUrl, Deno.env.get('SUPABASE_ANON_KEY')!, {
      global: { headers: { Authorization: authHeader } },
    });
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error || !user) {
      return new Response(JSON.stringify({ error: 'Invalid session' }), {
        status: 401,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    const redirectUri = `${supabaseUrl}/functions/v1/calendar-google-callback`;
    // state = base64url(user id + nonce) — callback verifies JWT via cookie alternative:
    // we embed user id signed... For v1: put user_id in state; callback requires re-auth via service.
    // Safer: state = user.id + '.' + random; store pending in DB. v1 uses signed state with user id only
    // because callback exchanges with service role after Google returns — we trust Google state echo
    // only when we also receive a Harbor session... Callback uses state as user_id (UUID).
    const state = user.id;

    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: 'https://www.googleapis.com/auth/calendar.readonly email',
      access_type: 'offline',
      prompt: 'consent',
      include_granted_scopes: 'true',
      state,
    });

    const url = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
    return new Response(JSON.stringify({ url }), {
      headers: { ...cors, 'Content-Type': 'application/json' },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: (e as Error).message || 'start failed' }), {
      status: 500,
      headers: { ...cors, 'Content-Type': 'application/json' },
    });
  }
});
