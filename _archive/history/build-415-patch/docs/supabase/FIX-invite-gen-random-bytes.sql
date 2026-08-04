-- =============================================================================
-- Harbor hotfix — Create invite fails: gen_random_bytes(integer) does not exist
--
-- Cause: On Supabase, pgcrypto lives in schema `extensions`. Our SECURITY DEFINER
-- RPCs used `set search_path = public`, which hides gen_random_bytes() / digest().
--
-- Fix: include `extensions` in search_path and call extensions.* explicitly.
--
-- Run in: Supabase → SQL Editor → New query → paste all → Run
-- Safe to re-run.
-- =============================================================================

create extension if not exists pgcrypto with schema extensions;


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

  -- Cap pending invites per household (abuse / spam)
  if (
    select count(*) from public.household_invites i
    where i.household_id = p_household_id
      and i.status = 'pending'
      and i.expires_at > now()
  ) >= 10 then
    raise exception 'Too many pending invites — revoke some first';
  end if;

  -- Fully qualify in case search_path is stripped by a host policy
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

  -- C1: user can only belong to one household at a time
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
