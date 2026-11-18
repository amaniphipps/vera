# Connecting tools

Vera gets useful when she can read your systems. Two kinds of connections,
both optional, both reversible.

## 1. MCP servers (packaged connectors)

The runtime supports MCP servers - packaged tool connectors with their own
auth. Adding one is a few lines of config plus an auth step, then a restart.

1. Pick the server for your tool (check what your Hermes install supports:
   `hermes mcp --help`).
2. Register it in your Hermes MCP config and complete its auth flow.
3. Restart the agent and confirm the new tools appear in-session.
4. First call is always a small, safe read.

## 2. Plain REST APIs

Anything with an HTTP API works. The pattern is a small helper script so
credentials stay out of the conversation:

- Copy `skills/templates/api-integration/` as the starting shape.
- Keys go in `.env` or your platform secret store - never in chat, never in a
  skill file. Paste them into your own terminal, not to Vera.
- Vera calls the helper; the helper holds the credential.

## The study question

After connecting, Vera will ask (once per system, verbatim shape):

> "Want me to study how this system works? I will map its endpoints, auth, and
> data shapes, and draft a skill so I can use it properly next time."

- **Yes** - she runs her `learn-a-system` skill: maps the system into
  `knowledge/graph/entities/systems/`, drafts a skill into `skills-live/`
  marked `status: unreviewed`. Nothing graduates into `skills/` without the
  nightly vetter plus your explicit approval.
- **No** - she uses the tool plainly and moves on. Consent is per system and
  never carries over.

## Rules that always apply

1. Read-only first. Writes to any connected system need your per-action yes
   until you grant standing writes in `policy/guardrails.yaml`.
2. A failed connection gets fixed before moving on - a half-connected tool is
   worse than none.
3. Skills from other agents (plain markdown) can drop into `skills-live/` and
   enter the same vetting flow.
4. Guardrails in `policy/guardrails.yaml` apply on every platform and every
   tool, enforced the same way.
