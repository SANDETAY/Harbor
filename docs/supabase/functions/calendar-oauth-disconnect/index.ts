// Harbor — disconnect calendar OAuth provider for the signed-in user
// Deploy: supabase functions deploy calendar-oauth-disconnect

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

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL') || '';
    const anon = Deno.env.get('SUPABASE_ANON_KEY') || '';
    const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
    if (!supabaseUrl || !anon || !serviceKey) return json({ error: 'Server misconfigured' }, 500);

    const authHeader = req.headers.get('Authorization') || '';
    const userClient = createClient(supabaseUrl, anon, {
      global: { headers: { Authorization: authHeader } },
    });
    const { data: userData, error: userErr } = await userClient.auth.getUser();
    if (userErr || !userData?.user) return json({ error: 'Not authenticated' }, 401);

    const body = await req.json().catch(() => ({}));
    if (body.provider === 'microsoft' || body.provider === 'outlook') {
      return json({ error: 'Outlook calendar connect is not available' }, 400);
    }
    const provider = 'google';

    const admin = createClient(supabaseUrl, serviceKey);
    const { error } = await admin
      .from('calendar_connections')
      .delete()
      .eq('user_id', userData.user.id)
      .eq('provider', provider);
    if (error) return json({ error: error.message }, 500);
    return json({ ok: true, provider });
  } catch (err) {
    return json({ error: err instanceof Error ? err.message : 'Disconnect failed' }, 500);
  }
});
