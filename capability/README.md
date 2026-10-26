# Capability acquisition

Optional module. Vera works fully without it.

This module adds REA (Reverse Engineer Anything) as an MCP plugin. It lets Vera
analyze apps and connected systems she cannot read the source of. Three
capability-acquisition skills and one workflow ride on top of it.

## What it is

REA is a third-party MCP server for reverse engineering. Vera's integration is
an instruction layer only. REA is not forked or vendored here. This repo calls
its MCP tools by name and credits it.

## Enabling

1. Set `REA_ENABLED=true` in `.env`.
2. Register the REA MCP server in your Hermes MCP config. A stdio snippet is in
   `mcp.rea.json`. The exact shape depends on the host. Verify against the REA
   docs before trusting it: run `npx -y rea-agents@latest doctor`, or see
   https://github.com/morluto/rea.
3. Restart the agent. Confirm the REA tools appear in the session.

Static JavaScript analysis needs no native engine. Native targets need Ghidra,
Hopper, or IDA separately, which this module does not install.

## The capability-acquisition procedures

Under `skills/capability-acquisition/`:

- **analyze-an-app**. Static JavaScript/Electron analysis. When to use it, the
  summary-first flow, the CLI fallback, and how to report with evidence and
  limitations. Native binaries, Android, and firmware are out of scope.
- **evidence-trail**. The house standard for "how does this system work"
  answers. Every claim carries evidence, confidence, a search boundary, and open
  unknowns in a reusable finding ledger.
- **learn-a-system**. The orchestrator. With approval, it maps a connected app's
  endpoints, auth, and data shapes, writes the system into the knowledge graph,
  and drafts a skill into `skills-live/`. It calls the two skills above.

Under `capability/workflows/`:

- **analyze-connector**. The end-to-end procedure for studying a newly connected
  system: approval first, runtime observation, an ontology write, and a draft
  skill handed to the vetter.

## Safety posture

Analysis output is never auto-trusted.

Anything REA produces is evidence, not a conclusion. A draft it informs lands in
`skills-live/` in quarantine, marked `status: unreviewed`, and requires approval
per `policy/` before anything graduates into `skills/`. No analysis result
becomes a shipped skill without the skill-vetter pass and human review.

Uses the REA MCP (https://github.com/morluto/rea, MIT).