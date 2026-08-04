-- Harbor Pro — Supabase schema (Phase B)
-- Run in Supabase SQL editor after creating a project.
-- Safe to re-run (drop policy if exists).
-- RLS: users only access their own rows.

-- Profiles (1:1 with auth.users)
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

-- Auto-create profile on signup (Apple/Google/email)
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
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
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Full-state cloud snapshot (backup / multi-device)
-- payload = export JSON (same shape as Export Profile)
create table if not exists public.harbor_snapshots (
  user_id uuid primary key references auth.users (id) on delete cascade,
  device_id text,
  schema_version int not null default 1,
  payload jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.harbor_snapshots enable row level security;

drop policy if exists "snapshots_select_own" on public.harbor_snapshots;
create policy "snapshots_select_own"
  on public.harbor_snapshots for select
  using (auth.uid() = user_id);

drop policy if exists "snapshots_insert_own" on public.harbor_snapshots;
create policy "snapshots_insert_own"
  on public.harbor_snapshots for insert
  with check (auth.uid() = user_id);

drop policy if exists "snapshots_update_own" on public.harbor_snapshots;
create policy "snapshots_update_own"
  on public.harbor_snapshots for update
  using (auth.uid() = user_id);

drop policy if exists "snapshots_delete_own" on public.harbor_snapshots;
create policy "snapshots_delete_own"
  on public.harbor_snapshots for delete
  using (auth.uid() = user_id);

-- Household shells (membership/invites in schema-c1-household.sql)
create table if not exists public.households (
  id uuid primary key default gen_random_uuid(),
  name text,
  owner_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default now()
);

create table if not exists public.household_members (
  household_id uuid not null references public.households (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  role text not null default 'member' check (role in ('owner', 'member')),
  primary key (household_id, user_id)
);

alter table public.households enable row level security;
alter table public.household_members enable row level security;

-- Optional: index for updated_at queries
create index if not exists harbor_snapshots_updated_at_idx
  on public.harbor_snapshots (updated_at desc);
