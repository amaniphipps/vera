# Capability acquisition

Optional capability modules. Vera works without them and provisions them on demand when you ask her to study a system.

This folder covers two complementary tools:

1. **REA (Reverse Engineer Anything)** — runtime observation and static JS/Electron analysis for web apps and tools whose source you cannot read (`mcp.rea.json`).
2. **Graphify** — deterministic tree-sitter AST + schema + documentation knowledge-graph engine (`mcp.graphify.json`). Indexes codebases, SQL/dbt models, OpenAPI/CSV schemas, docs, and `knowledge/graph/` itself into a queryable graph (`graph.json`) so Vera traverses dependencies instead of grepping raw files.

## What they are

Both integrations are instruction and provisioning layers. Neither tool is forked or vendored here; Vera invokes their CLI/MCP tools by name and credits upstream (`morluto/rea`, MIT; `Graphify-Labs/graphify`, Apache-2.0 / MIT).

## Enabling

### Graphify (recommended for repos, data warehouses, and multi-doc systems)

Graphify requires Python `3.11.5–3.14`. Rather than touching your system Python, Vera uses **`uv`** to install an isolated Python `3.12` + `graphifyy[mcp]`:

```bash
./setup/install_graphify.sh --runtime opencode --repo /path/to/vera
# or during Hermes setup:
./setup/setup.sh --with-graphify
```

When a user asks Vera to study a codebase or multi-file system and Graphify is missing, Vera offers to run `setup/install_graphify.sh` on the spot so non-technical users do not have to configure Python environments by hand.

### REA (for SaaS web apps without source)

1. Set `REA_ENABLED=true` in `.env`.
2. Register the REA MCP server from `mcp.rea.json` (verify with `npx -y rea-agents@latest doctor`, or see https://github.com/morluto/rea).
3. Restart / reload the agent and confirm the REA tools appear.

## Two-graph model for `knowledge/graph/`

- **`knowledge/graph/entities/` & `evidence/`** stay human-readable, git-diffable YAML and Markdown files where per-record policies (such as excluding HR/comp data from `people/`) are enforced.
- **Graphify** indexes `knowledge/graph/` alongside studied system docs/code into `knowledge/graph/.graphify-out/graph.json`, turning the folder into a real traversable graph (`query_graph`, `shortest_path`, `god_nodes`).

## The capability-acquisition procedures

Under `skills/capability-acquisition/`:

- **analyze-an-app** — Static JavaScript/Electron analysis via REA.
- **evidence-trail** — House standard for "how does this system work" answers: every claim carries evidence, confidence (`confirmed` / `inferred` / `unknown`), search boundary, and open unknowns.
- **learn-a-system** — Orchestrator: asks consent, scopes the target (using Graphify when the system has code/schemas/multi-file docs, OpenAPI/live reads/REA otherwise), writes the tactical map into `knowledge/graph/`, refreshes the Graphify index, and drafts a quarantined skill into `skills-live/`.

Under `capability/workflows/`:

- **analyze-connector** — Concrete step sequence for studying a newly connected system.

## Safety posture

Analysis output is never auto-trusted.

- Graphify defaults to `--code-only` (`GRAPHIFY_BACKEND=none`) so local AST extraction sends nothing off-machine. Running Pass 3 semantic extraction over private docs requires explicit approval (`graphify-semantic-pass` in `policy/guardrails.example.yaml`).
- Anything REA or Graphify produces is evidence, not automatic truth. Graphify `INFERRED` / `AMBIGUOUS` edges never enter `knowledge/graph/` as `confirmed` without spot-check verification.
- Draft skills land in `skills-live/` in quarantine (`status: unreviewed`) and require `skill-vetter` + human approval before graduating into `skills/`.
