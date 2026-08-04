// Harbor — start Google Calendar OAuth (Google only)
// Deploy: supabase functions deploy calendar-oauth-start
// Secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH_STATE_SECRET
// (Client secrets used on callback; start only needs client ID.)

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.49.1';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors, 'Content-Type': 'application/json' },
  });
}

function b64url(bytes: Uint8Array) {
  let s = btoa(String.fromCharCode(...bytes));
  return s.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function hmacState(payload: string, secret: string) {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payload));
  return b64url(new Uint8Array(sig));
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || '';
    const anon = Deno.env.get('SUPABASE_ANON_KEY') || '';
    const stateSecret = Deno.env.get('OAUTH_STATE_SECRET') || '';
    if (!supabaseUrl || !anon) return json({ error: 'Server misconfigured' }, 500);
    if (!stateSecret) return json({ error: 'OAUTH_STATE_SECRET not set' }, 500);

    const authHeader = req.headers.get('Authorization') || '';
    const userClient = createClient(supabaseUrl, anon, {
      global: { headers: { Authorization: authHeader } },
    });
    const { data: userData, error: userErr } = await userClient.auth.getUser();
    if (userErr || !userData?.user) return json({ error: 'Not authenticated' }, 401);
    const userId = userData.user.id;

    const body = await req.json().catch(() => ({}));
    if (body.provider === 'microsoft' || body.provider === 'outlook') {
      return json({ error: 'Outlook calendar connect is not available' }, 400);
    }
    const provider = 'google';
    const redirectTo = typeof body.redirect_to === 'string' ? body.redirect_to : '';

    const nonce = b64url(crypto.getRandomValues(new Uint8Array(16)));
    const statePayload = JSON.stringify({
      u: userId,
      p: provider,
      n: nonce,
      r: redirectTo,
      t: Date.now(),
    });
    const state = b64url(new TextEncoder().encode(statePayload)) + '.' + (await hmacState(statePayload, stateSecret));

    const callback =
      `${supabaseUrl.replace(/\/$/, '')}/functions/v1/calendar-oauth-callback`;

    const clientId = Deno.env.get('GOOGLE_CLIENT_ID') || '';
    if (!clientId) return json({ error: 'GOOGLE_CLIENT_ID not set' }, 500);
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: callback,
      response_type: 'code',
      scope: 'openid email https://www.googleapis.com/auth/calendar.readonly',
      access_type: 'offline',
      prompt: 'consent',
      state,
    });
    return json({ url: `https://accounts.google.com/o/oauth2/v2/auth?${params}` });
  } catch (err) {
    return json({ error: err instanceof Error ? err.message : 'Start failed' }, 500);
  }
});
