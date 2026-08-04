/**
 * Harbor — fetch Google Calendar events for the signed-in user (read-only).
 * Secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SUPABASE_SERVICE_ROLE_KEY
 *
 * Body optional: { timeMin?: ISO, timeMax?: ISO }
 * Returns: { events: HarborEventLike[], account_email?: string }
 */
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.49.8';

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

async function refreshAccess(
  refreshToken: string,
  clientId: string,
  clientSecret: string,
) {
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
    }),
  });
  const j = await res.json();
  if (!res.ok) throw new Error(j.error_description || j.error || 'refresh failed');
  return j as { access_token: string; expires_in?: number };
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });

  try {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(JSON.stringify({ error: 'Sign in required' }), {
        status: 401,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const anon = Deno.env.get('SUPABASE_ANON_KEY')!;
    const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const clientId = Deno.env.get('GOOGLE_CLIENT_ID')!;
    const clientSecret = Deno.env.get('GOOGLE_CLIENT_SECRET')!;

    const userClient = createClient(supabaseUrl, anon, {
      global: { headers: { Authorization: authHeader } },
    });
    const { data: { user }, error: uErr } = await userClient.auth.getUser();
    if (uErr || !user) {
      return new Response(JSON.stringify({ error: 'Invalid session' }), {
        status: 401,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    const admin = createClient(supabaseUrl, serviceKey);
    const { data: conn, error: cErr } = await admin
      .from('calendar_connections')
      .select('*')
      .eq('user_id', user.id)
      .eq('provider', 'google')
      .maybeSingle();
    if (cErr) throw cErr;
    if (!conn?.refresh_token) {
      return new Response(JSON.stringify({ error: 'Google Calendar not connected', code: 'NOT_CONNECTED' }), {
        status: 404,
        headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    let access = conn.access_token as string | null;
    const exp = conn.access_token_expires_at ? new Date(conn.access_token_expires_at).getTime() : 0;
    if (!access || exp < Date.now() + 60_000) {
      const refreshed = await refreshAccess(conn.refresh_token, clientId, clientSecret);
      access = refreshed.access_token;
      await admin.from('calendar_connections').update({
        access_token: access,
        access_token_expires_at: new Date(Date.now() + (refreshed.expires_in || 3600) * 1000).toISOString(),
        updated_at: new Date().toISOString(),
      }).eq('id', conn.id);
    }

    let body: { timeMin?: string; timeMax?: string } = {};
    try {
      if (req.method === 'POST') body = await req.json();
    } catch { /* empty */ }

    const now = new Date();
    const timeMin = body.timeMin || new Date(now.getTime() - 14 * 864e5).toISOString();
    const timeMax = body.timeMax || new Date(now.getTime() + 120 * 864e5).toISOString();

    const gUrl = new URL('https://www.googleapis.com/calendar/v3/calendars/primary/events');
    gUrl.searchParams.set('singleEvents', 'true');
    gUrl.searchParams.set('orderBy', 'startTime');
    gUrl.searchParams.set('timeMin', timeMin);
    gUrl.searchParams.set('timeMax', timeMax);
    gUrl.searchParams.set('maxResults', '250');

    const gRes = await fetch(gUrl.toString(), {
      headers: { Authorization: `Bearer ${access}` },
    });
    const gJson = await gRes.json();
    if (!gRes.ok) {
      await admin.from('calendar_connections').update({
        last_sync_error: gJson.error?.message || 'Google API error',
        updated_at: new Date().toISOString(),
      }).eq('id', conn.id);
      throw new Error(gJson.error?.message || 'Google Calendar API error');
    }

    const events = (gJson.items || []).map((ev: Record<string, unknown>) => {
      const start = ev.start as { dateTime?: string; date?: string } | undefined;
      const end = ev.end as { dateTime?: string; date?: string } | undefined;
      const allDay = !!(start?.date && !start?.dateTime);
      return {
        id: `gcal-${ev.id}`,
        title: (ev.summary as string) || '(No title)',
        start: start?.dateTime || start?.date || null,
        end: end?.dateTime || end?.date || null,
        allDay,
        location: (ev.location as string) || '',
        notes: (ev.description as string) || '',
        source: 'google_oauth',
        provider: 'google',
      };
    }).filter((e: { start: string | null }) => e.start);

    await admin.from('calendar_connections').update({
      last_sync_at: new Date().toISOString(),
      last_sync_error: null,
      updated_at: new Date().toISOString(),
    }).eq('id', conn.id);

    return new Response(JSON.stringify({
      events,
      account_email: conn.account_email,
      timeMin,
      timeMax,
    }), {
      headers: { ...cors, 'Content-Type': 'application/json' },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: (e as Error).message || 'events failed' }), {
      status: 500,
      headers: { ...cors, 'Content-Type': 'application/json' },
    });
  }
});
