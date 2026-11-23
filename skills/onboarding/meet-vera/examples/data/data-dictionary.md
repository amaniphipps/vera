# Northwind data dictionary

## Provenance and scope

All records are deterministic, synthetic, and anonymized. Seed: `20261123`. Generated: `2026-11-23`. Currency: USD. No production export or real identity was used. Account and person aliases do not map to real entities. Contact emails use only the reserved `.invalid` domain.

The pack contains **12,578 records** across the tables below. ARR covers Q3 2026. Pipeline and forecast cover Q4 2026 as of Nov 23, 2026.

### `crm-accounts.csv`

Rows: **1,050**

Fields: account_id, account_alias, lifecycle_status, segment, industry, region, country, owner_id, owner_alias, plan_tier, billing_frequency, currency, account_created_date, customer_since_date, health_score, last_activity_date, acquisition_source, movement_category.

### `crm-contacts.csv`

Rows: **2,100**

Fields: contact_id, account_id, contact_alias, role, email, is_primary, last_engagement_date.

### `crm-opportunities.csv`

Rows: **600**

Fields: opportunity_id, account_id, opportunity_alias, owner_id, owner_alias, stage, forecast_category, amount_usd, expected_arr_usd, probability, created_date, close_date, last_activity_date, next_step_date, acquisition_source, product_family, opportunity_type, risk_status, next_step, win_reason, loss_reason, competitor_alias, period.

### `crm-stage-history.csv`

Rows: **2,366**

Fields: stage_history_id, opportunity_id, account_id, stage, sequence, entered_at, exited_at, owner_id.

### `crm-activities.csv`

Rows: **3,000**

Fields: activity_id, account_id, opportunity_id, owner_id, activity_type, activity_date, outcome, subject_alias.

### `arr-rollforward.csv`

Rows: **1,050**

Fields: account_id, period, starting_arr, new_arr, expansion_arr, contraction_arr, churn_arr, ending_arr, movement_category, previous_plan_tier, current_plan_tier, currency.

### `activation-users.csv`

Rows: **2,400**

Fields: user_id, account_id, user_alias, cohort_week, signup_date, activated, activated_date, retained_w2, acquisition_source.

### `quota-targets.csv`

Rows: **8**

Fields: owner_id, owner_alias, period, quota_usd, tier1_threshold, tier1_rate, tier2_threshold, tier2_rate, tier3_rate, currency.

### `pdf-invoice.csv`

Rows: **2**

Fields: invoice_id, item, quantity, unit_price_usd, line_total_usd.

### `pdf-quarterly-sales.csv`

Rows: **2**

Fields: product, q1_units, q2_units, q3_units, q4_units.

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
