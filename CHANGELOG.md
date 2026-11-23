# Changelog

## [Unreleased] - v0.1.0 candidate

First public shape. Everything is new.

### Runtime model
- Stock Hermes Agent as upstream; this repo is config + content only, no forks.
- `setup/setup.sh` one-command install: preflight, Hermes install, provider +
  key (OpenRouter default; Anthropic/OpenAI/Gemini shells), skills copy,
  platform choice, visible-success hello. Idempotent, non-interactive mode.
- `setup/doctor.sh` health table: runtime, config, manifests, policy, secrets.

### Skills (17, preset so Vera is useful on day 1)
- onboarding: meet-vera (hello, tour, connect-tools, memory + model choices,
  guardrails review, examples offer)
- capability-acquisition: learn-a-system, analyze-an-app, evidence-trail
  (REA as optional MCP plugin; analysis enters at draft tier behind approval)
- analysis: revops-analyst (7 method guides), customer-intel, briefings
- delivery: vera-reporting, documents, visuals, brand-design, enablement,
  intro-messages
- engineering: thinking, code-review
- self-maintenance: skill-vetter (boot lint + weekly review + promotion PRs),
  analysis-validator (18-check two-gate QA: data correctness + output quality
  + significance awareness; mandatory before any numbered output ships)
- templates/api-integration (the helper-script pattern for plain REST APIs);
  skills/schema/skill.schema.yaml; every manifest validates

### Onboarding: carry-over
- Step 4 (memory) now frames the four memory options as quick defaults, not
  a fence, and always invites carry-over: memory exports, skills from other
  agents, conventions/glossary from whatever the user ran before.
- Each kind has a deliberate path: memory exports become proposed durable
  entries read back for confirmation before admitting; markdown skills land
  in skills-live/ quarantine (never straight into skills/); conventions seed
  the knowledge-graph glossary; unknown formats get mapped with an honest
  account of what mapped and what did not.
- Hard rule added after live testing caught the bypass: carry-over never
  uses the runtime's native memory-write or skill-create tools - they skip
  the review trail.

### Community skills (32 skills)
- Added 4 production document skills from `anthropics/skills` (Apache-2.0):
  `docx` (Word creation, editing, and analysis), `xlsx` (Excel models with recalc.py
  formula verification), `pdf` (forms, extraction, generation, and split/merge),
  and `pptx` (PowerPoint presentation deck generation with slide text extraction).
- Manifests added conforming to Vera's `skill.schema.yaml`, credited in
  `skills/community/ATTRIBUTION.md`.
- `skills/delivery/documents` updated to cross-reference these community skills.
- 28 skills adapted from swan-gtm/gtm-skills (MIT),
  selected by real skills.sh install rank, deduplicated against Vera's
  authored skills, and reshaped to her format: Vera frontmatter, skill.yaml
  manifests, org.example.yaml slots, vendor-neutral language, and her Output
  contract (self-contained files, analysis-validator before numbers ship,
  plain voice). Judgment preserved: rubrics, thresholds, cited benchmarks.
- Provenance: schema gains `origin: community-import` plus machine-readable
  `source_repo`/`source_author`/`source_license`; human credit in
  `skills/community/ATTRIBUTION.md`. All ship at tier: draft.
- setup.sh installs the community bucket; skill.schema.yaml extended;
  doctor verifies all 46 manifests.

### Positioning
- README rewritten for clarity: requirements, one-command quickstart, what
  she does, where she runs. Hermes stated plainly as the supported runtime.
- Docker/Railway demoted to optional always-on recipes - the local CLI is the
  tested golden path and the docs say so.
- Other-harnesses story: Hermes-only today; porting Vera elsewhere is framed
  as a job you do with Vera (her skills, persona, and policy are plain
  files), with the two invariants any host must honor.

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
- Public-main Vera tokens across report templates and examples: blue `#3559D6`
  and teal `#0F8A75` accents, `#1B1F27` ink, cool `#F4F5F7` paper, and
  `#14182E` dark surfaces, with system font stacks; vera-mark + vera-buddy logo
  assets

### Examples
- Canonical rich multi-format collection under
  `skills/onboarding/meet-vera/examples/`: populated synthetic outputs, source
  data, a visual index, onboarding and voice examples, native DOCX/XLSX/PPTX
  outputs, and PDF instructional CSVs with a walkthrough. Neutral HTML
  generation skeletons remain separate in
  `skills/delivery/vera-reporting/templates/`.
