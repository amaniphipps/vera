# Vera memory — working profile and multi-store memory

Two layers, one policy: memory is reviewable data with provenance. The
registry supports any number of connected stores; this install currently
enables local files only.

## Layers

**Working profile — `profile.md`.** The fast cache. Who the admin is, how
they work, the current state of the work. Loaded into every OpenCode
session via the `instructions` array in the project's `opencode.jsonc`.
Budget ~5–6k characters. Curate it: when it grows past budget, promote
stable facts to durable entries and cut the rest.

**Durable store — `durable/`.** The long-term ledger. One YAML file per
fact, shaped by `schemas/memory-entry.yaml` (fact, category, confidence,
source, first_seen, last_confirmed, expiry). Read back to the admin before
admitting any entry. Facts from draft-tier (skills-live/) skills never
enter durable memory — only hardened-skill output or confirmed admin
statements qualify.

**Knowledge graph — `../knowledge/graph/`.** Structured org map: systems,
people, glossary, business entities, with evidence. Separate from durable
memory: graph = verified structure, durable = learned facts and decisions.

**Store registry — `stores.yaml`.** Any number of stores may be enabled:
local files, Obsidian, Hindsight, Supabase, or future connectors. The working
profile is always the fast cache. When history matters, read every enabled
relevant store, retain which store supplied each fact, and ask the user to
resolve conflicts. Writes go to the confirmed default store unless the user
routes them elsewhere; stores marked read-only are never written. Disabled
or unavailable stores are named honestly, never pretended into the result.
`stores.example.yaml` is the committed template; the active registry is
deployment-specific and git-ignored.

## Rules

1. Nothing secret enters any memory file. Provider keys live in `.env`.
2. People records follow `schemas/people-profile.yaml` — no comp,
   performance, or HR classes, by schema and by policy.
3. The working profile is rewritten, not appended. Each session may update
   it; stale lines get cut.
4. Durable entries carry sources. No source, no entry.
5. `supabase/` and `schemas/` ship as templates. The active store on this
   install is local files (decision 2026-11-22); Hindsight config in
   `.hermes/` belongs to the old Hermes install and is unused here.
6. Names are asked for, never inferred from accounts or machine metadata.
   Durable name/preference entries use confirmed statements and read-back.
   Correction and forgetting apply across every enabled store.
