-- =============================================================================
-- Harbor C1c — Household Life pack share (MVP)
-- Run AFTER schema-c1-household.sql (membership + invites already work).
--
-- Shares: bills, subscriptions, grocery list, local schedule events.
-- Does NOT share: budget, tasks/habits (personal), full cloud backup, tokens.
-- =============================================================================

create table if not exists public.household_life_share (
  household_id uuid primary key references public.households (id) on delete cascade,
  payload jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  updated_by uuid references auth.users (id) on delete set null
);

create index if not exists household_life_share_updated_at_idx
  on public.household_life_share (updated_at desc);

alter table public.household_life_share enable row level security;

drop policy if exists "life_share_select_member" on public.household_life_share;
create policy "life_share_select_member"
  on public.household_life_share for select
  to authenticated
  using (public.is_household_member(household_id, auth.uid()));

-- Writes only via SECURITY DEFINER RPCs (no direct client upsert)
revoke all on table public.household_life_share from public, anon, authenticated;
grant select on table public.household_life_share to authenticated;

-- ---------------------------------------------------------------------------
-- Pull current life pack (null payload if none yet)
-- ---------------------------------------------------------------------------
create or replace function public.get_household_life_share(p_household_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_row public.household_life_share;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;
  if p_household_id is null or not public.is_household_member(p_household_id, v_uid) then
    raise exception 'Not a household member';
  end if;

  select * into v_row
  from public.household_life_share
  where household_id = p_household_id;

  if not found then
    return jsonb_build_object(
      'household_id', p_household_id,
      'payload', null,
      'updated_at', null,
      'updated_by', null
    );
  end if;

  return jsonb_build_object(
    'household_id', v_row.household_id,
    'payload', v_row.payload,
    'updated_at', v_row.updated_at,
    'updated_by', v_row.updated_by
  );
end;
$$;

revoke all on function public.get_household_life_share(uuid) from public;
grant execute on function public.get_household_life_share(uuid) to authenticated;

-- ---------------------------------------------------------------------------
-- Push life pack (member may write). Optimistic concurrency via base timestamp.
-- If p_base_updated_at is set and server is newer → returns conflict + server row.
-- ---------------------------------------------------------------------------
create or replace function public.upsert_household_life_share(
  p_household_id uuid,
  p_payload jsonb,
  p_base_updated_at timestamptz default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_existing public.household_life_share;
  v_now timestamptz := now();
  v_payload jsonb;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;
  if p_household_id is null or not public.is_household_member(p_household_id, v_uid) then
    raise exception 'Not a household member';
  end if;
  if p_payload is null or jsonb_typeof(p_payload) <> 'object' then
    raise exception 'Invalid life pack payload';
  end if;

  -- Soft size guard (~1.5MB text)
  if length(p_payload::text) > 1500000 then
    raise exception 'Life pack too large';
  end if;

  v_payload := p_payload || jsonb_build_object(
    'v', coalesce((p_payload->>'v')::int, 1),
    'updatedAt', v_now,
    'updatedBy', v_uid
  );

  select * into v_existing
  from public.household_life_share
  where household_id = p_household_id
  for update;

  if found then
    if p_base_updated_at is not null
       and v_existing.updated_at is not null
       and v_existing.updated_at > p_base_updated_at + interval '1 second' then
      return jsonb_build_object(
        'ok', false,
        'conflict', true,
        'household_id', v_existing.household_id,
        'payload', v_existing.payload,
        'updated_at', v_existing.updated_at,
        'updated_by', v_existing.updated_by
      );
    end if;

    update public.household_life_share
    set payload = v_payload,
        updated_at = v_now,
        updated_by = v_uid
    where household_id = p_household_id;

    return jsonb_build_object(
      'ok', true,
      'conflict', false,
      'household_id', p_household_id,
      'payload', v_payload,
      'updated_at', v_now,
      'updated_by', v_uid
    );
  end if;

  insert into public.household_life_share (household_id, payload, updated_at, updated_by)
  values (p_household_id, v_payload, v_now, v_uid);

  return jsonb_build_object(
    'ok', true,
    'conflict', false,
    'household_id', p_household_id,
    'payload', v_payload,
    'updated_at', v_now,
    'updated_by', v_uid
  );
end;
$$;

revoke all on function public.upsert_household_life_share(uuid, jsonb, timestamptz) from public;
grant execute on function public.upsert_household_life_share(uuid, jsonb, timestamptz) to authenticated;
