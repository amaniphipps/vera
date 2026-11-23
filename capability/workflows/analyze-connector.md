# Analyze a connector

End-to-end procedure for studying a newly connected system. The goal is a record
in `knowledge/graph/entities/systems/<slug>.yaml` plus a draft skill under
`skills-live/`. Not a finished skill. Promotion is a separate, reviewed step.

This procedure is what the `learn-a-system` skill orchestrates, written here as
the concrete step sequence.

## 1. Approval first

Before any inspection, answer the permission question and get a yes:

- Are we authorized to examine this system?
- Do its license or terms allow this analysis?
- Does `policy/guardrails` allow the read and write surfaces this will touch?

No approval, no analysis. Record the approval (who, when, scope) with the rest
of the evidence trail.

## 2. Gather structural & runtime evidence

### 2a. Structural graph scout (Graphify — when system has code, schemas, or multi-file docs)

Where the connected system exposes a repo, SDK, dbt/SQL warehouse models, CSV
specs, or multi-file Markdown/PDF documentation:

- If `graphify` / `graphify-mcp` is missing and the user approves setup, run
  `setup/install_graphify.sh --runtime <runtime>` (isolated `uv` + Python 3.12).
- Run `--code-only` first (`GRAPHIFY_BACKEND=none`) into
  `knowledge/graph/evidence/<slug>/graphify-out/` so AST extraction stays local.
  Ask explicit approval (`graphify-semantic-pass`) before sending private docs
  to an LLM backend.
- Query `god_nodes`, `query_graph`, and `shortest_path`, then spot-check cited
  `source_file:source_location` lines before promoting `EXTRACTED` claims.

### 2b. Observe the runtime (REA — when system is a SaaS web/Electron app)

Where the system has a browser, web, or Electron surface, use REA's runtime
tools to watch behavior: page traffic, endpoints called, data shapes that move.
Where it is a static artifact, use the analyze-an-app skill or the matching REA
tool.

Capture evidence as you go. Every observation gets a tool, target, timestamp or
ID, and a confidence level. Follow the evidence-trail standard.

## 3. Write & index the ontology

Record what you learned into a YAML file:

```
knowledge/graph/entities/systems/<slug>.yaml
```

Use the system's slug (lowercase, hyphens). Include at least:

- identity: name, slug, homepage, docs.
- interfaces: endpoints, methods, auth, data shapes observed.
- evidence: IDs or timestamps backing each claim.
- unknowns: what was not observed or not established.
- status: unreviewed.

When Graphify is enabled, refresh the graph index over `knowledge/graph/`
(`knowledge/graph/.graphify-out/`) so the new system connects to existing
glossary, business, and system records.

## 4. Draft the skill

Draft a skill for the system into `skills-live/`, following the skill-vetter
format. Mark its frontmatter `status: unreviewed`. Do not edit `skills/`
directly.

Hand the draft to the skill-vetter flow. Nothing graduates to `skills/` without
vetting and human approval.

Output is ready to forward as-is.

Uses the REA MCP (https://github.com/morluto/rea, MIT).