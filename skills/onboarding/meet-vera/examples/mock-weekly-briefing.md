# Q4 pipeline briefing - Northwind, week of Nov 23

*Synthetic / anonymized output. Generated from the included CRM fixtures, not a live CRM.*

**The read:** 200 open deals carry $17.72M of expected ARR. Commit view is $7.01M including $2.53M already closed won; Best Case reaches $12.85M. The remaining upside sits in 60 Best Case deals, not in a weighted-forecast claim.

## What moved

- **Open pipeline:** $17.72M across 200 deals - 60 Commit, 60 Best Case, and 80 Pipeline.
- **Closed won to date:** $2.53M of Q4 expected ARR.
- **Scenario ladder:** $7.01M Commit view, $12.85M Best Case, and $20.24M if every open deal closes. Full pipeline is a ceiling, not a weighted forecast.

## What needs you

- **Risk review:** 43 at-risk deals and 48 watch deals are visible in `mock-pipeline.csv`. Start with forecast-category exposure, not just deal count.
- **Largest open opportunities:**
- **Opportunity 0401** - $0.57M, Best Case, Negotiation, closes 2026-12-17, On track.
- **Opportunity 0565** - $0.49M, Pipeline, Proposal, closes 2026-12-17, Watch.
- **Opportunity 0498** - $0.47M, Commit, Negotiation, closes 2026-11-28, On track.
- **Opportunity 0541** - $0.40M, Pipeline, Proposal, closes 2026-12-31, On track.
- **Opportunity 0419** - $0.40M, Best Case, Negotiation, closes 2026-12-07, On track.
- **Existing-book retention:** Q3 NRR was 96.4%; expansion covered 48.2% of contraction and churn. Keep the retention work alongside the Q4 close plan.

## Next

- Review Commit slippage and next steps for the largest at-risk opportunities.
- Inspect stage, owner, segment, and risk slices in `tour/pipeline-analysis.html`.
- Reconcile customer-level retention in `mock-arr-rollforward.xlsx`.

---
*Sources: `crm-opportunities.csv`, `arr-rollforward.csv`, and `crm-activities.csv`. Validated by Vera · Nov 23, 2026 · synthetic fixture arithmetic and cross-file reconciliation checked.*
