# Guided tour index - synthetic Northwind examples

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
