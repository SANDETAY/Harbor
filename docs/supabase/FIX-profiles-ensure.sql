-- =============================================================================
-- Harbor — ensure profiles rows exist for every auth user
--
-- Why you might see no rows in Table Editor → profiles after Apple/Google sign-in:
--   1) You looked at "profiles" but the login only created auth.users
--   2) schema.sql trigger on_auth_user_created was never applied
--   3) RLS insert policy missing so the app can't self-heal
--
-- Run in: Supabase → SQL Editor → New query → paste all → Run
-- Safe to re-run.
-- =============================================================================

-- 1) Table (no-op if already exists)
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  display_name text,
  is_pro boolean not null default false,
  pro_until timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

-- 2) Policies: own row select / insert / update
drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own"
  on public.profiles for select
  using (auth.uid() = id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own"
  on public.profiles for insert
  with check (auth.uid() = id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
  on public.profiles for update
  using (auth.uid() = id);

-- 3) Trigger: every new auth.users row → profiles
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, display_name)
  values (
    new.id,
    new.email,
    coalesce(
      new.raw_user_meta_data->>'full_name',
      new.raw_user_meta_data->>'name',
      split_part(coalesce(new.email, ''), '@', 1)
    )
  )
  on conflict (id) do update
    set email = coalesce(excluded.email, public.profiles.email),
        updated_at = now();
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- 4) Backfill: anyone already in Auth but missing from profiles
insert into public.profiles (id, email, display_name)
select
  u.id,
  u.email,
  coalesce(
    u.raw_user_meta_data->>'full_name',
    u.raw_user_meta_data->>'name',
    split_part(coalesce(u.email, ''), '@', 1)
  )
from auth.users u
on conflict (id) do update
  set email = coalesce(excluded.email, public.profiles.email),
      updated_at = now();

-- 5) Sanity check (optional — shows counts in Results)
select
  (select count(*) from auth.users) as auth_users,
  (select count(*) from public.profiles) as profiles;
