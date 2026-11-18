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

## 2. Observe the runtime

Where the system has a browser, web, or Electron surface, use REA's runtime
tools to watch behavior: page traffic, endpoints called, data shapes that move.
Where it is a static artifact, use REA's static-analysis tools.

Capture evidence as you go. Every observation gets a tool, target, timestamp or
ID, a confidence level, and a search boundary - the evidence standard the
learn-a-system skill defines.

## 3. Write the ontology

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

## 4. Draft the skill

Draft a skill for the system into `skills-live/`, following the skill-vetter
format. Mark its frontmatter `status: unreviewed`. Do not edit `skills/`
directly.

Hand the draft to the skill-vetter flow. Nothing graduates to `skills/` without
vetting and human approval.

Output is ready to forward as-is.

Uses the REA MCP (https://github.com/morluto/rea, MIT).