# Graphify integration plan for Vera (rev 2)

**Repo:** `github.com/amaniphipps/vera`  
**Branch:** `feature/runtime-adaptive-onboarding` (or follow-on branch after PR 2)  
**Status:** draft plan · rev 2 · 2026-11-22  
**Review surface:** Plannotator  
**Upstream reference:** `https://github.com/Graphify-Labs/graphify` (`graphifyy` on PyPI, Apache-2.0 / MIT)

---

## 1. Feedback resolutions in rev 2

| Plannotator annotation | Design change in rev 2 |
|---|---|
| **1. Open-source audience challenge:** *"Would this actually work for anyone? People will download from a variety of backgrounds."* | Explicitly separates **two user realities**: (a) **Non-technical RevOps operators** connecting SaaS APIs/web apps (HubSpot, Stripe, ChurnZero) with no codebase — Graphify only runs when there is a multi-file corpus (docs, PDFs, OpenAPI/SQL schemas, CSV packs, dbt, or code), and skips silently for single-API SaaS connectors; (b) **Technical RevOps / builders** with repos, warehouses, and runbooks — Vera handles all setup automatically. Also adds a zero-manual-config installer (`setup/install_graphify.sh` via `uv` standalone Python 3.12) + Docker preinstall so users never debug Python versions or hand-edit JSON. |
| **2. `knowledge/graph/` vs. Graphify:** *"Why shouldn't this replace? What is this anyway?"* | Explains honestly what `knowledge/graph/` actually is today (a folder of hand-written YAML/Markdown files with **no graph engine**) and turns Graphify into the **query/traversal engine *over* `knowledge/graph/` + connected system docs/code**, rather than keeping two isolated islands. Keeps YAML/MD files only for human-editable, policy-checked records (`people-profile.yaml` HR exclusions, `systems/<slug>.yaml` tactical maps), while Graphify builds the traversable graph across them. |
| **3. Tool provisioning:** *"This is one of Vera's tools, and Vera should configure it as necessary to support the work the user requests."* | Replaces passive "degrade to INFO on Python 3.9.6" with **on-demand self-provisioning**: when a user asks Vera to study a codebase/docs/warehouse and `graphify` is missing or Python is `< 3.11.5`, Vera installs `uv` (which bundles isolated Python 3.12 without touching system Python) + `graphifyy[mcp]` and wires `graphify-mcp` into the active runtime (`opencode.jsonc` or `$HERMES_HOME/config.yaml`) after a one-line user confirmation. |

---

## 2. Audience reality check: who does this actually work for?

Because Vera is open source, people will download her across very different setups:

| User profile | What they connect to Vera | Does Graphify help? | What Vera actually does |
|---|---|---|---|
| **Non-technical RevOps lead** (macOS/Docker, connects HubSpot, Stripe, Slack, Google Sheets) | Live SaaS OAuth/API keys + web dashboards; usually **no local codebase** | **Only if** they drop a folder of PDFs, Notion/Markdown playbooks, CSV exports, or SQL/warehouse schemas | Uses OpenAPI/live read-only calls + REA for SaaS UIs. Does **not** force Graphify on a 1-API SaaS connection. If they hand Vera a folder of playbooks/PDFs/CSVs, Graphify indexes those automatically. |
| **GTM Engineer / RevOps Analyst** (has dbt, SQL warehouse models, Python/TS sync scripts, CRM migration packs) | Git repos, dbt models, sync scripts, data dictionaries, integration READMEs | **Yes — high value.** AST parsing is local and 0-token; traces metric & key lineage across code + docs | Runs `setup/install_graphify.sh` if missing, builds `graph.json`, queries `god_nodes` / `shortest_path` / `explain`, and drafts the connector skill into `skills-live/`. |
| **Docker / self-hosted admin** | `deploy/docker/Dockerfile` container | **Yes — zero setup** | Container ships `uv` + isolated Python 3.12 + `graphifyy[mcp]` preinstalled. |

**Bottom line:** Graphify should never be a hurdle for someone who just wants Vera to connect to HubSpot and run a pipeline review — and should configure itself cleanly the moment someone asks Vera to understand a repo, warehouse, or doc corpus.

---

## 3. What `knowledge/graph/` is today — and how Graphify fits

### What `knowledge/graph/` actually is right now
In this repo, `knowledge/graph/` is **not** a graph database. It is a structured directory of plain-text YAML and Markdown files:
- `knowledge/graph/entities/{systems,people,glossary,business}/*.yaml` (e.g., `entities/systems/widgetco-billing.yaml`)
- `knowledge/graph/evidence/*.md` (e.g., `evidence/widgetco-billing.md`)

Today, there is no query engine, no edge traversal, and no cross-file clustering over those files — Vera finds things in `knowledge/graph/` by listing directories and reading files.

### Why Graphify should *power* `knowledge/graph/` instead of deleting the YAML/Markdown files
- **Don't delete the YAML/Markdown source files:** `graphify-out/graph.json` is a generated 150KB+ NetworkX JSON blob. Humans cannot cleanly edit it, diff it in PRs, or enforce per-record guardrails on it (e.g., `memory/schemas/people-profile.yaml` banning comp/HR data, or `policy/guardrails.yaml` evidence provenance).
- **DO use Graphify as the graph engine *over* `knowledge/graph/` + connected system artifacts:**
  - Every time Vera finishes studying a system and writes `knowledge/graph/entities/systems/<slug>.yaml` + `evidence/<slug>.md` (or indexes a connected system's repo/docs), Graphify updates `knowledge/graph/.graphify-out/graph.json` across `knowledge/graph/` and the studied corpus.
  - Now `knowledge/graph/` actually **is** a queryable graph: Vera can traverse how a newly connected system (`hubspot`, `widgetco-billing`, `dbt-warehouse`) links to existing glossary terms, business metrics, and people already in `knowledge/graph/`.
  - `EXTRACTED` vs `INFERRED` tags remain intact, so Vera still distinguishes verified YAML/AST facts from inferred cross-links (`evidence-trail`).

---

## 4. Zero-friction provisioning (how Vera configures it for anyone)

On machines like macOS with only system Python `3.9.6` (no `brew`, no `uv`, no `pipx`), asking a user to "install Python 3.11.5–3.14 first" breaks open-source adoption.

**Solution:** Use **`uv`** (Astral's single-binary package/Python manager), which downloads a standalone, isolated Python `3.12` inside `~/.local/share/uv/` without touching `/usr/bin/python3` or requiring Homebrew/admin rights.

### `setup/install_graphify.sh` *(new helper)*
1. Checks if `graphify` and `graphify-mcp` already work on `PATH`. If yes, exits `0` immediately.
2. If `uv` is missing: installs `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`) and ensures `~/.local/bin` is on `PATH`.
3. Installs `graphifyy[mcp]` with isolated Python 3.12:
   ```bash
   uv tool install --python 3.12 "graphifyy[mcp]"
   ```
4. Wires the active runtime MCP config:
   - **OpenCode:** updates project/user `opencode.jsonc` (or runs `opencode mcp add`) with `graphify-mcp` (`GRAPHIFY_QUERY_LOG_DISABLE=1`), and optionally installs project skill (`graphify install --project --platform opencode`) if user wants `/graphify`.
   - **Hermes:** registers `graphify` stdio MCP entry in `$HERMES_HOME/config.yaml` (matching `capability/mcp.graphify.json`).
5. Verifies `graphify-mcp --help` / `graphify --help` succeeds and exits non-zero with plain-English diagnostics if offline/blocked.

### When it runs
- **During `setup/setup.sh`:** Optional `--with-graphify` flag (matching existing `--with-rea`), plus an optional prompt during interactive setup.
- **In `deploy/docker/Dockerfile`:** Pre-installed in the container image so Docker users need zero runtime downloads.
- **On-demand in chat (`learn-a-system` / `build-it`):** When a user connects a system or asks Vera to map a repo/docs/warehouse and `graphify` is not yet configured, Vera explains in one sentence what she'll install (isolated `uv` + Python 3.12 + `graphifyy[mcp]`, won't touch system Python), asks for a quick go-ahead, runs `setup/install_graphify.sh`, and immediately proceeds with the task.

---

## 5. Exact repository changes (`vera/`)

| File | Change |
|---|---|
| `capability/core-capabilities.yaml` | Add 6th `enhanced` capability: `graphify-indexing` (`needs: [mcp:graphify]`, `verify` checks `graphify-mcp` / `graphify` + runtime MCP config, `degraded` explains on-demand provisioning). Total capabilities: **13 (7 core, 6 enhanced)**. |
| `capability/mcp.graphify.json` *(new)* | Stdio MCP template for `graphify-mcp` with `GRAPHIFY_QUERY_LOG_DISABLE=1`, mirroring `capability/mcp.rea.json`. |
| `capability/README.md` | Document Graphify alongside REA, including the two-graph model (YAML/MD source of truth + Graphify query index) and `setup/install_graphify.sh`. |
| `setup/install_graphify.sh` *(new)* | Idempotent, isolated installer (`uv` + Python 3.12 + `graphifyy[mcp]` + runtime MCP wiring for OpenCode / Hermes). |
| `setup/setup.sh` | Add `--with-graphify` flag (parallel to `--with-rea`) calling `install_graphify.sh`. |
| `deploy/docker/Dockerfile` | Install `uv` + `graphifyy[mcp]` cleanly in the image. |
| `deploy/runtimes/{hermes,opencode,generic}.yaml` | Add `graphify-indexing: optional` so all 3 runtime profiles stay aligned with `core-capabilities.yaml`. |
| `setup/capability_check.py` | Probe `graphify-indexing` (`graphify-mcp` on `PATH` + configured in `opencode.jsonc` / `config.yaml` → `pass`; missing → `info` noting on-demand provisioning, never `fail`). |
| `skills/capability-acquisition/learn-a-system/SKILL.md` | Add Graphify as the structural scout for repos, SQL/dbt schemas, CSV packs, and multi-file docs (with on-demand `install_graphify.sh` provisioning if missing, `--code-only` default for local AST, explicit approval before LLM semantic pass on private docs, and indexing `knowledge/graph/` after write). Skip Graphify for single-endpoint SaaS APIs without a doc/code corpus. |
| `skills/capability-acquisition/learn-a-system/org.example.yaml` | Add `use_graphify: true` and `graphify_code_only_default: true` under `study:`. |
| `skills/capability-acquisition/evidence-trail/SKILL.md` | Map Graphify edge confidence (`EXTRACTED` → spot-check then `confirmed`; `INFERRED` → `inferred` with score; `AMBIGUOUS` → `unknown`). |
| `capability/workflows/analyze-connector.md` | Add **Step 2a. Structural graph pass** and **Step 3a. Refresh `knowledge/graph/` index**. |
| `policy/guardrails.example.yaml` | Add `graphify-semantic-pass` to `approvals.require_for` (local AST `--code-only` runs under study consent; sending private docs to an LLM backend requires explicit approval). |
| `.gitignore` | Ignore `graphify-out/`, `knowledge/graph/.graphify-out/`, `.graphify_labels.json*`, and `.graphify_root`. |
| `tests/onboarding/test_capability_check.py` | Update capability counts (`13` total: `7` core, `6` enhanced) and add tests for `graphify-indexing` across `hermes`, `opencode`, and `generic` + dry-run/mocked `install_graphify.sh` checks. |

---

## 6. Verification plan

1. **Automated test suite:** Run `./tests/run.sh` in `vera/` and confirm all existing + new checks pass (`0` failures).
2. **Real macOS Python 3.9.6 provisioning test:** Run `./setup/install_graphify.sh` on this exact machine (which has Python 3.9.6 and no `uv`), confirm `uv` + isolated Python 3.12 + `graphifyy[mcp]` installs cleanly without touching `/usr/bin/python3`, and verify `doctor.sh --runtime opencode` flips `graphify-indexing` from `INFO` to `PASS`.
3. **Real end-to-end connector study:** Run `learn-a-system` with real `graphify` against `gtm-crm-demo-dataset/` (mixed Python + Markdown + CSV specs) and verify `graph.json`, `knowledge/graph/entities/systems/`, `knowledge/graph/evidence/`, and quarantined `skills-live/` draft output, plus a clean `git status`.
