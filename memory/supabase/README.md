# Durable memory: Supabase shell

OPTIONAL. Vera works fully without this. The working profile (a small
local file) covers day-one use. This directory is the recommended path
when you want durable memory in a real database.

## Which memory option

| Option | When to pick it |
| --- | --- |
| Working profile only | Smallest setup. One user, short-term use. Facts live in a local file. |
| Supabase (this dir) | You want durable memory with SQL access and backups. |
| Hindsight | You want an existing durable-memory plugin that handles recall itself. |
| Obsidian | You want local-first markdown files you can read and edit by hand. |

Nothing is locked in at setup. Vera can move between these later.

## Setup

1. Create a Supabase project.
2. Open the SQL editor and run `schema.sql`.
3. Put the URL and service key in `.env`:

   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-service-role-key
   ```

4. Restart the agent. Vera reads and writes memory through these tables.

Use the service role key, not the anon key. Row-level security in
`schema.sql` grants access to the service role only.

## Without it

Vera keeps everything in the working profile and the local knowledge
graph. Memory still works; it just does not survive a wiped profile.