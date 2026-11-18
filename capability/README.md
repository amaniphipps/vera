# Capability acquisition

Optional module. Vera works fully without it.

This module adds REA (Reverse Engineer Anything) as an MCP plugin. It lets Vera
observe apps and connected systems she cannot read the source of. The
`learn-a-system` skill orchestrates the work; REA is one of its evidence
sources.

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

## The procedure

- **learn-a-system** (`skills/capability-acquisition/`). With approval, it maps
  a connected app's endpoints, auth, and data shapes, writes the system into
  the knowledge graph, and drafts a skill into `skills-live/`. It uses REA for
  runtime observation and static analysis when docs and live reads are not
  enough. Without REA it degrades to docs-and-reads only.
- **analyze-connector** (`capability/workflows/`). The same procedure written
  as the concrete step sequence: approval first, observation, an ontology
  write, and a draft skill handed to the vetter.

## Safety posture

Analysis output is never auto-trusted.

Anything REA produces is evidence, not a conclusion. A draft it informs lands in
`skills-live/` in quarantine, marked `status: unreviewed`, and requires approval
per `policy/` before anything graduates into `skills/`. No analysis result
becomes a shipped skill without the skill-vetter pass and human review.

Uses the REA MCP (https://github.com/morluto/rea, MIT).
