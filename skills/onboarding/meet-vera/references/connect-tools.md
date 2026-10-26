# Connecting tools - the walkthrough

## Presenting the options

Two kinds of connections:

1. **MCP servers** - packaged tool connectors. The user picks from what their
   runtime supports; each one is a few lines of config plus an auth step.
2. **Plain REST APIs** - anything with an HTTP API. These get a small helper
   script (the api-integration template) so credentials stay out of the
   conversation.

Walk through ONE connection live, whichever the user picks. Show each step
before taking it. Confirm it works with a real read, not a guess.

## The permission question (always ask, verbatim shape)

"Want me to study how this system works? I will map its endpoints, auth, and
data shapes, and draft a skill so I can use it properly next time. It takes a
few minutes and I will show you everything I find."

- On yes: run the study (the capability-acquisition skills handle method),
  write the system into `knowledge/graph/entities/systems/`, and draft the
  skill into `skills-live/` marked `status: unreviewed`.
- On no: note it, connect the tool plainly, move on.
- Ask again for each new system. Past consent does not carry over.

## Rules

1. Secrets go in `.env` or the platform secret store, never in chat. The user
   pastes keys into their own terminal, not to you.
2. First call after connecting is always a small, safe read.
3. If the connection fails, troubleshoot with the user before moving on. A
   half-connected tool is worse than none.
4. Suggest, do not prescribe: if they have skills from other agents as
   markdown files, those can drop into `skills-live/` and enter the normal
   vetting flow.
