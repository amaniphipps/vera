# Rich, centralized Vera examples - migration plan

Status: **approved and implemented in isolated staging for artifact review**. No branch, commit, or push has been created. The current dirty working tree is untouched.

## 1. Decisions locked for this plan

- **Source baseline:** public `main`, commit `63ab023` only.
- **Design baseline:** the committed public-main Vera brand and reporting conventions. Do not use or copy the current uncommitted Astryx/Allo work.
- **Additional requirements:** none beyond the user's request.
- **Isolation:** build and review in a fresh staging directory. Do not touch the current dirty `feature/graphify-integration` working tree.
- **Git gate:** no branch, commit, push, or bundle until the generated datasets and outputs have been reviewed and the user explicitly approves packaging.
- **Data posture:** entirely synthetic, CRM-shaped, anonymized data. No production CRM export, real customer identity, credential, or external connection.

## 2. Desired end state

All reusable mock datasets and sample outputs live under one canonical root:

`skills/onboarding/meet-vera/examples/`

The examples become a reproducible demonstration of Vera working from linked source records, not a collection of unrelated hardcoded reports.

The canonical pack will contain:

1. A CRM-shaped synthetic dataset with 1,000 ending active customers and at least 200 open opportunities.
2. A customer-level ARR roll-forward covering 1,050 accounts, including churned records, with visible movement.
3. Supporting records that make the funnel, briefing, win/loss, weekly recap, and commission examples reproducible.
4. Regenerated HTML, Markdown, TXT, DOCX, XLSX, and PPTX outputs from the same source data.
5. One master catalog and one visual gallery for reviewing every example.
6. Updated documentation and references, with duplicate fictional data removed from skills and docs.
7. Deterministic generators and validation that prove record counts, relationships, arithmetic, and output freshness.

## 3. Non-goals

- No live CRM, billing, product, marketing, or Slack connection.
- No claim that synthetic data came from a real customer system.
- No Astryx console work and no use of uncommitted fonts, themes, or tour files.
- No redesign of Vera's public-main brand tokens.
- No changes to runtime guardrails, provider configuration, memory, or current Vera state.
- No Office/LibreOffice installation outside the approved staging environment without separate user approval.
- No branch or commit before artifact approval.

## 4. Canonical directory design

Keep existing public-main filenames where references already depend on them. Add structure below the existing examples root instead of renaming everything and creating avoidable breakage.

```text
skills/onboarding/meet-vera/examples/
  README.md                         # master catalog, record counts, regeneration, review links
  index.html                        # visual gallery of every generated example
  data/
    crm-accounts.csv                # 1,050 anonymized accounts
    crm-contacts.csv                # approximately 2,100 anonymized contacts
    crm-opportunities.csv           # 200 open + 400 closed opportunities
    crm-stage-history.csv           # stage transitions for funnel/conversion analysis
    crm-activities.csv              # approximately 3,000 activities
    arr-rollforward.csv             # 1,050 rows: 1,000 ending active + 50 churned
    activation-users.csv            # 2,400 signup/activation/retention records
    quota-targets.csv               # owner-level quotas and commission tiers
    pdf-invoice.csv                 # canonical PDF-skill instructional data
    pdf-quarterly-sales.csv         # canonical PDF-skill instructional data
    data-dictionary.md              # every table, field, enum, relationship, definition
    manifest.json                   # seed, counts, sums, metric definitions, source hashes
    validation-summary.json         # output hashes and cross-format QA results
  scripts/
    generate_data.py                # deterministic standard-library data generator
    validate_data.py                # schema, privacy, relationships, arithmetic
    build_html_examples.py          # shared design + HTML/SVG generation
    build_office_examples.py        # DOCX/XLSX/PPTX generation in isolated venv
    validate_examples.py            # cross-format consistency and file checks
  documents/
    mock-revenue-review.docx
    mock-pipeline-review.docx
    mock-campaign-one-pager.docx
    mock-project-plan.docx
  presentations/
    mock-revenue-review.pptx
  tour/
    index.md
    mock-revenue-dashboard.html
    pipeline-motion.html
    campaign-one-pager.html
    win-loss-brief.html
    pipeline-analysis.html
    quota-commission.html
    project-plan.html
  mock-pipeline.csv                 # backwards-compatible 200-open-deal export
  mock-arr-rollforward.xlsx         # multi-sheet formula-first workbook with full detail
  mock-arr-rollforward.md
  mock-arr-waterfall.html
  mock-forecast.html
  mock-weekly-briefing.md
  mock-briefing-slack.md
  mock-briefing-text.txt
  mock-briefing-email.html
  mock-slides.html                  # browser companion to the PPTX deck
  mock-activation-funnel.html       # migrated and regenerated funnel example
  mock-weekly-recap.html            # migrated and regenerated team recap example
  voice-examples.md                 # canonical synthetic voice examples
  onboarding-conversation.md        # canonical synthetic onboarding script
  pdf-examples.md                   # canonical explanation for the PDF sample data
```

The three old `vera-reporting/templates/` files remain at their current paths as neutral, functional skeletons. Their populated fictional reports move to the canonical examples root. A pointer-only compatibility file remains at the old voice-example path so existing deep links do not break. No generator directory contains `SKILL.md` or `skill.yaml`, so skill discovery and manifest counts remain unchanged.

## 5. Synthetic data model

### 5.1 Accounts and ARR

Generate **1,000 ending active customers**, plus **50 churned customer records** so churn remains visible at row level. That produces **1,050 unique accounts** and **1,050 ARR roll-forward rows**, one per account for the Q3 reporting period. The Q4 pipeline and forecast use the same account book.

Core account fields:

- `account_id`, `account_alias`, `lifecycle_status`
- `segment`, `industry`, `region`, `country`
- `owner_id`, `owner_alias`
- `plan_tier`, `billing_frequency`, `currency`
- `account_created_date`, `customer_since_date`
- `health_score`, `last_activity_date`, `acquisition_source`

ARR fields:

- `account_id`, `period`
- `starting_arr`, `new_arr`, `expansion_arr`, `contraction_arr`, `churn_arr`, `ending_arr`
- `movement_category`, `previous_plan_tier`, `current_plan_tier`

Movement rules:

- New: start at zero, positive `new_arr`, positive ending ARR.
- Expansion: positive starting and ending ARR, ending above starting.
- Contraction: positive starting and ending ARR, ending below starting.
- Churn: positive starting ARR, `churn_arr = starting_arr`, ending at zero.
- Flat: positive starting ARR equal to ending ARR.
- No separate reactivation total in the first version; any reactivated account is included in expansion and identified in the data dictionary to avoid double counting.

Target this deterministic movement distribution:

- 670 flat accounts.
- 150 expansion accounts.
- 100 contraction accounts.
- 50 churned accounts.
- 80 new accounts.

That yields 970 starting active customers, 50 churned customers, 80 new customers, and **1,000 ending active customers** across **1,050 roll-forward rows**. The manifest verifies these counts rather than leaving them implicit.

For every row:

`ending_arr = starting_arr + new_arr + expansion_arr - contraction_arr - churn_arr`

### 5.2 CRM opportunities

Generate **600 opportunities**:

- **200 open deals** for the pipeline and forecast examples.
- **400 closed deals** with won/lost outcomes, close dates, reasons, and competitor aliases for win/loss and conversion examples.

Core fields:

- `opportunity_id`, `account_id`, `opportunity_alias`
- `owner_id`, `stage`, `forecast_category`
- `amount_usd`, `expected_arr_usd`, `probability`
- `created_date`, `close_date`, `last_activity_date`, `next_step_date`
- `acquisition_source`, `product_family`, `risk_status`
- `next_step`, `win_reason`, `loss_reason`, `competitor_alias`

Rules:

- Open forecast categories are mutually exclusive: `Commit`, `Best Case`, `Pipeline`.
- Closed records use terminal stages and do not carry an open forecast category.
- Amounts, dates, probabilities, risk, and stage must be internally consistent.
- Open coverage, commit, best case, full pipeline, win rates, stage conversion, owner concentration, and aging are computed from the records, never typed into reports independently.
- Closed-won `expected_arr_usd` for the roll-forward period reconciles by account to new and expansion ARR movements. Older closed history is used only for conversion and win/loss analysis; closed-lost deals have no ARR effect.

### 5.3 Supporting linked records

- **Contacts:** approximately 2,100, linked to accounts, using aliases and `.invalid` email addresses only.
- **Stage history:** enough transitions to reproduce stage conversion and aging for all 600 opportunities.
- **Activities:** approximately 3,000, linked to accounts and, where applicable, opportunities and owners.
- **Activation:** 2,400 synthetic signup records with activation and week-two retention fields for the funnel report.
- **Quota targets:** owner-period quotas and documented marginal commission tiers; commission outputs use formulas.

The complete pack will contain more than 10,000 linked records while remaining ordinary CSV text that is easy to review and migrate.

### 5.4 Anonymization and privacy

- Use IDs and aliases such as `acct_0001`, `Account 0001`, `owner_01`, and `Contact 0001`.
- Use only reserved `.invalid` email domains. No phone numbers, street addresses, real domains, real names, or production IDs.
- Northwind remains the fictional reporting organization. Account and person aliases do not map to real entities.
- Add an automated scan for secret-shaped strings, real-looking email domains, and unapproved identity fields.
- The README will say plainly that the data is synthetic and anonymized, not a sanitized production extract.

## 6. One source of metrics

`generate_data.py` will use a fixed seed and standard-library Python wherever practical.

`validate_data.py` will create `manifest.json` with source metrics and hashes. After the outputs are built, `validate_examples.py` will write output hashes and cross-format validation results to `validation-summary.json`, keeping the source manifest stable and free of output-hash feedback loops. The completed manifest contains:

- Generator seed and reporting period.
- Record counts for every table.
- Open and closed opportunity counts.
- ARR movement counts and sums.
- Starting and ending ARR.
- GRR, NRR, gross adds, gross losses, and net ARR added.
- Pipeline totals by stage and forecast category.
- Win/loss counts and conversion rates.
- Activation and retention totals.
- Commission and quota reconciliation totals.
- SHA-256 hashes for source CSVs and generated outputs.

Every report reads the same CSVs or the validated manifest. A report build fails if a source hash or metric disagrees with the manifest. No headline figure is manually maintained in HTML, DOCX, XLSX, PPTX, Markdown, or documentation.

Metric contract:

```text
ending ARR = starting ARR + new + expansion - contraction - churn
net ARR added = ending ARR - starting ARR
GRR = (starting ARR - contraction - churn) / starting ARR
NRR = (starting ARR + expansion - contraction - churn) / starting ARR
closed-won ARR = sum of closed-won expected_arr_usd in the period
commit view = closed-won ARR + open Commit expected_arr_usd
best-case view = commit view + open Best Case expected_arr_usd
full-pipeline view = best-case view + open Pipeline expected_arr_usd
win rate = closed-won opportunities / (closed-won + closed-lost opportunities)
stage conversion = opportunities reaching the next stage / opportunities entering the prior stage
activation rate = activated users / signup users
week-two retention = retained users / activated users
```

New-logo ARR is excluded from NRR. Expansion is excluded from GRR. Forecast categories are mutually exclusive, and full pipeline is never labeled a weighted forecast. Quota and commission formulas use the documented owner-period targets and marginal tiers.

## 7. Output matrix

All visual formats use the public-main Vera design tokens and actual Vera logo asset. All text formats use Vera's public-main voice rules.

| Example | HTML | DOCX | XLSX | PPTX | Text/other |
|---|---:|---:|---:|---:|---:|
| Revenue dashboard and ARR roll-forward | Yes | Yes | Yes | Yes | Markdown summary |
| Pipeline analysis and forecast | Yes | Yes | Detail sheets in workbook | Included in revenue deck | 200-open-deal CSV |
| Weekly briefing | Email HTML | No | No | No | Markdown, Slack Markdown, TXT |
| Activation funnel | Yes | No | Cohort detail in workbook | Optional deck view if it adds clarity | Source CSV |
| Weekly team recap | Yes | No | No | Included if materially different | Source data linked |
| Win/loss brief | Yes | Included in pipeline DOCX | Closed-history sheets | Included in revenue deck | Evidence notes |
| Quota and commission | Yes | No | Formula-first sheets | No | Definitions in data dictionary |
| Campaign one-pager | Yes | Yes, if it remains a distinct example | No | No | None |
| Project plan | Yes | Yes | No | Included only if it adds a useful walkthrough | Markdown source optional |
| Pipeline motion | Animated HTML with static and reduced-motion fallbacks | No | No | No | None |
| Voice examples | No | No | No | No | Canonical Markdown |
| PDF instructional examples | No | No | No | No | Canonical CSV + Markdown |

The workbook will include visible, filterable detail for all 1,050 ARR rows, including the 1,000 ending active customers, and all 200 open deals, plus summaries and formula checks. The DOCX and PPTX will present decision-ready summaries and link to the workbook for full row-level detail rather than squeezing thousands of rows into unreadable pages.

## 8. Public-main design system

Use only committed public-main sources:

- `skills/delivery/brand-design/org.example.yaml` for color, font, voice, and logo policy.
- `skills/delivery/vera-reporting/templates/` for the existing public-main reporting conventions that survive the migration.
- `docs/assets/vera-mark.png` as the actual Vera mark; never redraw it.
- Existing `mock-forecast.html`, `mock-arr-waterfall.html`, and `mock-slides.html` as layout references where useful.

Canonical public-main palette:

| Role | Value |
|---|---|
| Accent | `#3559D6` |
| Secondary accent | `#0F8A75` |
| Ink | `#1B1F27` |
| Paper | `#F4F5F7` |
| Dark surface | `#14182E` |
| Surface | `#FFFFFF` |
| Line | `#DDE1E6` |
| Good | `#1F9D55` |
| Warning | `#B7791F` |
| Risk | `#C53030` |

Replace older violet/warm defaults rather than carrying them into another generation of examples. Define any soft or muted derivatives centrally and prove their contrast; do not invent them independently inside reports. The Vera logo's `#5B71E4` artwork is not a new CSS token. HTML uses `system-ui, -apple-system, 'Segoe UI', sans-serif`; Office outputs use Arial. Because the committed PNG logos have no alpha and the org's light/dark logo slots are blank, logo background treatment requires visual QA rather than an assumed transparent variant.

Implementation rules:

1. One generator-owned token map feeds HTML, DOCX, XLSX, and PPTX.
2. Generated HTML remains self-contained: inline CSS/JS/SVG and embedded assets. No runtime network dependency.
3. HTML uses semantic CSS variables, sentence-case headings, tabular numerals, accessible SVG titles/descriptions, responsive tables, and reduced-motion fallbacks.
4. Office outputs use the same palette and Vera mark, with a documented system-safe Office font mapping.
5. Financial workbook inputs are blue, formulas black, cross-sheet links green, and key assumptions yellow, following the XLSX skill.
6. Every output carries `Synthetic / anonymized`, reporting period, source filename, caveats, and `Built by Vera` with date.
7. No placeholder copy, fake live source statement, external font request, or invented customer quote.

## 9. Source-content migration map

Apply these rules after confirming all inbound references:

| Current public-main content | Canonical destination | Source treatment |
|---|---|---|
| `skills/onboarding/meet-vera/examples/` existing Northwind files | Keep filenames where practical; regenerate from the richer source data | Replace hardcoded values and placeholders |
| `skills/delivery/vera-reporting/templates/forecast.html` | Merge useful layout into canonical `mock-forecast.html` | Retain the original path as a neutral functional forecast skeleton; remove fixed forecast numbers and account claims |
| `skills/delivery/vera-reporting/templates/funnel.html` | `mock-activation-funnel.html` | Retain the original path as a neutral functional funnel skeleton; remove fixed cohorts, totals, and takeaways |
| `skills/delivery/vera-reporting/templates/weekly-recap.html` | `mock-weekly-recap.html` | Retain the original path as a neutral functional recap skeleton; remove fixed employees, volumes, and week-specific claims |
| `skills/self-maintenance/voice-curator/references/voice-examples.md` | `examples/voice-examples.md` | Replace duplicate examples with a link; rewrite numeric examples from the canonical data; update skill and tests |
| `docs/VOICE-AND-TONE.md` extended examples | `examples/voice-examples.md` | Keep rules; replace duplicated fictional records with canonical links |
| `docs/PERSONAL-ONBOARDING-BUILD-IT-PLANNOTATOR.md` synthetic conversation | `examples/onboarding-conversation.md` | Keep design rationale; link to canonical script |
| Numeric excerpts in `personas/vera.md` and `skills/analysis/revops-analyst/SKILL.md` | `examples/voice-examples.md` or the relevant generated report | Replace duplicated figures with canonical references |
| Inline arrays in `skills/community/pdf/REFERENCE.md` | `data/pdf-invoice.csv`, `data/pdf-quarterly-sales.csv`, and `pdf-examples.md` | Keep executable instructions; reference canonical data instead of maintaining separate sample values |

Inbound-reference decisions confirmed from public `main`:

- The three reporting template basenames are referenced only by `vera-reporting/SKILL.md`; `cron/weekly-recap.sh` invokes the skill, not an HTML file. No cron path change is needed.
- Voice-example inbound links are `voice-curator/SKILL.md`, `tests/onboarding/test_personal_memory_and_build_it.py`, and `docs/PERSONAL-ONBOARDING-BUILD-IT-PLANNOTATOR.md`. Preserve the five existing register headings in the canonical file and update the test path plus the skill's “patterns here” ownership wording.
- Existing meet-vera and tour filenames remain in place, avoiding changes to setup, runtime discovery, and most tour documentation.
- `setup/setup.sh`, `deploy/docker/Dockerfile`, and `cron/weekly-recap.sh` already copy or invoke at the skill level; verify them but do not change their paths for this migration.

Replace legacy claims such as `Live from CRM` and `Pulled at run time; no stored figures` with truthful provenance: `Generated from the included synthetic CSV fixtures`, source filename/hash, generation date, and validation status.

No source file will be converted into a dead link. Generic templates needed for real deliverables remain functional and contain no fictional customer records.

## 10. Documentation updates

At minimum:

- `examples/README.md`: master example catalog, dataset schema summary, record counts, regeneration commands, validation commands, output matrix, privacy statement, and review links.
- `examples/data/data-dictionary.md`: complete fields, types, enums, relationships, metric definitions, and anonymization rules.
- `examples/tour/index.md`: every tour artifact, producing skill, source tables, format, and fallback.
- `meet-vera/SKILL.md` and `references/capability-tour.md`: point to the master catalog/gallery and describe the 1,000-customer/200-open-deal demonstration without implying live data.
- Root `README.md`: link to the richer example pack and its DOCX/XLSX/PPTX formats.
- `vera-reporting/SKILL.md`: separate generic skeletons from canonical examples and fix its `.report-page` versus `.page` mismatch by documenting the public-main `.page` selector.
- `voice-curator/SKILL.md`: read examples from the canonical location and remove the old “patterns here” ownership wording.
- `docs/VOICE-AND-TONE.md`: link to canonical examples instead of duplicating fictional figures.
- `docs/PERSONAL-ONBOARDING-BUILD-IT-PLANNOTATOR.md`: link to the canonical synthetic conversation.
- `skills/community/pdf/REFERENCE.md`: use the canonical instructional data.
- `CHANGELOG.md`: replace the stale violet/warm-palette description and exact old example count with the standardized design and richer multi-format pack.
- `tests/onboarding/test_personal_memory_and_build_it.py`: point to the canonical voice-example file and assert that `voice-curator/SKILL.md` links to it; preserve the existing five-register checks.
- Any test or documentation reference found by the inbound-reference scan.

No `AGENTS.md` exists in the public-main tree, so no agent-instruction update is expected.

## 11. Implementation sequence

### Phase 0 - Review and isolate

1. Obtain plan approval through Plannotator.
2. Create a fresh staging copy from public `main` `63ab023`, outside the current dirty repo.
3. Record the current repo branch/status for a final unchanged-state comparison.
4. Create an isolated Python environment inside staging for Office generation and validation.

### Phase 1 - Data first

1. Write the data dictionary and metric contract.
2. Generate accounts, contacts, opportunities, stage history, activities, ARR, activation, and quota data.
3. Run count, schema, privacy, relationship, date, stage, ARR, pipeline, and retention checks.
4. Inspect representative rows from every movement category and every open forecast category.
5. Produce the manifest and stop if any check fails.

### Phase 2 - Shared design and HTML

1. Build the shared public-main token/style layer in the generator.
2. Regenerate the existing Northwind HTML outputs.
3. Replace all seven tour placeholders with substantive, data-driven reports.
4. Migrate and regenerate the funnel and weekly-recap examples.
5. Build the master HTML gallery with direct links to every dataset and output.
6. Browser-check every HTML file at desktop and 390px, including motion-off behavior and console/network errors.

### Phase 3 - Office formats

1. Generate the formula-first workbook with full customer/deal detail.
2. Generate the revenue-review and pipeline-review DOCX files.
3. Generate the revenue-review PPTX and its browser companion.
4. Run structural validation and cross-format metric checks.
5. Recalculate formulas and visually render Office files if LibreOffice is available.

### Phase 4 - Centralize and update references

1. Migrate the populated examples out of reporting templates, voice docs, onboarding docs, persona excerpts, and PDF instructions.
2. Keep functional templates functional; remove duplicated fictional records.
3. Update every inbound reference and the documentation listed above.
4. Add `tests/onboarding/test_examples.py` for record counts, reconciliation, forecast/briefing agreement, funnel totals, offline HTML, Office package structure, canonical links, and synthetic provenance. `tests/run.sh` already discovers onboarding test files and needs no path change.

### Phase 5 - Full verification and review

1. Run the entire public-main test suite plus new example tests.
2. Run analysis-validator on every quantitative output.
3. Verify all formats show the same metrics and reporting period.
4. Verify no placeholders, real-looking identities, secrets, external asset requests, or stale source hashes.
5. Present the gallery and every generated output for user review, including Office files or their honestly labeled validation previews.
6. Stop for feedback. No branch yet.

### Phase 6 - Branch bundle only after approval

1. After explicit approval, create a clean worktree/branch from `origin/main`.
2. Apply only the reviewed dataset, generator, example, test, and documentation changes.
3. Re-run all checks in the clean branch.
4. Present the diff and bundle contents.
5. Ask separately before any commit or push.

## 12. Acceptance criteria

### Data

- Exactly 1,000 ending active customers, 50 churned records, 1,050 unique ARR customer rows, and 1,050 linked accounts.
- Movement counts reconcile exactly: 670 flat, 150 expansion, 100 contraction, 50 churn, and 80 new.
- Exactly 200 open opportunities and 400 closed opportunities.
- Every open deal is included in the visible workbook detail.
- Every customer movement row reconciles to the cent.
- Summary ARR, GRR, NRR, pipeline, forecast, funnel, win/loss, activation, and commission figures recompute from source records.
- Current-period closed-won expected ARR reconciles to new and expansion ARR by account.
- Zero duplicate primary keys and zero orphaned foreign keys.
- No real identities, production IDs, real email domains, or secrets.

### Centralization

- Every reusable mock/sample example has one canonical home under `meet-vera/examples/`.
- No duplicated fictional account figures remain in reporting templates, voice docs, persona excerpts, onboarding docs, or PDF instructions.
- Existing meet-vera paths still resolve or have explicit updated references.
- Generic templates remain usable for real outputs.

### Outputs

- Every existing HTML example is regenerated from the richer data; no placeholder-only tour artifact remains.
- DOCX, XLSX, and PPTX outputs are present and structurally valid.
- The workbook exposes all 1,050 customer rows, including 1,000 ending active customers, and all 200 open deals with filters and formula checks.
- All formats agree on source hashes, period, currency, and headline metrics.
- Public-main Vera tokens, logo, voice, and attribution are consistent across formats.
- HTML works offline, has no console errors or document-level overflow, and respects reduced motion.
- Every output has a clear synthetic/anonymized label and no fake live-source language.

### Office validation honesty

- Formula recalculation and visual Office rendering are mandatory before calling those aspects passed.
- If LibreOffice remains unavailable, do not install it globally without approval. Ship the review previews with structural checks and label Office formula recalculation/visual rendering **not inspected**, rather than claiming a pass.

### Repository safety

- Current working-tree branch/status remains unchanged during staging and review.
- No branch, commit, push, or bundle appears before explicit artifact approval.

## 13. Review package

The review handoff will contain:

1. `index.html` gallery linking every example.
2. Master `README.md` and data dictionary.
3. Raw CSVs and manifest with validation results.
4. Regenerated HTML, Markdown, TXT, DOCX, XLSX, and PPTX files.
5. Desktop/mobile screenshots for HTML and Office renders when available.
6. Test results and analysis-validator trails.
7. A proposed branch file manifest, with no branch created yet.
