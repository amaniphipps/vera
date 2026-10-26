-- Vera durable-memory database shell (Postgres / Supabase).
-- OPTIONAL. Vera works fully without a database. This is the recommended
-- shell when you want durable memory that survives restarts and redeploys.
--
-- Run once, in the Supabase SQL editor or via psql.

-- ── memory_entries ─────────────────────────────────────────────
-- One row per durable-memory fact. Mirrors memory/schemas/memory-entry.yaml.
create table if not exists memory_entries (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),   -- when the fact was admitted
  category text not null,                          -- user-preference | org-fact | system-fact | contact-fact | decision
  content text not null,                           -- the fact, one line, plain
  source text not null,                            -- where it came from (admin statement, API read)
  confidence text not null default 'medium'        -- high | medium | low
);

-- ── people_profiles ────────────────────────────────────────────
-- What Vera may hold about a person. Hard-excluded classes (comp,
-- performance, HR) have no columns here and never will.
create table if not exists people_profiles (
  id uuid primary key default gen_random_uuid(),
  display_name text not null,
  role text,
  team text,
  timezone text,
  preferences jsonb default '{}'::jsonb           -- work preferences + communication style
);

-- ── entities ──────────────────────────────────────────────────
-- The knowledge graph's generic entity store. kind separates people,
-- systems, glossary, and business nodes; data holds the typed payload.
create table if not exists entities (
  id uuid primary key default gen_random_uuid(),
  kind text not null,                             -- person | system | glossary | business
  slug text not null unique,                      -- stable machine name, e.g. "person-jane-example"
  data jsonb default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- ── Row-level security ────────────────────────────────────────
-- Every table is locked to the service role. The anon and public roles see
-- nothing. Point the app at the service key, never the anon key.
alter table memory_entries enable row level security;
alter table people_profiles enable row level security;
alter table entities enable row level security;

-- Policy stub: service role only. In Supabase the service role bypasses
-- RLS by default; these policies state the intent so any non-service role
-- added later stays locked out.
create policy "service role only: memory_entries"
  on memory_entries for all
  to service_role
  using (true) with check (true);

create policy "service role only: people_profiles"
  on people_profiles for all
  to service_role
  using (true) with check (true);

create policy "service role only: entities"
  on entities for all
  to service_role
  using (true) with check (true);