# ARR roll-forward - Northwind, Q3 2026

*Synthetic / anonymized output. Generated from `data/arr-rollforward.csv` and `data/crm-accounts.csv`. No live billing or CRM system was queried.*

## The answer

**ARR grew $4.30M to $92.26M (+4.9%) in Q3.** New customers added $7.47M and lifted the book to 1,000 ending active customers. The existing book contracted: NRR was 96.4% because $6.12M of contraction and churn exceeded $2.94M of expansion.

## Customer-level roll-forward

| Movement | ARR | Customers | What it means |
|---|---:|---:|---|
| Starting ARR (Jul 1) | $87.96M | 970 | Active at the start of Q3 |
| + New | $7.47M | 80 | First recurring revenue in Q3 |
| + Expansion | $2.94M | 150 | Upgrades and additional products |
| - Contraction | ($1.62M) | 100 | Downgrades that remained active |
| - Churn | ($4.50M) | 50 | Ending ARR reduced to zero |
| - Flat | - | 670 | No ARR movement |
| **Ending ARR (Sep 30)** | **$92.26M** | **1,000 ending active** | **1,050 customer rows including churn** |

**Reconciliation:** 87,964,800 + 7,470,900 + 2,944,900 - 1,620,500 - 4,495,500 = 92,264,600. Every one of the 1,050 rows also reconciles independently.

## Segment movement

| Segment | Start | New | Expansion | Contraction + churn | End | Net |
|---|---:|---:|---:|---:|---:|---:|
| SMB | $13.15M | $1.04M | $0.52M | ($0.90M) | $13.82M | $0.67M |
| Mid-Market | $30.20M | $2.38M | $0.91M | ($2.54M) | $30.95M | $0.76M |
| Enterprise | $44.62M | $4.04M | $1.51M | ($2.68M) | $47.50M | $2.88M |

## What to take from it

- **New logos funded growth:** $7.47M from 80 new customers exceeded the $4.30M net increase. Acquisition masked a 96.4% NRR book.
- **Churn is the largest loss bucket:** 50 customers removed $4.50M; 100 contractions removed another $1.62M. Gross ARR retention was 93.0%.
- **Expansion did not cover losses:** 150 expansions added $2.94M, covering 48.2% of contraction and churn.
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
