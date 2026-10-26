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
- How does auth work (type only: OAuth, API key, session, other — never the
  secret values)?
- What are the core objects and their shapes?
- What are the read paths a skill would use most?
- What can it NOT do (rate limits, missing endpoints, gotchas)?

### 2. Gather evidence
Use the cheapest honest source first, escalate only as needed:
1. Official docs and OpenAPI specs, when they exist.
2. Small, safe live reads against the connected tool (list one record, describe
   one object). Read-only always.
3. Runtime observation with the REA MCP when the surface is a web app with no
   usable docs: browser scenario capture and network-capture inspection. REA
   output is evidence, not truth — record its stated limitations.
4. Static analysis (the analyze-an-app skill) only when the target is a
   JS/Electron app with no documented API.

Respect every rate limit. Batch nothing aggressive. A study is a guest visit,
not a load test.

### 3. Write the ontology entry
Create or update `knowledge/graph/entities/systems/<slug>.yaml`:
- purpose, owner (if known), auth model class, base endpoints (references,
  not secrets), core objects with field shapes, known limitations, and links
  to the evidence you gathered. Every claim carries its evidence — follow the
  evidence-trail format. Facts come from verified reads only, never from chat
  assertions alone.

### 4. Draft the skill
Write a draft integration skill into `skills-live/<system-slug>/`:
- `SKILL.md` — the procedure as observed: how to answer the common questions
  with this system, with the pitfalls you actually hit.
- `org.example.yaml` — every org-specific value (endpoints, object names,
  field quirks) as a documented slot.
- `skill.yaml` — manifest with `tier: draft`, `scope: read-only`,
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
