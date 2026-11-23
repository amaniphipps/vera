# Vera example catalog

One canonical location for Vera's synthetic datasets and generated examples. Everything is synthetic and anonymized. No live system is queried.

## Start here

- **Visual gallery:** `index.html`
- **Data dictionary:** `data/data-dictionary.md`
- **Validated metrics and source hashes:** `data/manifest.json`
- **Output hashes and cross-format QA:** `data/validation-summary.json`

## Dataset at a glance

- **12,578 linked records**
- **1,000 ending active customers** across 1,050 ARR rows, including 50 churned records
- **200 open opportunities** and **400 closed opportunities**
- **2,100 contacts**, **3,000 activities**, and **2,400 activation users**
- **$92.26M ending ARR**, **$17.72M open expected ARR**

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
