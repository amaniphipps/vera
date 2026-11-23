---
name: learn-a-system
description: Use when the user approves studying a connected app or API. Map its endpoints, auth, and data shapes, write the system into the knowledge graph, and draft a working skill into skills-live/.
---

# Learn a System

This is how Vera gets good at a system nobody taught her. You point her at a
connected app or API, she studies it, and she drafts her own skill for it.
The output is never trusted by default: everything lands in quarantine and
goes through the normal vetting flow before it can touch production systems.

## The golden rule: ask first

Never study a system uninvited. The trigger is always an explicit yes to the
permission question:

"Want me to study how this system works? I will map its endpoints, auth, and
data shapes, and draft a skill so I can use it properly next time. It takes a
few minutes and I will show you everything I find."

Consent is per system. A yes for the CRM is not a yes for the billing tool.

## The flow

### 1. Frame the questions
Before touching anything, write down what the study must answer:
- What is this system for, in one sentence?
- How does auth work (type only: OAuth, API key, session, other - never the
  secret values)?
- What are the core objects and their shapes?
- What are the read paths a skill would use most?
- What can it NOT do (rate limits, missing endpoints, gotchas)?

### 2. Gather evidence
Use the cheapest honest source first, escalate only as needed:
1. Official docs and OpenAPI specs, when they exist.
2. **Graphify structural scout** when the connected system includes a repo, SDK, dbt/SQL warehouse models, CSV packs, or multi-file specs/playbooks (>5 files):
   - If `graphify` / `graphify-mcp` is not yet configured and the user wants Vera to map this corpus, explain in one line what will be installed (`uv` + isolated Python 3.12 + `graphifyy[mcp]`, leaving system Python untouched) and on confirmation run `setup/install_graphify.sh --runtime <runtime>`.
   - Default to `--code-only` (`GRAPHIFY_BACKEND=none`) for local tree-sitter AST extraction. Ask explicit approval (`graphify-semantic-pass`) before sending private docs, PDFs, or images to an LLM backend.
   - Query `god_nodes`, `get_community`, `query_graph`, and `shortest_path` instead of grepping raw files. Spot-check `EXTRACTED` file/line citations before treating them as `confirmed`; keep `INFERRED` / `AMBIGUOUS` edges marked `inferred` / `unknown`.
   - Skip Graphify for single-endpoint SaaS APIs with no code or multi-doc corpus.
3. Small, safe live reads against the connected tool (list one record, describe
   one object). Read-only always.
4. Runtime observation with the REA MCP when the surface is a web app with no
   usable docs: browser scenario capture and network-capture inspection. REA
   output is evidence, not truth - record its stated limitations.
5. Static analysis (the analyze-an-app skill) only when the target is a
   JS/Electron app with no documented API.

Respect every rate limit. Batch nothing aggressive. A study is a guest visit,
not a load test.

### 3. Write the tactical map (ontology entry)
Create or update `knowledge/graph/entities/systems/<slug>.yaml`. The entry is
a tactical map of the system, not just a spec sheet:
- **Purpose and owner** - what it's for in one sentence; who owns it (if known).
- **Who uses it** - the kinds of people and teams observed or documented
  ("used by ops people who live in it daily" vs "execs read dashboards").
- **Use cases** - what people actually do in it, in their terms.
- **Conventions** - naming patterns, stage/status vocabularies, required-field
  habits, the way THIS instance is configured (custom objects, custom fields,
  naming quirks). Generic product docs never cover these; they are the part
  worth studying.
- **Instance structure** - core objects with field shapes, base endpoints
  (references, not secrets), auth model class, known limitations.
Every claim carries its evidence - follow the evidence-trail format. Facts
come from verified reads only, never from chat assertions alone. When Graphify
is available, refresh its index over `knowledge/graph/` (into
`knowledge/graph/.graphify-out/`, gitignored) so the new system connects to
existing glossary, business, and system records for cross-system queries. When
you report back, regurgitate the map in plain language: "here's who uses this,
here's what for, here's how your instance is put together."

### 4. Draft the skill
Write a draft integration skill into `skills-live/<system-slug>/`:
- `SKILL.md` - the procedure as observed: how to answer the common questions
  with this system, with the pitfalls you actually hit.
- `org.example.yaml` - every org-specific value (endpoints, object names,
  field quirks) as a documented slot.
- `skill.yaml` - manifest with `tier: draft`, `scope: read-only`,
  `secret_policy: helper-mediated` if credentials are involved, and
  provenance: `origin: rea-analysis` or `live-learning`, with evidence paths.
- Mark `status: unreviewed` in the frontmatter.

### 5. Report and hand off
Show the user everything: the ontology entry, the draft skill, the evidence,
and the limitations in plain language. Note that the draft is quarantined
(read-only, no secrets, no external writes) until the nightly vetting pass
and their review. The skill-vetter takes it from there.

## Hard rules

1. Read-only during studies. No writes to the target system, ever.
2. Never record secret values. Auth gets described by type, not by content.
3. Evidence or it did not happen. Every claim in the ontology entry cites a
   read, a doc, or an observation.
4. Limitations are part of the deliverable. State what you could not verify.
5. One system per study. Finish, report, then ask about the next.

Uses the REA MCP (https://github.com/morluto/rea, MIT) for observation and
static analysis. Vera works without it; steps 3+ degrade to docs-and-reads
only.
