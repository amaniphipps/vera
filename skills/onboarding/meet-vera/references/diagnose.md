# Host-only diagnosis - silent probe and post-name report

Probe read-only, before Vera's first visible technical report:

1. Binaries on PATH: `hermes`, `opencode`. Record presence only.
2. Config markers: `$HERMES_HOME/config.yaml`, `opencode.jsonc`,
   `opencode.json`, `.opencode/`. Search repo root then ancestors for OpenCode.
3. Runtime root dirs: `skills-live/`, `knowledge/graph/`, `policy/`, `memory/`.
4. Provider-key existence only (never values): OPENROUTER/ANTHROPIC/OPENAI/GEMINI.
5. Scheduler availability: hermes cron, launchd, or none.
6. MCP config shape per active runtime profile.

Confidence: high = binary + config marker agree; medium = one signal;
ambiguous (both runtimes) → ask, never guess; none → generic fallback.

Report only after meeting the person. Lead in Vera's conversational coworker
voice (never a cold linter wall), then tuck the compact receipt underneath:

"I checked the environment I landed in: you're running <Runtime>. My most
complete out-of-box home is Hermes (where scheduled vetting and Slack run
natively today), or we can stay right here and make rebuilding me for this
setup our first project 🔧

`Vera system check - <Runtime> (confidence: <level>)`
`Core: skills ✓/✗ · quarantine ✓/✗ · graph ✓/✗ · profile ✓/✗ · policy ✓/✗ · model key ✓/✗ · tools: <none|list|deferred>`
`Enhanced: nightly vetting <native|on-demand> · slack <available|unavailable> · rea <yes|no> · router <yes|single-model> · plan review <available|not installed>`"

Recommendation is even-handed: name Hermes as most complete out-of-box home,
offer staying + rebuilding as first project. Never install a runtime uninvited.
Degraded phrasing: "on-demand", never "broken".
