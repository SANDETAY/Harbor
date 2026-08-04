-- =============================================================================
-- Harbor — FIX household invite (ambiguous is_household_member)
--
-- Error you hit:
--   function public.is_household_member(uuid) is not unique
--
-- Cause: two overloads exist (e.g. (uuid) and (uuid, uuid)). Policies that call
-- is_household_member(id) with one arg cannot pick a winner.
--
-- This script:
--   1) Drops ALL overloads of the helper functions
--   2) Recreates ONE clear pair (uuid, uuid) — always pass auth.uid()
--   3) Ensures invite table + create/accept/list/leave RPCs exist
--
-- Supabase → SQL Editor → New query → paste ALL → Run
-- Safe to re-run.
-- =============================================================================

create extension if not exists pgcrypto with schema extensions;

-- ---------------------------------------------------------------------------
-- Drop ALL helper overloads (names may collide across past partial runs)
-- ---------------------------------------------------------------------------
do $$
declare
  r record;
begin
  for r in
    select p.oid::regprocedure as sig
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.proname in (
        'is_household_member',
        'is_household_owner'
      )
  loop
    execute 'drop function if exists ' || r.sig || ' cascade';
  end loop;
end $$;

-- ---------------------------------------------------------------------------
-- Tables (no-op if already present)
-- ---------------------------------------------------------------------------
create table if not exists public.households (
  id uuid primary key default gen_random_uuid(),
  name text,
  owner_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.households
  add column if not exists name text,
  add column if not exists updated_at timestamptz not null default now();

create table if not exists public.household_members (
  household_id uuid not null references public.households (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  role text not null default 'member' check (role in ('owner', 'member')),
  display_name text,
  joined_at timestamptz not null default now(),
  primary key (household_id, user_id)
);

alter table public.household_members
  add column if not exists display_name text,
  add column if not exists joined_at timestamptz not null default now();

create table if not exists public.household_invites (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references public.households (id) on delete cascade,
  created_by uuid not null references auth.users (id) on delete cascade,
  token_hash text not null unique,
  label text,
  status text not null default 'pending'
    check (status in ('pending', 'accepted', 'revoked', 'expired')),
  expires_at timestamptz not null,
  accepted_by uuid references auth.users (id) on delete set null,
  accepted_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists household_members_user_id_idx
  on public.household_members (user_id);
create index if not exists household_invites_household_id_idx
  on public.household_invites (household_id);

alter table public.households enable row level security;
alter table public.household_members enable row level security;
alter table public.household_invites enable row level security;

-- ---------------------------------------------------------------------------
-- Helpers — ONLY two-arg form (no defaults → no ambiguity)
-- ---------------------------------------------------------------------------
create or replace function public.is_household_member(p_household_id uuid, p_user_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.household_members m
    where m.household_id = p_household_id
      and m.user_id = p_user_id
  );
$$;

create or replace function public.is_household_owner(p_household_id uuid, p_user_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.households h
    where h.id = p_household_id
      and h.owner_id = p_user_id
  );
$$;

revoke all on function public.is_household_member(uuid, uuid) from public;
revoke all on function public.is_household_owner(uuid, uuid) from public;
grant execute on function public.is_household_member(uuid, uuid) to authenticated;
grant execute on function public.is_household_owner(uuid, uuid) to authenticated;

-- ---------------------------------------------------------------------------
-- RLS policies — always pass auth.uid() as second arg
-- ---------------------------------------------------------------------------
drop policy if exists "households_select_member" on public.households;
create policy "households_select_member"
  on public.households for select
  to authenticated
  using (public.is_household_member(id, auth.uid()));

drop policy if exists "households_insert_owner" on public.households;
create policy "households_insert_owner"
  on public.households for insert
  to authenticated
  with check (owner_id = auth.uid());

drop policy if exists "households_update_owner" on public.households;
create policy "households_update_owner"
  on public.households for update
  to authenticated
  using (owner_id = auth.uid())
  with check (owner_id = auth.uid());

drop policy if exists "households_delete_owner" on public.households;
create policy "households_delete_owner"
  on public.households for delete
  to authenticated
  using (owner_id = auth.uid());

drop policy if exists "members_select_same_household" on public.household_members;
create policy "members_select_same_household"
  on public.household_members for select
  to authenticated
  using (public.is_household_member(household_id, auth.uid()));

drop policy if exists "members_delete_self_or_owner" on public.household_members;
create policy "members_delete_self_or_owner"
  on public.household_members for delete
  to authenticated
  using (
    user_id = auth.uid()
    or public.is_household_owner(household_id, auth.uid())
  );

drop policy if exists "invites_select_creator" on public.household_invites;
create policy "invites_select_creator"
  on public.household_invites for select
  to authenticated
  using (
    created_by = auth.uid()
    and public.is_household_owner(household_id, auth.uid())
  );

-- ---------------------------------------------------------------------------
-- RPC: create household
-- ---------------------------------------------------------------------------
create or replace function public.create_household(p_name text default 'Family')
returns public.households
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_row public.households;
  v_name text;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;
  v_name := left(trim(coalesce(nullif(p_name, ''), 'Family')), 48);

  if exists (select 1 from public.households h where h.owner_id = v_uid) then
    select * into v_row from public.households h where h.owner_id = v_uid limit 1;
    return v_row;
  end if;

  insert into public.households (name, owner_id)
  values (v_name, v_uid)
  returning * into v_row;

  insert into public.household_members (household_id, user_id, role, display_name)
  values (
    v_row.id,
    v_uid,
    'owner',
    coalesce(
      (select nullif(trim(p.display_name), '') from public.profiles p where p.id = v_uid),
      (select split_part(u.email, '@', 1) from auth.users u where u.id = v_uid),
      'Me'
    )
  );

  return v_row;
end;
$$;

revoke all on function public.create_household(text) from public;
grant execute on function public.create_household(text) to authenticated;

-- ---------------------------------------------------------------------------
-- RPC: create invite (plaintext token returned once)
-- ---------------------------------------------------------------------------
create or replace function public.create_household_invite(
  p_household_id uuid,
  p_label text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_uid uuid := auth.uid();
  v_token text;
  v_hash text;
  v_exp timestamptz;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;
  if not public.is_household_owner(p_household_id, v_uid) then
    raise exception 'Only the household owner can invite';
  end if;

  if (
    select count(*) from public.household_invites i
    where i.household_id = p_household_id
      and i.status = 'pending'
      and i.expires_at > now()
  ) >= 10 then
    raise exception 'Too many pending invites — revoke some first';
  end if;

  v_token := encode(extensions.gen_random_bytes(32), 'hex');
  v_hash := encode(extensions.digest(v_token, 'sha256'), 'hex');
  v_exp := now() + interval '7 days';

  insert into public.household_invites (
    household_id, created_by, token_hash, label, status, expires_at
  ) values (
    p_household_id, v_uid, v_hash, left(trim(coalesce(p_label, '')), 40), 'pending', v_exp
  );

  return jsonb_build_object(
    'token', v_token,
    'expires_at', v_exp,
    'household_id', p_household_id
  );
end;
$$;

revoke all on function public.create_household_invite(uuid, text) from public;
grant execute on function public.create_household_invite(uuid, text) to authenticated;

-- ---------------------------------------------------------------------------
-- RPC: accept invite
-- ---------------------------------------------------------------------------
create or replace function public.accept_household_invite(p_token text)
returns jsonb
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_uid uuid := auth.uid();
  v_hash text;
  v_inv public.household_invites;
  v_hname text;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;
  if p_token is null or length(trim(p_token)) < 32 then
    raise exception 'Invalid invite code';
  end if;

  v_hash := encode(extensions.digest(trim(p_token), 'sha256'), 'hex');

  select * into v_inv
  from public.household_invites
  where token_hash = v_hash
  for update;

  if not found then
    raise exception 'Invite not found or invalid';
  end if;
  if v_inv.status <> 'pending' then
    raise exception 'Invite is no longer valid';
  end if;
  if v_inv.expires_at <= now() then
    update public.household_invites set status = 'expired' where id = v_inv.id;
    raise exception 'Invite has expired';
  end if;
  if v_inv.created_by = v_uid then
    raise exception 'You cannot accept your own invite';
  end if;
  if public.is_household_member(v_inv.household_id, v_uid) then
    raise exception 'Already a member of this household';
  end if;

  if exists (select 1 from public.household_members m where m.user_id = v_uid) then
    raise exception 'Leave your current household before joining another';
  end if;

  insert into public.household_members (household_id, user_id, role, display_name)
  values (
    v_inv.household_id,
    v_uid,
    'member',
    coalesce(
      (select nullif(trim(p.display_name), '') from public.profiles p where p.id = v_uid),
      (select split_part(u.email, '@', 1) from auth.users u where u.id = v_uid),
      'Member'
    )
  );

  update public.household_invites
  set status = 'accepted',
      accepted_by = v_uid,
      accepted_at = now()
  where id = v_inv.id;

  select name into v_hname from public.households where id = v_inv.household_id;

  return jsonb_build_object(
    'household_id', v_inv.household_id,
    'household_name', v_hname,
    'role', 'member'
  );
end;
$$;

revoke all on function public.accept_household_invite(text) from public;
grant execute on function public.accept_household_invite(text) to authenticated;

-- ---------------------------------------------------------------------------
-- RPC: leave household
-- ---------------------------------------------------------------------------
create or replace function public.leave_household(p_household_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_is_owner boolean;
  v_others int;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;
  if not public.is_household_member(p_household_id, v_uid) then
    raise exception 'Not a member';
  end if;

  v_is_owner := public.is_household_owner(p_household_id, v_uid);
  if v_is_owner then
    select count(*) into v_others
    from public.household_members
    where household_id = p_household_id and user_id <> v_uid;
    if v_others > 0 then
      raise exception 'Owner must remove other members before leaving, or delete the household';
    end if;
    delete from public.households where id = p_household_id;
    return jsonb_build_object('left', true, 'deleted_household', true);
  end if;

  delete from public.household_members
  where household_id = p_household_id and user_id = v_uid;

  return jsonb_build_object('left', true, 'deleted_household', false);
end;
$$;

revoke all on function public.leave_household(uuid) from public;
grant execute on function public.leave_household(uuid) to authenticated;

-- ---------------------------------------------------------------------------
-- RPC: list my households
-- ---------------------------------------------------------------------------
create or replace function public.list_my_households()
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_result jsonb;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;

  select coalesce(jsonb_agg(row_data), '[]'::jsonb) into v_result
  from (
    select jsonb_build_object(
      'id', h.id,
      'name', h.name,
      'owner_id', h.owner_id,
      'is_owner', h.owner_id = v_uid,
      'members', (
        select coalesce(jsonb_agg(
          jsonb_build_object(
            'user_id', m.user_id,
            'role', m.role,
            'display_name', m.display_name,
            'email', p.email,
            'joined_at', m.joined_at
          ) order by m.joined_at
        ), '[]'::jsonb)
        from public.household_members m
        left join public.profiles p on p.id = m.user_id
        where m.household_id = h.id
      )
    ) as row_data
    from public.households h
    where public.is_household_member(h.id, v_uid)
  ) q;

  return v_result;
end;
$$;

revoke all on function public.list_my_households() from public;
grant execute on function public.list_my_households() to authenticated;

-- Done. In Harbor: Household → Create invite for partner.
