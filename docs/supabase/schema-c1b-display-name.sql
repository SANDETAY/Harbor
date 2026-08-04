-- =============================================================================
-- Harbor C1b — Set my display name (household + profile)
-- Run in Supabase SQL Editor AFTER schema-c1-household.sql
-- Safe to re-run.
-- =============================================================================

create or replace function public.set_my_display_name(p_name text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_name text;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;

  v_name := left(trim(coalesce(p_name, '')), 40);
  if length(v_name) < 1 then
    raise exception 'Enter a name';
  end if;
  if position('@' in v_name) > 0 then
    raise exception 'Use a name, not an email address';
  end if;

  update public.profiles
  set display_name = v_name,
      updated_at = now()
  where id = v_uid;

  update public.household_members
  set display_name = v_name
  where user_id = v_uid;

  return jsonb_build_object('display_name', v_name);
end;
$$;

revoke all on function public.set_my_display_name(text) from public, anon;
grant execute on function public.set_my_display_name(text) to authenticated;

create or replace function public.rename_household(p_household_id uuid, p_name text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_name text;
begin
  if v_uid is null then
    raise exception 'Not authenticated';
  end if;
  if not public.is_household_owner(p_household_id, v_uid) then
    raise exception 'Only the owner can rename the household';
  end if;

  v_name := left(trim(coalesce(nullif(p_name, ''), 'Family')), 48);

  update public.households
  set name = v_name,
      updated_at = now()
  where id = p_household_id;

  return jsonb_build_object('id', p_household_id, 'name', v_name);
end;
$$;

revoke all on function public.rename_household(uuid, text) from public, anon;
grant execute on function public.rename_household(uuid, text) to authenticated;
