# Changelog

## [Unreleased] - v0.1.0 candidate

First public shape. Everything is new.

### Runtime model
- Stock Hermes Agent as upstream; this repo is config + content only, no forks.
- `setup/setup.sh` one-command install: preflight, Hermes install, provider +
  key (OpenRouter default; Anthropic/OpenAI/Gemini shells), skills copy,
  platform choice, visible-success hello. Idempotent, non-interactive mode.
- `setup/doctor.sh` health table: runtime, config, manifests, policy, secrets.

### Skills (16)
- onboarding: meet-vera (hello, tour, connect-tools, memory + model choices,
  guardrails review, examples offer)
- capability-acquisition: learn-a-system, analyze-an-app, evidence-trail
  (REA as optional MCP plugin; analysis enters at draft tier behind approval)
- analysis: revops-analyst (7 method guides), customer-intel, briefings
- delivery: vera-reporting, documents, visuals, brand-design, enablement,
  intro-messages
- engineering: thinking, code-review
- self-maintenance: skill-vetter (boot lint + weekly review + promotion PRs)
- skills/schema/skill.schema.yaml; every manifest validates

### Policy
- guardrails schema + safe-default example; five platform profiles
  (Slack, WhatsApp, SMS, GroupMe, Teams); enforcement doc
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
