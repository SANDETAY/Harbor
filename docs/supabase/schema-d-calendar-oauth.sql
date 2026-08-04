-- =============================================================================
-- Harbor Phase D — Google Calendar OAuth connections (server-held tokens)
-- Run AFTER schema.sql (Phase B). Safe to re-run.
-- Client NEVER reads refresh_token; only Edge Functions (service role) should.
-- =============================================================================

create table if not exists public.calendar_connections (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  provider text not null check (provider in ('google', 'microsoft')),
  -- Google account email (display only)
  account_email text,
  -- Opaque refresh token — treat as secret. RLS: no select of this column for clients
  -- (clients use SELECT with column grants; Edge uses service role).
  refresh_token text not null,
  access_token text,
  access_token_expires_at timestamptz,
  scopes text,
  -- Optional: last successful event sync
  last_sync_at timestamptz,
  last_sync_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, provider)
);

create index if not exists calendar_connections_user_id_idx
  on public.calendar_connections (user_id);

alter table public.calendar_connections enable row level security;

-- Clients: may see that a connection exists (not tokens)
drop policy if exists "calendar_connections_select_meta" on public.calendar_connections;
create policy "calendar_connections_select_meta"
  on public.calendar_connections for select
  to authenticated
  using (user_id = auth.uid());

-- No client insert/update/delete — Edge Functions use service role
drop policy if exists "calendar_connections_insert" on public.calendar_connections;
drop policy if exists "calendar_connections_update" on public.calendar_connections;
drop policy if exists "calendar_connections_delete" on public.calendar_connections;

revoke all on table public.calendar_connections from public, anon;
revoke insert, update, delete on table public.calendar_connections from authenticated;
-- Authenticated can select; column privilege still allows refresh_token unless revoked:
revoke all on table public.calendar_connections from authenticated;
grant select (id, user_id, provider, account_email, scopes, last_sync_at, last_sync_error, created_at, updated_at)
  on table public.calendar_connections to authenticated;

-- Helper: am I connected? (no token leakage)
create or replace function public.my_calendar_connection_status()
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;
  return coalesce(
    (
      select jsonb_agg(
        jsonb_build_object(
          'provider', c.provider,
          'account_email', c.account_email,
          'last_sync_at', c.last_sync_at,
          'connected', true
        )
      )
      from public.calendar_connections c
      where c.user_id = v_uid
    ),
    '[]'::jsonb
  );
end;
$$;

revoke all on function public.my_calendar_connection_status() from public, anon;
grant execute on function public.my_calendar_connection_status() to authenticated;
