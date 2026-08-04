/**
 * Harbor — Google OAuth callback. Exchanges code for refresh_token; stores row.
 * Secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SUPABASE_SERVICE_ROLE_KEY,
 *          HARBOR_OAUTH_RETURN_URL (or HARBOR_OAUTH_RETURN_URL_PROD)
 */
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.49.8';

function htmlRedirect(to: string, message: string) {
  const safe = to.replace(/"/g, '');
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=${safe}">
<title>Harbor</title></head><body style="font-family:system-ui;padding:2rem">
<p>${message}</p><p><a href="${safe}">Continue to Harbor</a></p></body></html>`;
}

Deno.serve(async (req) => {
  const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
  const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
  const clientId = Deno.env.get('GOOGLE_CLIENT_ID')!;
  const clientSecret = Deno.env.get('GOOGLE_CLIENT_SECRET')!;
  const returnBase =
    Deno.env.get('HARBOR_OAUTH_RETURN_URL') ||
    Deno.env.get('HARBOR_OAUTH_RETURN_URL_PROD') ||
    'http://127.0.0.1:3000/';

  try {
    const url = new URL(req.url);
    const err = url.searchParams.get('error');
    if (err) {
      const dest = new URL(returnBase);
      dest.searchParams.set('calendar_oauth', 'error');
      dest.searchParams.set('reason', err);
      return new Response(htmlRedirect(dest.toString(), 'Calendar connect cancelled.'), {
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
      });
    }

    const code = url.searchParams.get('code');
    const state = url.searchParams.get('state'); // user id
    if (!code || !state || !/^[0-9a-f-]{36}$/i.test(state)) {
      throw new Error('Missing code or state');
    }

    const redirectUri = `${supabaseUrl}/functions/v1/calendar-google-callback`;
    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri,
        grant_type: 'authorization_code',
      }),
    });
    const tokenJson = await tokenRes.json();
    if (!tokenRes.ok) {
      throw new Error(tokenJson.error_description || tokenJson.error || 'Token exchange failed');
    }

    const refresh = tokenJson.refresh_token as string | undefined;
    const access = tokenJson.access_token as string;
    const expiresIn = Number(tokenJson.expires_in || 3600);
    if (!access) throw new Error('No access token');

    // Account email (optional)
    let accountEmail: string | null = null;
    try {
      const ui = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
        headers: { Authorization: `Bearer ${access}` },
      });
      if (ui.ok) {
        const j = await ui.json();
        accountEmail = j.email || null;
      }
    } catch { /* ignore */ }

    const admin = createClient(supabaseUrl, serviceKey);
    const row: Record<string, unknown> = {
      user_id: state,
      provider: 'google',
      account_email: accountEmail,
      access_token: access,
      access_token_expires_at: new Date(Date.now() + expiresIn * 1000).toISOString(),
      scopes: tokenJson.scope || 'https://www.googleapis.com/auth/calendar.readonly',
      updated_at: new Date().toISOString(),
      last_sync_error: null,
    };
    // Only overwrite refresh_token when Google returns a new one
    if (refresh) row.refresh_token = refresh;

    // Upsert: if re-consent without new refresh, keep old refresh_token
    const { data: existing } = await admin
      .from('calendar_connections')
      .select('refresh_token')
      .eq('user_id', state)
      .eq('provider', 'google')
      .maybeSingle();

    if (!refresh && existing?.refresh_token) {
      row.refresh_token = existing.refresh_token;
    }
    if (!row.refresh_token) {
      throw new Error('No refresh token — revoke Harbor in Google Account permissions and try again with consent');
    }

    const { error: upErr } = await admin.from('calendar_connections').upsert(row, {
      onConflict: 'user_id,provider',
    });
    if (upErr) throw upErr;

    const dest = new URL(returnBase);
    dest.searchParams.set('calendar_oauth', 'connected');
    if (accountEmail) dest.searchParams.set('email', accountEmail);
    return new Response(htmlRedirect(dest.toString(), 'Calendar connected. Returning to Harbor…'), {
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    });
  } catch (e) {
    const dest = new URL(returnBase);
    dest.searchParams.set('calendar_oauth', 'error');
    dest.searchParams.set('reason', (e as Error).message || 'callback_failed');
    return new Response(htmlRedirect(dest.toString(), 'Could not connect calendar.'), {
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    });
  }
});
