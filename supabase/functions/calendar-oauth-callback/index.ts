// Harbor — OAuth callback: exchange code, store refresh token (service role only)
// Deploy: supabase functions deploy calendar-oauth-callback

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.49.1';

function b64urlDecode(s: string) {
  const pad = s.length % 4 === 0 ? '' : '='.repeat(4 - (s.length % 4));
  const b64 = s.replace(/-/g, '+').replace(/_/g, '/') + pad;
  return atob(b64);
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
  const bytes = new Uint8Array(sig);
  let s = btoa(String.fromCharCode(...bytes));
  return s.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function html(title: string, body: string) {
  return new Response(
    `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>${title}</title>
    <style>
      body{font-family:system-ui,sans-serif;background:#0f1c1a;color:#e8f2ef;display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0;padding:1.5rem}
      .card{max-width:22rem;background:#1a2e2a;border:1px solid #2d4a44;border-radius:1.25rem;padding:1.5rem;text-align:center}
      h1{font-size:1.1rem;margin:0 0 .5rem}p{font-size:.85rem;opacity:.85;line-height:1.45;margin:0}
      a{color:#7dcfb6}
    </style></head><body><div class="card"><h1>${title}</h1><p>${body}</p></div>
    <script>try{if(window.opener)setTimeout(function(){window.close()},1200)}catch(e){}</script>
    </body></html>`,
    { headers: { 'Content-Type': 'text/html; charset=utf-8' } },
  );
}

Deno.serve(async (req) => {
  try {
    const url = new URL(req.url);
    const code = url.searchParams.get('code') || '';
    const stateRaw = url.searchParams.get('state') || '';
    const err = url.searchParams.get('error');
    if (err) return html('Couldn’t connect', `Provider said: ${err}. You can close this tab.`);
    if (!code || !stateRaw) return html('Missing code', 'Try Connect again from Harbor.');

    const stateSecret = Deno.env.get('OAUTH_STATE_SECRET') || '';
    const [payloadB64, sig] = stateRaw.split('.');
    if (!payloadB64 || !sig || !stateSecret) return html('Bad state', 'Try Connect again.');
    const statePayload = b64urlDecode(payloadB64);
    const expect = await hmacState(statePayload, stateSecret);
    if (expect !== sig) return html('Invalid state', 'Try Connect again from Harbor.');

    const state = JSON.parse(statePayload) as {
      u: string; p: string; r?: string; t?: number;
    };
    if (!state.u || !state.p) return html('Invalid state', 'Try Connect again.');
    if (state.t && Date.now() - state.t > 15 * 60 * 1000) {
      return html('Link expired', 'Go back to Harbor and tap Connect again.');
    }

    if (state.p === 'microsoft' || state.p === 'outlook') {
      return html('Not available', 'Outlook calendar connect is not offered. Use Google, phone calendars, or .ics.');
    }
    const provider = 'google';
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || '';
    const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
    const callback =
      `${supabaseUrl.replace(/\/$/, '')}/functions/v1/calendar-oauth-callback`;
    const admin = createClient(supabaseUrl, serviceKey);

    let refresh_token = '';
    let access_token = '';
    let expires_at: string | null = null;
    let account_email: string | null = null;
    let scopes: string | null = null;

    const clientId = Deno.env.get('GOOGLE_CLIENT_ID') || '';
    const clientSecret = Deno.env.get('GOOGLE_CLIENT_SECRET') || '';
    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: callback,
        grant_type: 'authorization_code',
      }),
    });
    const tok = await tokenRes.json();
    if (!tokenRes.ok) {
      return html('Token exchange failed', tok.error_description || tok.error || 'Google error');
    }
    refresh_token = tok.refresh_token || '';
    access_token = tok.access_token || '';
    scopes = tok.scope || null;
    if (tok.expires_in) {
      expires_at = new Date(Date.now() + Number(tok.expires_in) * 1000).toISOString();
    }
    if (tok.id_token) {
      try {
        const mid = tok.id_token.split('.')[1];
        const claims = JSON.parse(b64urlDecode(mid));
        account_email = claims.email || null;
      } catch (_) { /* ignore */ }
    }
    if (!refresh_token) {
      // Re-consent may be needed; keep access-only row only if we already had a refresh
      const { data: existing } = await admin
        .from('calendar_connections')
        .select('refresh_token')
        .eq('user_id', state.u)
        .eq('provider', 'google')
        .maybeSingle();
      refresh_token = existing?.refresh_token || '';
    }
    if (!refresh_token) {
      return html('No refresh token', 'Disconnect in Google account permissions, then Connect again with consent.');
    }

    const { error: upErr } = await admin.from('calendar_connections').upsert(
      {
        user_id: state.u,
        provider,
        account_email,
        refresh_token,
        access_token: access_token || null,
        access_token_expires_at: expires_at,
        scopes,
        last_sync_error: null,
        updated_at: new Date().toISOString(),
      },
      { onConflict: 'user_id,provider' },
    );
    if (upErr) return html('Save failed', upErr.message);

    const back = state.r
      ? `<a href="${state.r}">Return to Harbor</a>`
      : 'You can close this tab and return to Harbor.';
    return html('Connected', `Google Calendar is linked. ${back}`);  } catch (e) {
    return html('Error', e instanceof Error ? e.message : 'Unexpected error');
  }
});
