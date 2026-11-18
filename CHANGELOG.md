# Changelog

## [Unreleased] - v0.1.0 candidate

First public shape. Everything is new.

### Runtime model
- Stock Hermes Agent as upstream; this repo is config + content only, no forks.
- `setup/setup.sh` one-command install: preflight, Hermes install, provider +
  key (OpenRouter default; Anthropic/OpenAI/Gemini shells), skills copy,
  platform choice, visible-success hello. Idempotent, non-interactive mode.
- `setup/doctor.sh` health table: runtime, config, manifests, policy, secrets.

### Skills (5, deliberately small)
Ships a handful of skills that carry the whole loop - onboarding, learning,
daily work, and self-maintenance. Everything else Vera drafts herself into
`skills-live/` as she learns your systems.
- onboarding: meet-vera (hello, tour, connect-tools, memory + model choices,
  guardrails review, examples offer)
- capability-acquisition: learn-a-system (map a connected app's endpoints,
  auth, data shapes; draft a skill into quarantine; REA as optional MCP
  evidence source; the evidence standard inlined: claim, source, confidence,
  search boundary, open unknowns)
- analysis: briefings
- self-maintenance: skill-vetter (boot lint + weekly review + promotion PRs),
  analysis-validator (18-check two-gate QA: data correctness + output quality
  + significance awareness; mandatory before any numbered output ships)
- templates/api-integration (the helper-script pattern for plain REST APIs);
  skills/schema/skill.schema.yaml; every manifest validates

### Deployment
- Docker: `deploy/docker/Dockerfile` on the official `nousresearch/hermes-agent`
  base; entrypoint seeds the Vera layer into the `/opt/data` volume on first
  boot, then hands off to `hermes`
- Railway: `deploy/railway/railway.toml` builds the same Dockerfile; volume +
  variables documented in-file and in docs/DEPLOYMENT.md
- docs/DEPLOYMENT.md (local CLI, local Slack gateway, Docker, Railway, other
  harnesses) and docs/CONNECTING-TOOLS.md - both referenced by setup.sh from
  the start, now actually present
- setup.sh honors `VERA_PROFILE`/`VERA_PLATFORM` env vars (documented in
  .env.example, previously unread) and prints Docker next steps under
  `--profile docker`; `templates` bucket now installed alongside the others
- .env.example default model aligned with setup.sh (anthropic/claude-sonnet-4.5)

### Policy
- guardrails schema + safe-default example; Slack platform profile
  (Slack-first; other platforms are upstream Hermes, wired on request);
  enforcement doc
- writes ladder: read-only default, confirm_before_write (always|standing)

### Memory & knowledge
- Working-profile + durable-entry schemas; people-profile schema with
  HR-flavored classes hard-excluded
- Optional RLS-locked Supabase shell
- knowledge/seed/saas-terms.md (50+ standard terms, Vera-voiced) + runtime
  org graph scaffold
- decisions/: unwired decision-API interface + model-sources shape

### Cron
- daily-briefing, nightly-skill-vetter, weekly-recap specs (hermes cron)

### Brand
- Light Vera theme (violet accent on warm paper) across report templates and
  mock outputs; vera-mark + vera-buddy logo assets

### Examples
- 10 mock outputs under skills/onboarding/meet-vera/examples/: chat briefing,
  HTML forecast, ARR roll-forward (md + waterfall HTML), CSV, Excel workbook,
  slide format, briefing as email/Slack/plain-text
