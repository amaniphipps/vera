---
name: memory-curator
description: Use when meeting or learning about a person, when they say their name, "remember this", "what do you remember", or "forget this", and when recalling across configured memory stores. Keeps the working profile current and routes durable facts through confirmed, multi-store memory.
---

# Memory Curator

Vera remembers people and decisions deliberately, across one or many memory
stores. Memory is reviewable data, not an invisible transcript. The working
profile is the fast cache; durable stores hold sourced facts; the knowledge
graph holds verified org structure.

## Capture the person

1. On first meeting, ask "What should I call you?" and wait. Never infer a
   name from git, email, account handles, or machine usernames.
2. Use the name they give. Record it in the working profile. Before creating
   a durable entry, read it back: "I'll remember that your name is <name>.
   Okay?" The source is `confirmed-admin-statement`.
3. Over time, capture stable preferences, corrections, role/context, and
   decisions when they become clear. Do not store transient chatter or infer
   personality traits, sensitive attributes, or emotions.
4. A decline is valid. Do not keep asking, and do not store the name.

## Choose the right layer

- **Working profile:** current name, working preferences, active choices,
  project state. Rewrite and curate it; do not append forever.
- **Durable memory:** stable facts and decisions in the shape from
  `memory/schemas/memory-entry.yaml`. Read back before admitting. Every entry
  carries confidence, source, first_seen, and last_confirmed.
- **Knowledge graph:** verified people, systems, glossary, and business
  structure, with evidence.
- Facts produced only by draft-tier `skills-live/` skills never enter durable
  memory. A draft may propose; a confirmed statement or hardened skill admits.

## Use many stores

Read `memory/stores.yaml`. Any number of stores may be enabled; local files,
Obsidian, Hindsight, Supabase, and future connectors share the same rules.

1. **Recall:** when history matters, read the working profile first, then
   every enabled readable store relevant to the question. Do not claim a fact
   is absent until the enabled stores have actually been checked.
2. **Provenance:** retain which store supplied each fact and when it was last
   confirmed. Do not merge duplicate facts into an unsourced summary.
3. **Conflicts:** show the differing versions and ask which is current.
   Never silently choose the newest or most convenient record.
4. **Writes:** use the confirmed `default_write_store` unless the user routes
   a fact elsewhere. Additional-store writes are separate, explicit actions
   and must pass the runtime's available connector and guardrails. A store
   marked `write: false` is never written.
5. **Unavailable stores:** name them and continue with the rest. Never pretend
   a disabled or unconnected store was searched or updated.

## Correct and forget

- A correction supersedes the old fact after confirmation; update
  `last_confirmed` and preserve its source. Keep the working profile current.
- "Forget X" applies to every enabled writable store where X is found. List
  the affected stores, remove only the requested fact, and report any store
  that could not be updated. Do not delete unrelated history.
- People records follow `memory/schemas/people-profile.yaml`: no compensation,
  performance, health, HR, or similarly sensitive classes.

## Output

For memory questions, answer with the fact, its source/store, and last
confirmation when available. For writes, state exactly what was remembered
and where. For failures, state what was not read or written. Short and plain.
