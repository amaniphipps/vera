# Runtime-adaptive onboarding — repo update plan

**Target repo:** `github.com/amaniphipps/vera` (feature branch based on
`origin/main` `9f82949`) · **Status:** implementation plan, rev 3 · **Date:** 2026-11-22

## Objective

Ship a Vera release where onboarding **diagnoses the host system first**,
then recommends a setup that delivers her core capabilities on that system.
OpenCode and Hermes are the supported runtimes; a generic path is honored.
The user chooses. Vera detects, reports, recommends — never installs a
runtime uninvited.

This document is the engineering plan for updating the repo itself: files,
implementation order, tests, and the merge path.

## 1. Scope

**In scope**

- `capability/core-capabilities.yaml` — declarative capability contract
  (core vs enhanced, per-capability verify probes).
- `deploy/runtimes/{hermes,opencode,generic}.yaml` — per-runtime satisfaction
  profiles (detection markers, runtime root, skill-discovery mechanism,
  scheduler, memory options, MCP config shape).
- `skills/onboarding/meet-vera/` — Step 0 diagnosis inserted; hello asks the
  person's name and remembers it with confirmation; step 3 rewired through
  the active runtime profile; close-out re-check recorded in the working
  profile. New `references/diagnose.md`.
- `skills/self-maintenance/memory-curator/` + `memory/stores.example.yaml` —
  multi-store recall/write routing, profile curation, provenance, correction,
  and forgetting across enabled stores.
- `skills/capability-acquisition/build-it/` — capability questions trigger a
  reverse-engineering and implementation workflow with plan approval,
  checkpoints, tested artifacts, and quarantined skill drafts.
- `setup/setup.sh` — `--runtime hermes|opencode|generic` (default:
  auto-detect, ask when ambiguous). OpenCode path writes `opencode.jsonc`
  skills array + `OPENCODE.md` path mapping + seeds runtime dirs. Generic
  path prints the manual wiring checklist.
- `setup/doctor.sh` — renders the capability table from
  `core-capabilities.yaml` + active runtime profile; Hermes-only checks
  become the hermes profile's probes. Secret-hygiene scan unchanged.
- `skills/self-maintenance/skill-vetter/SKILL.md` — boot lint gains a
  portability check: flag skill bodies referencing `$HERMES_HOME`,
  `hermes cron`, or `rea` without a profile fallback. Drift-class finding,
  not a blocker.
- `personas/vera.md` — one line: diagnose before recommending on any new
  system.
- `README.md`, `docs/DEPLOYMENT.md` — OpenCode and Hermes as first-class
  runtimes; generic as supported-minimum.

**Out of scope**

- Auto-installing any runtime.
- Per-runtime forks of the skill set.
- Changes to `skills/community/*` (imports; portability lint reports only).
- Slack/gateway behavior (unchanged; Hermes-only, declared as such).

## 2. Pre-flight: repo hygiene (must land first)

The working tree has uncommitted changes from earlier sessions
(`.gitignore`, `vera-reporting`, new `vera-bar/`, `vera.sh`,
`OPENCODE.md`, astryx docs). Before any onboarding work:

1. Branch from `origin/main` (`9b82412`) as
   `feature/runtime-adaptive-onboarding`.
2. Commit or stash existing work on separate branches — this feature must
   diff cleanly against baseline. Do not bundle astryx/vera-reporting/
   vera-bar changes into this PR.
3. Keep this plan at `docs/RUNTIME-ADAPTIVE-ONBOARDING.md` (committed with
   the feature).

**Gitignore guardrails for the new files**

- `policy/guardrails.yaml` must stay uncommitted (deployment-specific);
  add it to `.gitignore` alongside `.env`. Ship
  `policy/guardrails.example.yaml` only.
- Runtime-dir seeds commit as `.gitkeep` files:
  `skills-live/.gitkeep`,
  `knowledge/graph/entities/{business,glossary,people,systems}/.gitkeep`,
  `knowledge/graph/evidence/.gitkeep`. Existing ignore rules already cover
  the contents — verify the negations work after the new dirs are added.
- No provider keys, no `opencode.json` from any real install, no
  `skills-live/` learned content in the PR.

## 3. File-by-file changes

### 3.1 New: `capability/core-capabilities.yaml`

Single source of truth for "fully capable Vera". Onboarding, setup, and
doctor all read it. Twelve capabilities; `tier: core` gates onboarding
completion, `tier: enhanced` is offered only.

Core: `skills-bundled`, `skills-quarantine`, `knowledge-graph`,
`policy-guardrails`, `working-profile`, `model-provider`,
`tool-connections`.
Enhanced: `nightly-vetting`, `slack-gateway`, `rea-observation`,
`model-router`, `usage-bar`.

Each entry: `id`, `tier`, `needs`, `verify` (a concrete check), and
`degraded` (one honest sentence for when it cannot verify on this runtime).

### 3.2 New: `deploy/runtimes/{hermes,opencode,generic}.yaml`

Per-runtime profiles. Fields: `runtime`, `detect` (binary + config
markers), `runtime-root`, `skill-discovery` (mechanism + bucket list +
exclusions), `path-mapping-doc`, `scheduler`, `memory`, `mcp`, `notes`.

Key differences the profiles encode:

| Concern | hermes | opencode | generic |
|---|---|---|---|
| runtime root | `$HERMES_HOME` | `<repo>/vera` | `<repo>/vera` |
| skill discovery | directory scan of `skills/` | `opencode.jsonc` `"skills"` array; exclude `templates`, `schema` | manual checklist |
| scheduler | `hermes cron` | none → on-demand vetting, optional launchd recipe | none |
| memory | supabase / hindsight / obsidian / files | working-profile / files | working-profile / files |
| slack-gateway | available | unavailable (declared) | unavailable |

`generic` is never auto-detected — user-selected only.

### 3.3 Modify: `skills/onboarding/meet-vera/SKILL.md`

- **New Step 0 — Diagnose this system.** Silent read-only probe (binaries,
  config markers, runtime dirs, provider-key existence — never values,
  scheduler, MCP config) → runtime hypothesis with stated confidence →
  capability report rendered from `core-capabilities.yaml` × active
  profile → recommendation with the choice explicit ("You're on OpenCode;
  core set intact, tools are the gap. Hermes is the full-capability path if
  you want nightly vetting and Slack — or we stay here. Your call.")
- **Step 1** opens "What should I call you?", waits, and never infers a name
  from account/machine metadata. The working profile records the answer;
  durable name memory requires read-back confirmation.
- **Step 2** tour paths resolve through the profile.
- **Step 3** reads the profile's `mcp` block for config shape and commands
  (OpenCode: `opencode mcp add`; Hermes: config.yaml; generic: helper
  scripts). Permission question and study flow unchanged.
- **Step 4** memory options filtered by the profile's `memory` list, with
  multiple enabled stores and one confirmed default write store recorded in
  `memory/stores.yaml`.
- **Close-out:** re-run the capability report; record runtime, choices, and
  degraded capabilities with reasons in the working profile.

### 3.4 New: `skills/onboarding/meet-vera/references/diagnose.md`

Probe checklist; detection confidence rules (high = binary + config marker
agree; ambiguous → ask, never guess); the capability-report template;
recommendation language that presents OpenCode/Hermes even-handedly and
honors a generic choice; the degraded-capability phrasing standard
("on-demand", never "broken").

### 3.5 Modify: `setup/setup.sh`

- Add `--runtime` flag; default auto-detect, prompt when both runtimes
  present or neither recognized.
- **OpenCode path:** write project `opencode.jsonc` with the seven skill
  buckets (excluding `templates/`, `schema/`), `instructions` entries for
  `personas/vera.md` + `OPENCODE.md`; generate `OPENCODE.md` path mapping;
  seed `vera/skills-live/`, `vera/knowledge/graph/*`, and
  `vera/policy/guardrails.yaml` from the example. This codifies the manual
  wiring validated in the OpenCode pilot session (2026-11-22).
- **Hermes path:** existing behavior, unchanged.
- **Generic path:** create runtime dirs, print the manual wiring checklist.
- Keep the "setup isn't done until she says hello" gate on every path.

### 3.6 Modify: `setup/doctor.sh`

- Load `core-capabilities.yaml` + active runtime profile; render one
  pass/warn/fail row per capability. Core failures exit 1; enhanced
  unavailability prints as INFO with the degraded sentence, not FAIL.
- Hermes-only checks (hermes binary, config.yaml model.default) become the
  hermes profile's probes. OpenCode profile probes: `opencode.jsonc`
  exists, skills array covers seven buckets, `OPENCODE.md` present.
- Secret-hygiene scan and `.gitignore`-aware file selection unchanged.

### 3.7 Modify: `skills/self-maintenance/skill-vetter/SKILL.md`

Boot lint adds a portability check: any `skills/**/SKILL.md` body
referencing `$HERMES_HOME`, `hermes cron`, `rea`, or Slack gateway without
a runtime-profile fallback is flagged as a drift-class finding in the
digest. Report-only; does not block vetting or promotion.

### 3.8 Modify: `personas/vera.md`, `README.md`, `docs/DEPLOYMENT.md`

Persona gains one steady-core line (diagnose before recommending). README
"Where she runs" lists OpenCode + Hermes as first-class with the generic
minimum; DEPLOYMENT gets the OpenCode setup section pointing at the
generated `opencode.jsonc`/`OPENCODE.md`.

## 4. Tests (new: `tests/onboarding/`)

No test harness ships today; add `tests/run.sh` (bash + python3 + pyyaml,
same deps as doctor) with fixtures under `tests/onboarding/fixtures/`.

1. **Fresh-install matrix:** `setup.sh --runtime hermes` and
   `--runtime opencode` into clean temp homes → doctor passes all core
   checks on both. Generic → core minus auto skill discovery, checklist
   printed.
2. **Golden transcripts:** `tests/onboarding/golden/{hermes,opencode}.md` —
   the Step 0 report for each fixture system must match byte-for-byte.
3. **Ambiguity:** fixture with both runtimes present → onboarding asks;
   transcript asserts the question, not a guess.
4. **Degradation:** OpenCode fixture, no scheduler → nightly-vetting
   reported "on-demand" in both the Step 0 report and the close-out record.
5. **Manifest schema:** every new/edited `skill.yaml` validates against
   `skills/schema/skill.schema.yaml` (reuse doctor's lint as a shared
   function, don't duplicate it).
6. **Hygiene:** repo grep asserts no secrets, no real-install config, no
   `skills-live/` content in the diff.
7. **Regression:** existing Hermes quickstart (clone → setup → hello)
   passes unchanged on a clean machine/container.

## 5. Implementation & merge plan

Three PRs, each independently shippable and reviewable:

- **PR 1 — Contract + doctor.** `core-capabilities.yaml`, runtime
  profiles, doctor rewrite, tests 1/5/6/7. Onboarding still
  Hermes-default; diagnosis works read-only via doctor.
- **PR 2 — Onboarding + setup + personal memory + build-it.** meet-vera
  Step 0 and confirmed name capture, `diagnose.md`, setup.sh `--runtime`,
  memory-curator and multi-store registry, build-it workflow, tests 2/3/4
  plus skill/registry acceptance tests.
- **PR 3 — Lint + docs.** vetter portability lint, persona line,
  README/DEPLOYMENT, `CHANGELOG.md` entry.

Each PR: branch off latest `main`, full `tests/run.sh` green, diff
contains only that PR's files, no unrelated working-tree changes. Tag a
release after PR 3 (`v0.x.0`) — this is a user-facing behavior change to
onboarding, call it out in release notes with the OpenCode quickstart.

## 6. Risks & open questions

- **Upstream drift in OpenCode's skill/config format.** Mitigation: profile
  `verify` probes fail loudly in doctor; note the tested-against OpenCode
  version in the profile's `notes`.
- **Golden-transcript brittleness** as prose evolves. Mitigation: golden
  files assert structure + capability lines, not full prose, if this
  becomes noisy.
- **Two-runtime ambiguity UX** could annoy power users. Open question:
  accept a `--runtime` flag on `vera.sh` to skip the question.
- **Windows:** generic path only (WSL2 for Hermes, per existing docs). No
  new Windows work in this plan.

## 7. Definition of done

A second person, on a clean machine, runs `git clone … && cd vera &&
./setup/setup.sh` with either runtime installed; onboarding opens with an
accurate system diagnosis, offers the runtime choice, and finishes with
every core capability verified — or an explicit, recorded degraded state
they accepted. Doctor reproduces that verdict on demand. All tests green
in CI on the merge commit.
