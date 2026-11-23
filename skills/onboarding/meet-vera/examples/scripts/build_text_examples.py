#!/usr/bin/env python3
"""Build Markdown/TXT examples and the canonical example catalog from source data."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
M = json.loads((DATA / "manifest.json").read_text())
A = M["arr"]
P = M["pipeline"]
ACT = M["activation"]


def rows(name: str) -> list[dict]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def money(value: int | float, decimals: int = 2) -> str:
    return f"${value / 1_000_000:,.{decimals}f}M"


def pct(value: float, decimals: int = 1) -> str:
    return f"{value * 100:.{decimals}f}%"


def write(name: str, content: str) -> None:
    path = BASE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


accounts = {r["account_id"]: r for r in rows("crm-accounts.csv")}
arr = rows("arr-rollforward.csv")
opps = rows("crm-opportunities.csv")
open_opps = [r for r in opps if r["forecast_category"]]
closed = [r for r in opps if not r["forecast_category"]]
open_sorted = sorted(open_opps, key=lambda r: int(r["expected_arr_usd"]), reverse=True)
risk_open = [r for r in open_opps if r["risk_status"] == "At risk"]
watch_open = [r for r in open_opps if r["risk_status"] == "Watch"]
segments = defaultdict(lambda: defaultdict(int))
for row in arr:
    segment = accounts[row["account_id"]]["segment"]
    for field in ("starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr"):
        segments[segment][field] += int(row[field])

segment_lines = []
for segment in ("SMB", "Mid-Market", "Enterprise"):
    values = segments[segment]
    net = values["ending_arr"] - values["starting_arr"]
    segment_lines.append(f"| {segment} | {money(values['starting_arr'])} | {money(values['new_arr'])} | {money(values['expansion_arr'])} | ({money(values['contraction_arr'] + values['churn_arr'])}) | {money(values['ending_arr'])} | {money(net)} |")

arr_md = f"""# ARR roll-forward - Northwind, Q3 2026

*Synthetic / anonymized output. Generated from `data/arr-rollforward.csv` and `data/crm-accounts.csv`. No live billing or CRM system was queried.*

## The answer

**ARR grew {money(A['net_arr_added'])} to {money(A['ending_arr'])} (+{pct(A['net_arr_added'] / A['starting_arr'])}) in Q3.** New customers added {money(A['new_arr'])} and lifted the book to 1,000 ending active customers. The existing book contracted: NRR was {pct(A['nrr'])} because {money(A['contraction_arr'] + A['churn_arr'])} of contraction and churn exceeded {money(A['expansion_arr'])} of expansion.

## Customer-level roll-forward

| Movement | ARR | Customers | What it means |
|---|---:|---:|---|
| Starting ARR (Jul 1) | {money(A['starting_arr'])} | {A['starting_active_customers']} | Active at the start of Q3 |
| + New | {money(A['new_arr'])} | {A['movement_counts']['New']} | First recurring revenue in Q3 |
| + Expansion | {money(A['expansion_arr'])} | {A['movement_counts']['Expansion']} | Upgrades and additional products |
| - Contraction | ({money(A['contraction_arr'])}) | {A['movement_counts']['Contraction']} | Downgrades that remained active |
| - Churn | ({money(A['churn_arr'])}) | {A['movement_counts']['Churn']} | Ending ARR reduced to zero |
| - Flat | - | {A['movement_counts']['Flat']} | No ARR movement |
| **Ending ARR (Sep 30)** | **{money(A['ending_arr'])}** | **{A['ending_active_customers']:,} ending active** | **1,050 customer rows including churn** |

**Reconciliation:** {A['starting_arr']:,} + {A['new_arr']:,} + {A['expansion_arr']:,} - {A['contraction_arr']:,} - {A['churn_arr']:,} = {A['ending_arr']:,}. Every one of the 1,050 rows also reconciles independently.

## Segment movement

| Segment | Start | New | Expansion | Contraction + churn | End | Net |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(segment_lines)}

## What to take from it

- **New logos funded growth:** {money(A['new_arr'])} from 80 new customers exceeded the {money(A['net_arr_added'])} net increase. Acquisition masked a {pct(A['nrr'])} NRR book.
- **Churn is the largest loss bucket:** 50 customers removed {money(A['churn_arr'])}; 100 contractions removed another {money(A['contraction_arr'])}. Gross ARR retention was {pct(A['grr'])}.
- **Expansion did not cover losses:** 150 expansions added {money(A['expansion_arr'])}, covering {pct(A['expansion_arr'] / (A['contraction_arr'] + A['churn_arr']))} of contraction and churn.
- **Use the workbook for the full list:** `mock-arr-rollforward.xlsx` contains all 1,050 customer rows, account detail, formulas, and validation checks.

*Sources: `data/arr-rollforward.csv`, `data/crm-accounts.csv`, and reconciling Q3 closed-won rows in `data/crm-opportunities.csv`. Source hashes are in `data/manifest.json`.*

---

**Validated by Vera · Nov 23, 2026**
<details><summary>Validation trail</summary>

```text
GATE 1  1,050/1,050 rows reconcile; Q3 closed-won expected ARR matches new + expansion by account
        Starting active 970 + new 80 - churn 50 = ending active 1,000
        Aggregate movement and segment sums reconcile to zero residual
GATE 2  Synthetic label, source paths, complete movement table, and attribution present
SIGNIFICANCE  Deterministic synthetic census, not a sampled estimate
FINAL: PASS - source-dependent live-system checks not applicable
```
</details>
"""
write("mock-arr-rollforward.md", arr_md)

top_lines = [f"- **{r['opportunity_alias']}** - {money(int(r['expected_arr_usd']))}, {r['forecast_category']}, {r['stage']}, closes {r['close_date']}, {r['risk_status']}." for r in open_sorted[:5]]
brief_md = f"""# Q4 pipeline briefing - Northwind, week of Nov 23

*Synthetic / anonymized output. Generated from the included CRM fixtures, not a live CRM.*

**The read:** 200 open deals carry {money(P['open_expected_arr_total'])} of expected ARR. Commit view is {money(P['commit_view'])} including {money(P['q4_closed_won_arr'])} already closed won; Best Case reaches {money(P['best_case_view'])}. The remaining upside sits in 60 Best Case deals, not in a weighted-forecast claim.

## What moved

- **Open pipeline:** {money(P['open_expected_arr_total'])} across 200 deals - 60 Commit, 60 Best Case, and 80 Pipeline.
- **Closed won to date:** {money(P['q4_closed_won_arr'])} of Q4 expected ARR.
- **Scenario ladder:** {money(P['commit_view'])} Commit view, {money(P['best_case_view'])} Best Case, and {money(P['full_pipeline_view'])} if every open deal closes. Full pipeline is a ceiling, not a weighted forecast.

## What needs you

- **Risk review:** {len(risk_open)} at-risk deals and {len(watch_open)} watch deals are visible in `mock-pipeline.csv`. Start with forecast-category exposure, not just deal count.
- **Largest open opportunities:**
{chr(10).join(top_lines)}
- **Existing-book retention:** Q3 NRR was {pct(A['nrr'])}; expansion covered {pct(A['expansion_arr'] / (A['contraction_arr'] + A['churn_arr']))} of contraction and churn. Keep the retention work alongside the Q4 close plan.

## Next

- Review Commit slippage and next steps for the largest at-risk opportunities.
- Inspect stage, owner, segment, and risk slices in `tour/pipeline-analysis.html`.
- Reconcile customer-level retention in `mock-arr-rollforward.xlsx`.

---
*Sources: `crm-opportunities.csv`, `arr-rollforward.csv`, and `crm-activities.csv`. Validated by Vera · Nov 23, 2026 · synthetic fixture arithmetic and cross-file reconciliation checked.*
"""
write("mock-weekly-briefing.md", brief_md)

slack = f"""*Q4 pipeline briefing - Northwind, week of Nov 23* _(synthetic / anonymized)_

200 open deals carry *{money(P['open_expected_arr_total'])}* expected ARR. Commit view is *{money(P['commit_view'])}*; Best Case reaches *{money(P['best_case_view'])}*. Full-pipeline ceiling: {money(P['full_pipeline_view'])}, not a weighted forecast.

*What moved*
• *{money(P['q4_closed_won_arr'])}* Q4 closed-won expected ARR.
• *60 Commit / 60 Best Case / 80 Pipeline* deals, all mutually exclusive.
• Q3 ARR ended at *{money(A['ending_arr'])}* across *1,000 active customers*; NRR *{pct(A['nrr'])}*.

*Needs you*
• Review *{len(risk_open)} at-risk* and *{len(watch_open)} watch* open deals.
• Largest open: {open_sorted[0]['opportunity_alias']} *{money(int(open_sorted[0]['expected_arr_usd']))}*, {open_sorted[0]['forecast_category']}, closes {open_sorted[0]['close_date']}.
• Expansion covered *{pct(A['expansion_arr'] / (A['contraction_arr'] + A['churn_arr']))}* of Q3 contraction and churn. Retention work stays on the plan.

*Next*
• Open `tour/pipeline-analysis.html` for deal slices and `mock-arr-rollforward.xlsx` for all 1,050 ARR rows.

_Generated from included synthetic CRM fixtures · Nov 23, 2026 · arithmetic + claims checked_
"""
write("mock-briefing-slack.md", slack)

text = f"""VERA BRIEFING - NORTHWIND - Q4 2026 (SYNTHETIC / ANONYMIZED)

THE LINE: 200 open deals, {money(P['open_expected_arr_total'])} expected ARR. Commit view {money(P['commit_view'])}; Best Case {money(P['best_case_view'])}.

MOVED
+ Q4 closed won: {money(P['q4_closed_won_arr'])}.
+ Open: 60 Commit, 60 Best Case, 80 Pipeline.
+ Q3 ARR: {money(A['ending_arr'])} across 1,000 ending active customers.

NEEDS YOU
! {len(risk_open)} at-risk and {len(watch_open)} watch open deals.
! Q3 NRR {pct(A['nrr'])}; expansion covered {pct(A['expansion_arr'] / (A['contraction_arr'] + A['churn_arr']))} of losses.

NEXT
> Review tour/pipeline-analysis.html.
> Inspect all 1,050 ARR rows in mock-arr-rollforward.xlsx.

SOURCE: INCLUDED SYNTHETIC CRM FIXTURES - NO LIVE CRM PULL
VALIDATED BY VERA - NOV 23, 2026 - ARITHMETIC + CLAIMS CHECKED
"""
write("mock-briefing-text.txt", text)

voice = f"""# Voice examples - synthetic Northwind patterns, not customer transcripts

These examples use the canonical CSVs in `data/`. They demonstrate register and formatting, not live customer activity.

## 1. Social, banter, and team belonging

> One thousand active customers, two hundred open deals, and exactly zero mystery spreadsheets. I could get used to this. 🚀
>
> The useful part is not the record count. Every ARR row and every forecast number ties back to a file you can inspect.

## 2. Executive & analytical readout

> Everything checks out. Shipping it:
>
> **Northwind exited Q3 at {money(A['ending_arr'])} across 1,000 active customers - up {money(A['net_arr_added'])} from {money(A['starting_arr'])}. New logos added {money(A['new_arr'])}, but NRR was {pct(A['nrr'])} as expansion covered only {pct(A['expansion_arr'] / (A['contraction_arr'] + A['churn_arr']))} of contraction and churn. Full report below 👇**
>
> ---
>
> - **Growth came from acquisition:** 80 new customers added {money(A['new_arr'])}. Expansion added {money(A['expansion_arr'])} across 150 accounts.
> - **⚠️ Retention needs work:** 50 churned accounts removed {money(A['churn_arr'])} and 100 contractions removed {money(A['contraction_arr'])}. GRR was {pct(A['grr'])}. Start with the largest losses in the workbook, now.
> - **Q4 is visible at deal level:** 200 open deals carry {money(P['open_expected_arr_total'])}. Commit view is {money(P['commit_view'])} and Best Case reaches {money(P['best_case_view'])}; full pipeline is only a ceiling.

## 3. Multi-task parallel dispatch

> Three outputs dispatched from the same validated snapshot. Status:
>
> 1. **ARR review → HTML + XLSX + DOCX + PPTX** - 1,050 roll-forward rows, retention, segment movement, and reconciliation
> 2. **Pipeline review → HTML + CSV + DOCX** - 200 open deals, 400 closed deals, forecast scenarios, owner/risk slices
> 3. **Weekly briefing → email + Markdown + Slack + TXT** - the same Q4 totals, no independent numbers

## 4. New capability / integration live

> Northwind's example workspace is now connected 🎉
>
> Same local files, one reproducible build. No external credentials or live systems.
>
> - 12,578 linked records across CRM, ARR, activation, quota, and instructional tables
> - 1,000 ending active customers and 200 open opportunities
> - HTML, DOCX, XLSX, and PPTX examples in one catalog

## 5. Serious register

> Sorry, I couldn't validate the Office render. LibreOffice is not installed in this environment. The files have structural and cross-format checks, but formula recalculation and visual Office rendering remain not inspected.
>
> The HTML examples and source CSVs are available for review. Do not call the Office render passed until a real renderer completes it.
"""
write("voice-examples.md", voice)

onboarding = f"""# Synthetic onboarding conversation - Northwind example

This is a sample script for documentation, not a transcript from a live admin or production system. "Sam" is synthetic.

## 1. Meet

**Vera:** 😁 Hey, I'm Vera - a RevOps teammate. What should I call you?

**Sam:** Sam. Keep this demo separate from my real workspace.

**Vera:** Good to meet you, Sam. I'll keep the demo in its own workspace. You can inspect, correct, or remove what I remember.

## 2. How I work

**Vera:** My reviewed skills ship in `skills/`; learned drafts stay in `skills-live/` until reviewed. This example uses local synthetic fixtures and read-only guardrails.

## 3. Tools

**Sam:** Skip live connections.

**Vera:** Tools deferred. I will use the included synthetic CRM and ARR files and label every output accordingly.

## 4. Memory

**Sam:** Local files only.

**Vera:** Local files are the default write store. Any durable fact is read back before saving.

## 5. Models

**Sam:** Speed, no model changes for the demo.

**Vera:** Recorded. I will not change the configured model or invent a benchmark recommendation.

## 6. Guardrails and examples

**Vera:** The demo stays read-only with per-action confirmation. The example gallery contains {money(A['ending_arr'])} of ending ARR across 1,000 active customers, 200 open deals, and {ACT['signups']:,} activation records. Open `index.html` to inspect HTML, DOCX, XLSX, and PPTX outputs. Everything is synthetic and generated from the included CSVs.
"""
write("onboarding-conversation.md", onboarding)

pdf = """# PDF instructional sample data

The PDF community skill uses these canonical files rather than maintaining separate inline sample values:

- `data/pdf-invoice.csv`: two invoice lines for invoice `12345`, with quantity, unit price, and line total.
- `data/pdf-quarterly-sales.csv`: Widget and Gadget unit counts for Q1-Q4.

Read the CSV rows in the example code, compute line totals and quarterly totals from the fields, and label generated PDFs as instructional samples. The data is generic and synthetic, not a company dataset.
"""
write("pdf-examples.md", pdf)

fields = {
    "crm-accounts.csv": "account_id; account_alias; lifecycle_status; segment; industry; region; country; owner_id; owner_alias; plan_tier; billing_frequency; currency; account_created_date; customer_since_date; health_score; last_activity_date; acquisition_source; movement_category",
    "crm-contacts.csv": "contact_id; account_id; contact_alias; role; email; is_primary; last_engagement_date",
    "crm-opportunities.csv": "opportunity_id; account_id; opportunity_alias; owner_id; owner_alias; stage; forecast_category; amount_usd; expected_arr_usd; probability; created_date; close_date; last_activity_date; next_step_date; acquisition_source; product_family; opportunity_type; risk_status; next_step; win_reason; loss_reason; competitor_alias; period",
    "crm-stage-history.csv": "stage_history_id; opportunity_id; account_id; stage; sequence; entered_at; exited_at; owner_id",
    "crm-activities.csv": "activity_id; account_id; opportunity_id; owner_id; activity_type; activity_date; outcome; subject_alias",
    "arr-rollforward.csv": "account_id; period; starting_arr; new_arr; expansion_arr; contraction_arr; churn_arr; ending_arr; movement_category; previous_plan_tier; current_plan_tier; currency",
    "activation-users.csv": "user_id; account_id; user_alias; cohort_week; signup_date; activated; activated_date; retained_w2; acquisition_source",
    "quota-targets.csv": "owner_id; owner_alias; period; quota_usd; tier1_threshold; tier1_rate; tier2_threshold; tier2_rate; tier3_rate; currency",
    "pdf-invoice.csv": "invoice_id; item; quantity; unit_price_usd; line_total_usd",
    "pdf-quarterly-sales.csv": "product; q1_units; q2_units; q3_units; q4_units",
}
table_docs = []
for name, field_list in fields.items():
    table_docs.append(f"### `{name}`\n\nRows: **{M['tables'][name]:,}**\n\nFields: {field_list.replace('; ', ', ')}.\n")
dictionary = f"""# Northwind data dictionary

## Provenance and scope

All records are deterministic, synthetic, and anonymized. Seed: `{M['seed']}`. Generated: `{M['generated_on']}`. Currency: USD. No production export or real identity was used. Account and person aliases do not map to real entities. Contact emails use only the reserved `.invalid` domain.

The pack contains **{M['total_linked_records']:,} records** across the tables below. ARR covers Q3 2026. Pipeline and forecast cover Q4 2026 as of Nov 23, 2026.

{chr(10).join(table_docs)}
## Relationships

- `crm-accounts.account_id` is the parent for contacts, opportunities, ARR, and activation users.
- `crm-opportunities.opportunity_id` is the parent for stage history and activities.
- `owner_id` links opportunities, activities, stage history, and quota targets.
- Q3 closed-won `expected_arr_usd` reconciles by account to `new_arr + expansion_arr`.
- `mock-pipeline.csv` is the backwards-compatible export of the 200 open opportunities.

## Metric definitions

```text
ending ARR = starting ARR + new + expansion - contraction - churn
GRR = (starting ARR - contraction - churn) / starting ARR
NRR = (starting ARR + expansion - contraction - churn) / starting ARR
commit view = Q4 closed-won expected ARR + open Commit expected ARR
best-case view = commit view + open Best Case expected ARR
full-pipeline view = best-case view + open Pipeline expected ARR
win rate = closed won / (closed won + closed lost)
activation rate = activated / signups
week-two retention = retained_w2 / activated
```

New-logo ARR is excluded from NRR. Expansion is excluded from GRR. Open forecast categories are mutually exclusive. Full pipeline is a ceiling, not a weighted forecast. Commission tiers are marginal and documented in `quota-targets.csv` and the workbook.

## Privacy and validation

`validate_data.py` checks unique keys, foreign keys, movement counts, ARR arithmetic, Q3 CRM-to-ARR reconciliation, forecast categories, activation cohorts, and the `.invalid` email rule. `manifest.json` records counts, metrics, and SHA-256 source hashes.
"""
write("data/data-dictionary.md", dictionary)

catalog = f"""# Vera example catalog

One canonical location for Vera's synthetic datasets and generated examples. Everything is synthetic and anonymized. No live system is queried.

## Start here

- **Visual gallery:** `index.html`
- **Data dictionary:** `data/data-dictionary.md`
- **Validated metrics and source hashes:** `data/manifest.json`
- **Output hashes and cross-format QA:** `data/validation-summary.json`

## Dataset at a glance

- **{M['total_linked_records']:,} linked records**
- **{A['ending_active_customers']:,} ending active customers** across 1,050 ARR rows, including 50 churned records
- **{P['open_deals']} open opportunities** and **{P['closed_deals']} closed opportunities**
- **{M['tables']['crm-contacts.csv']:,} contacts**, **{M['tables']['crm-activities.csv']:,} activities**, and **{ACT['signups']:,} activation users**
- **{money(A['ending_arr'])} ending ARR**, **{money(P['open_expected_arr_total'])} open expected ARR**

## Generated examples

| Example | Formats |
|---|---|
| ARR roll-forward | `mock-arr-waterfall.html`, `mock-arr-rollforward.md`, `mock-arr-rollforward.xlsx`, `tour/mock-revenue-dashboard.html` |
| Pipeline and forecast | `mock-forecast.html`, `mock-pipeline.csv`, `tour/pipeline-analysis.html`, `documents/mock-pipeline-review.docx` |
| Revenue review | `documents/mock-revenue-review.docx`, `presentations/mock-revenue-review.pptx`, `mock-slides.html` |
| Weekly briefing | `mock-weekly-briefing.md`, `mock-briefing-slack.md`, `mock-briefing-text.txt`, `mock-briefing-email.html` |
| Activation funnel | `mock-activation-funnel.html`, `data/activation-users.csv` |
| Weekly team recap | `mock-weekly-recap.html`, `data/crm-activities.csv` |
| Guided tour | `tour/mock-revenue-dashboard.html`, `tour/pipeline-motion.html`, `tour/campaign-one-pager.html`, `tour/win-loss-brief.html`, `tour/pipeline-analysis.html`, `tour/quota-commission.html`, `tour/project-plan.html` |
| Other document examples | `documents/mock-campaign-one-pager.docx`, `documents/mock-project-plan.docx` |
| Voice and onboarding | `voice-examples.md`, `onboarding-conversation.md` |
| PDF instructional data | `pdf-examples.md`, `data/pdf-invoice.csv`, `data/pdf-quarterly-sales.csv` |

## Regenerate

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install pyyaml openpyxl python-docx python-pptx pillow lxml
EXAMPLES=skills/onboarding/meet-vera/examples
.venv/bin/python "$EXAMPLES/scripts/generate_data.py"
.venv/bin/python "$EXAMPLES/scripts/validate_data.py"
.venv/bin/python "$EXAMPLES/scripts/build_text_examples.py"
.venv/bin/python "$EXAMPLES/scripts/build_html_examples.py"
.venv/bin/python "$EXAMPLES/scripts/build_office_examples.py"
.venv/bin/python "$EXAMPLES/scripts/validate_examples.py"
```

The data generator is deterministic. Rebuilding from unchanged inputs should produce identical data and consistent metrics.

## Validation scope

Source data checks cover keys, relationships, record counts, ARR reconciliation, Q3 CRM-to-ARR reconciliation, forecast categories, and privacy rules. HTML and cross-format checks cover metrics, paths, offline assets, labels, and file structure.

LibreOffice is not installed in the build environment. Formula recalculation and full multi-page Office rendering remain **not inspected**. Review-specific first-page previews are documented separately and do not imply full rendering or recalculation.
"""
write("README.md", catalog)

tour = f"""# Guided tour index - synthetic Northwind examples

All seven artifacts use the canonical source CSVs. Start with the [master catalog](../README.md)
for regeneration and validation details, or open the [visual gallery](../index.html)
for every populated example. All values are synthetic and anonymized. In
particular, the shared scenario's 1,000 ending active customers and 200 open
deals are demonstration data, never live metrics.

| # | Artifact | File | Producing skill | Source tables | Format | Fallback |
|---|---|---|---|---|---|---|
| 1 | Revenue dashboard | `mock-revenue-dashboard.html` | vera-reporting | `arr-rollforward.csv`, `crm-accounts.csv`, `crm-opportunities.csv` | Static HTML/SVG | Static file; no script or network required |
| 2 | Motion | `pipeline-motion.html` | vera-reporting | `crm-opportunities.csv`, `crm-stage-history.csv` | Animated HTML/CSS/SVG | Pause control and reduced-motion static view |
| 3 | Marketing/design | `campaign-one-pager.html` | enablement + brand-design | `crm-accounts.csv`, `arr-rollforward.csv` | Static HTML | Static file; no external assets required |
| 4 | Win/loss | `win-loss-brief.html` | revops-analyst | `crm-opportunities.csv` | Static HTML | Static evidence notes and limitations remain visible |
| 5 | Pipeline analysis | `pipeline-analysis.html` | revops-analyst | `crm-opportunities.csv`, `crm-accounts.csv` | Static HTML | Responsive tables with representative deal rows |
| 6 | Quota/commission | `quota-commission.html` | revops-analyst | `quota-targets.csv`, `crm-opportunities.csv` | Static HTML | Formula definitions and reconciliation notes remain visible |
| 7 | Project plan | `project-plan.html` | enablement | `data/manifest.json` and linked canonical CSVs | Static HTML | Static gates, owners, blocker, and validation steps |

The separate `../mock-forecast.html` is the detailed forecast example.
`../mock-arr-rollforward.xlsx` contains the full row-level detail. Native DOCX,
XLSX, and PPTX outputs are cataloged in the master guide; PDF instructional
CSVs and `../pdf-examples.md` support the PDF skill without pretending a PDF
render was inspected.

Keep this index aligned with the canonical guide when artifact filenames,
sources, or fallbacks change. The neutral skeletons in
`skills/delivery/vera-reporting/templates/` are generation inputs, not populated
tour outputs.
"""
write("tour/index.md", tour)
print("Built text examples, data dictionary, and example catalog")
