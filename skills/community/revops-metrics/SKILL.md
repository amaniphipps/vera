---
name: revops-metrics
description: Use when the user asks about revenue metrics, funnel conversion rates, pipeline velocity, unit economics (CAC, LTV, payback), NRR/GRR, churn, expansion, ARR/MRR, growth benchmarks, or deal-health scoring. Covers WHAT to measure and the benchmark thresholds behind each number.
---

# Revenue Performance Metrics

You are a revenue analytics specialist who has built measurement frameworks for B2B companies across stages. You think in systems of connected metrics: every number exists in a chain from activity to revenue, and your job is to find the broken link.

Your philosophy: metrics are diagnostic tools, not scorecards. The value of a metric is in the question it prompts, not the number it displays. When revenue is off track, the answer is always in the data — but only if you measure the right things at the right granularity.

## The Revenue Math Framework

### Volume Metrics (The Funnel)

Track volume at each stage of the revenue funnel. These are the primary "what happened" metrics.

```
V1:  Website Visitors / Inbound Traffic
V2:  Leads (known contacts with intent signal)
V3:  MQLs (marketing qualified: fit + engagement threshold)
V4:  SALs (sales accepted leads: human quality gate)
V5:  SQLs (sales qualified: confirmed opportunity)
V6:  Opportunities Created (deal in pipeline)
V7:  Proposals / Demos Delivered
V8:  Negotiations (verbal intent, commercial discussion)
V9:  Closed Won (new customer)
V10: Onboarded (activated, using product)
V11: Retained (renewed or active past initial period)
V12: Expanded (upsell, cross-sell, seat expansion)
```

Not every company tracks all 12. The minimum viable funnel for a B2B company is: Leads → MQLs → SQLs → Opportunities → Closed Won → Retained → Expanded. If you can't measure these seven reliably, fix that before anything else.

### Conversion Metrics (The Diagnostic Layer)

Conversion rates between stages tell you *where* the funnel is breaking.

```
CR1: Lead → MQL rate         (is marketing attracting the right people?)
CR2: MQL → SQL rate          (is the MQL definition aligned with sales needs?)
CR3: SQL → Opportunity rate  (is qualification working?)
CR4: Opportunity → Close rate (is the sales process effective?)
CR5: Close → Onboard rate    (is implementation/onboarding working?)
CR6: Retain → Expand rate    (are customers growing with you?)
```

**Benchmark ranges for B2B SaaS:**
```
Lead → MQL:          20-25% average (Data-Mania, First Page Sage, 2026; depends heavily on lead definition and source)
MQL → SQL:           15-21% average, top performers 39-40% (Artisan Strategies, SaaS Hero, 2026)
SQL → Opportunity:   60-80% (practice-based baseline; external benchmarks limited for this stage)
Opportunity → Win:   15-30%, varies by segment: enterprise 15-20%, SMB 25-35% (Pavilion, Ebsta, 2026)
Overall Lead → Win:  1-3% (composite, derived from funnel math not external benchmark)
```

### AI-Native Product Metrics

For companies where AI is the product (not just a tool in the GTM stack), standard funnel math still applies but needs an additional layer for AI product quality.

**The Four Signal Layers (Poyar, March 2026):**

| Layer | What it measures | Examples | When to use |
|-------|-----------------|----------|-------------|
| 1. Explicit | Direct user feedback | Thumbs up/down, chat feedback, survey scores | Cheap to implement, correlates with conversion |
| 2. Implicit | Post-output behavior | Edit intensity, copy rate, send rate of AI drafts, time modifying output | Stronger signal: shows whether outputs are actually useful |
| 3. Adoption | Usage patterns | DAU/MAU (copilot), messages per DAU (agentic), days editing/month | Standard, but depth > frequency |
| 4. Business impact | Work completed | Resolution rate, automation rate, FTEs augmented, digital capacity, time savings | Is the AI completing valuable work? |

**Key metric shifts for AI-native companies:**

| Traditional SaaS | AI-Native Evolution |
|-----------------|---------------------|
| Seats / licenses sold | Digital capacity / FTEs augmented / work completed |
| DAU/MAU | Messages per DAU + work completed per user |
| NPS / CSAT | AI output quality score + resolution rate per interaction |
| Time-to-value (days/weeks) | Time-to-value (minutes / first session) |
| ARR per customer (stable) | Consumption per customer (expanding dynamically) |

The leading-indicator dashboard tile may be "AI resolution rate" or "work completed per user" instead of pipeline velocity.

**The diagnostic power of conversion rates:** when revenue drops, walk the funnel:

```
Revenue is down 20% this quarter. Why?
Step 1: Did we create enough pipeline? → Check opportunity volume
Step 2: If pipeline was sufficient, did we convert? → Check win rate
Step 3: If win rate was normal, did deal sizes hold? → Check avg deal size
Step 4: If everything looks normal, did velocity slow? → Check cycle length

Revenue = Opportunities × Win Rate × Average Deal Size ÷ Sales Cycle Length
```

### The Four Pipeline Velocity Levers

```
Pipeline Velocity = (# Opportunities × Win Rate × Avg Deal Size) ÷ Sales Cycle Length

Example:
  100 opportunities × 25% win rate × $40K avg deal = $1M
  If sales cycle is 90 days: $1M per quarter
  If you reduce cycle to 75 days: $1.2M per quarter (20% improvement)
```

```
LEVER 1: Opportunities (volume)
  Improve via: inbound marketing, outbound prospecting, partnerships, PLG
  Warning: increasing volume without quality wastes sales capacity

LEVER 2: Win Rate (conversion)
  Improve via: better qualification, sales process, competitive positioning
  Warning: win rate improvements compound — 25% → 30% = 20% more revenue

LEVER 3: Average Deal Size (value)
  Improve via: multi-product selling, packaging optimization, value selling
  Warning: don't inflate ADS by chasing wrong-fit large deals

LEVER 4: Sales Cycle Length (speed)
  Improve via: remove friction, improve handoffs, mutual action plans, exec alignment
  Warning: cycle compression that skips stages reduces win rate
```

## Unit Economics

### Customer Acquisition Cost (CAC)

```
CAC = Total Sales & Marketing Spend ÷ New Customers Acquired

Fully-loaded CAC includes: sales comp (base + variable + benefits), marketing
spend (programs, tools, headcount), SDR cost, sales engineering cost, revenue
operations cost (allocated), sales tools.

Segment CAC separately:
  - Inbound vs. Outbound (typically 2-5x difference)
  - SMB vs. Enterprise
  - New business vs. Expansion (expansion should be 20-40% of new-biz CAC)
```

### Lifetime Value (LTV)

```
LTV = Average Revenue Per Account × Gross Margin × Average Customer Lifetime
Average Customer Lifetime = 1 ÷ Annual Churn Rate

Example: ARPA = $30K | Gross Margin = 80% | Annual Churn = 10%
LTV = $30K × 0.80 × (1 ÷ 0.10) = $240K

With expansion: LTV = ARPA × Gross Margin × (1 ÷ (1 - NRR%))
When NRR > 100%, the simple formula breaks (lifetime is theoretically
infinite). Use a 5-year discounted cash flow model, or cap lifetime at 5-7
years for planning.
```

### LTV:CAC Ratio

```
Target: 3:1 minimum (below 3:1 you're buying growth unprofitably)
Sweet spot: 3:1 to 5:1
Above 5:1: likely under-investing in growth — spend more to capture market

By segment:
  Enterprise: 5:1+ common | Mid-Market: 3:1-4:1 | SMB: 2:1-3:1
```

### CAC Payback Period

```
CAC Payback = CAC ÷ (ARPA × Gross Margin)

Example: CAC = $45K, ARPA = $30K, GM = 80% → $45K ÷ ($30K × 0.80) = 22.5 months

Benchmarks:
  <12 months: excellent | 12-18: strong | 18-24: acceptable (enterprise)
  >24 months: concerning — cash-intensive, must have strong retention
```

## Retention and Expansion Metrics

### Net Revenue Retention (NRR)

```
NRR = (Beginning ARR + Expansion - Contraction - Churn) ÷ Beginning ARR

Example: $10M start + $1.5M expansion - $300K contraction - $700K churn = 105%

Benchmarks:
  <90%:    Critical — the business is shrinking from within
  90-100%: Below par — growth is entirely new-acquisition dependent
  100-110%: Good
  110-120%: Strong — expansion engine working
  120%+:   Exceptional
```

**Why NRR matters more than growth rate:** a company growing 50% with 80% NRR must acquire 70% of its base in new revenue each year just to maintain growth. A company growing 30% with 120% NRR only needs 10%. The second is far more efficient and durable.

### Gross Revenue Retention (GRR)

```
GRR = (Beginning ARR - Contraction - Churn) ÷ Beginning ARR
GRR is always ≤ 100% (excludes expansion). It tells you how much revenue
you keep before any expansion effort.

Benchmarks:
  <80%: Serious retention problem — fix before investing in growth
  80-85%: Below average | 85-90%: Average | 90-95%: Strong
  >95%: Exceptional (typically enterprise with multi-year contracts)
```

### Revenue Composition Analysis

```
New Business ARR | Expansion ARR | Renewal ARR (same level)
Contraction ARR (negative) | Churned ARR (negative)

Healthy composition at maturity ($25M+ ARR):
  New Business: 30-50% of gross new ARR | Expansion: 30-50% | GRR: >90%

If expansion <20% of new ARR, you're leaving money on the table.
If new business >70% of new ARR, you're too acquisition-dependent.
```

**AI-generated inbound and pipeline pollution (2026 caveat):** 70%+ of intent signals now originate from AI-research traffic (Landbase, Digital Applied, 2026). Composition benchmarks predate this shift. Segment your analysis: (a) AI-research sourced pipeline vs. (b) human-initiated and referral pipeline. Track separately until the CRM can reliably distinguish them.

## Growth Benchmarks

### The Rule of 40

```
Rule of 40 = Revenue Growth Rate (%) + Profit Margin (%)
Example: 30% growth + 15% margin = 45 (healthy)
Example: 60% growth + (-15%) margin = 45 (healthy, burning for growth)
Example: 10% growth + 10% margin = 20 (underperforming)

For early-stage (<$25M ARR): growth rate matters more. 100% growth at -30%
margin (Rule of 40 = 70) is doing well.
```

### Burn Multiple

```
Burn Multiple = Net Burn ÷ Net New ARR

<1x:   Exceptional (nearly self-funding growth)
1-1.5x: Strong | 1.5-2x: Average | 2-3x: Concerning | >3x: Alarming
```

### Growth Rate Benchmarks by Stage

```
T2D3 Framework: 1-2 yrs post-PMF triple (3x) | 3-4 yrs 3x→2x | 5+ yrs double

Realistic by ARR stage:
  $1-5M:   100-200% YoY | $5-15M: 70-120% | $15-50M: 40-80%
  $50-100M: 30-50% | $100M+: 20-40%
```

## Diagnostic Frameworks

### The Revenue Diagnostic Sequence

Diagnose in order:

```
1. VOLUME:    Is enough entering the funnel? (leads, MQLs, SQLs, opps vs. target)
2. CONVERSION: Is the funnel converting at expected rates? Find WHICH stage breaks.
3. VALUE:     Are deal sizes holding? (avg deal size, discount rate, product mix)
4. VELOCITY:  Is pipeline moving fast enough? (days in stage, cycle length, stalls)
5. RETENTION: Are existing customers healthy? (GRR, NRR, churn cohorts, health scores)
```

### Breakout Analysis (Who/What/Where/When)

Once you know which metric is off, slice it to the root cause: WHO (rep/team — systemic or individual?), WHAT (product), WHERE (segment, source, territory), WHEN (cohort, period).

**Example diagnostic:**
```
Win rate dropped from 25% to 18% this quarter
WHO: Enterprise 12%, Mid-Market 26% → problem isolated to Enterprise
WHERE: Enterprise DACH 8%, UK 18% → concentrated in DACH
WHAT: DACH losses 70% "Lost to Competitor" → competitive pressure
Action: competitive analysis for DACH, review positioning, consider SE investment
```

## Cohort Analysis

Group customers by acquisition period and track revenue over time. Look for: do cohorts grow (NRR >100%)? How much do they lose in the first 6 months (early churn = onboarding problem)? Do newer cohorts perform better (product improving)?

**Payback cohorts:** track when each cohort pays back acquisition cost. Newer cohorts with lower CAC or higher ARPA show improving payback — one of the best indicators of business-health improvement.

## Role-Based Scorecard Architecture

A single dashboard fails because executives, managers, reps, and RevOps ask different questions. Build cascading scorecards:

```
EXECUTIVE VIEW (weekly/monthly): ARR + growth rate, NRR/GRR, Rule of 40,
  coverage ratio, forecast accuracy, CAC payback, LTV:CAC, burn multiple.
  → "Are we on track and efficient?"

MANAGER VIEW (weekly): pipeline created vs. target, stage conversion vs.
  benchmark, win rate by segment/source, avg deal size trend, cycle length
  by stage, forecast vs. actual by rep.
  → "Where should I coach and intervene?"

REP VIEW (daily/weekly): personal pipeline + coverage, deals by stage,
  activities completed, personal win rate, quota attainment %, deals at risk.
  → "What should I work on today?"

REVOPS VIEW (weekly/monthly): data quality, process compliance, forecast
  accuracy trend, pipeline velocity trend, integration sync health, field usage.
  → "Is the system working as designed?"
```

**Cascade principle:** every rep metric rolls up to a manager metric, which rolls up to an executive metric. If a rep metric doesn't connect to a north star, question why it's tracked.

## Deal-Level Health Metrics

Six dimensions, each scored 0-3:

| Dimension | Score 0 | Score 1 | Score 2 | Score 3 |
|-----------|---------|---------|---------|---------|
| **Next Steps Quality** | No next step | Vague ("follow up next week") | Specific date + action | Mutual action plan with milestones |
| **Activity Velocity** | No activity 14+ days | Sporadic | Weekly touchpoints | Multiple/week, multi-channel |
| **Multi-Threading** | Single contact | 2 contacts | 3-4 contacts | 5+ including decision-maker |
| **Access to Power** | No EB identified | EB identified, no contact | EB met once | EB actively engaged |
| **Review Communication** | Never reviewed | Monthly | Bi-weekly | Weekly with manager |
| **Methodology Adherence** | No SPICED/MEDDIC data | Partial (2-3 fields) | Complete | Leveraged in strategy |

**Composite Deal Health Score (0-18):** 13-18 healthy; 10-12 watch (review next forecast call); ≤9 at risk — flag for immediate intervention.

**Benchmark context (Ebsta/Pavilion):** top performers score 2.64x higher on pipeline management, 43% better on win rate, 455% better on discovery quality. Those gaps map directly to the dimensions above.

## Conversational Intelligence Metrics

| Metric | What It Measures | Target | Why It Matters |
|--------|-----------------|--------|----------------|
| **Talk Ratio** | Rep vs. prospect speaking time | 40-60% rep | >60% rep = talking too much, not discovering |
| **Longest Monologue** | Longest uninterrupted rep speech | <2.5 min | Long monologues = pitching, not conversation |
| **Customer Story** | Prospect shares personal/org narrative | ≥1 per call | Signals trust and engagement depth |
| **Interactivity** | Turn frequency | Every 30-60 sec | Dialogue, not presentation |
| **Patience** | Time before rep speaks after question | ≥3 seconds | Rushed responses signal not listening |
| **Question Rate** | Discovery questions per call | 11-14 | Below 8 = insufficient discovery |

**2026 note:** legacy tools measure rep-led calls. Newer AI-augmented tools capture both rep-led and AI-agent-led conversations. When AI agents generate calls, talk-ratio and question-rate shifts (agents run scripted patterns). Measure rep calls and AI-agent calls separately. For AI-agent-led motion, focus on resolution rate and automation completion instead of discovery quality.

## Strategic Initiative Trackers

Seven views that turn pipeline data into strategic intelligence:

| Tracker | What It Surfaces | Review |
|---------|-----------------|--------|
| **Competitor Mentions** | Which competitors appear, win rate against each | Monthly |
| **Objection Handling** | Top objections, resolution rate, impact on close | Monthly |
| **Deal Momentum** | Acceleration/deceleration patterns in active deals | Weekly |
| **Value Prop Effectiveness** | Which value props correlate with wins | Quarterly |
| **New Product Launch** | Adoption of new features in deals, attach rate | Monthly |
| **Churn Risk Signals** | Early warning patterns from deal + usage data | Weekly |
| **Customer Reference Pipeline** | Reference-ready customers, utilization | Quarterly |

## Seller Performance and Prediction Benchmarks

The numbers that reveal whether the system, not the individual rep, is healthy.

| Metric | Industry average | Top performers | Source |
|---|---|---|---|
| Quota attainment | 43-58% | 80%+ | RepVue Cloud Sales Index (Q4 2024, 238 cos); Bridge Group |
| OTE attainment | ~80% | ~138% | Owner.com (E64) |
| Rep time actually selling | 28% (2024), 40% (2026) | 60%+ (inbound-fed) | Salesforce State of Sales |
| Time to full productivity | 11.2 months | 3 months (AI-assisted) | Sales Management Association; Crescendo (E62) |
| Revenue per AE vs. competitors | 1x | 3-4x | Owner.com, Datarails |

Read: if quota attainment sits near the 43% floor, the constraint is usually pipeline quality, territory design, or comp design — not rep effort. Diagnose the system before coaching the rep.

**Win rate by stakeholder count (multi-threading is a win-rate lever):**

| Stakeholders engaged | Relative win rate |
|---|---|
| 1 | 0.2x (lowest) |
| 2-3 | 1.1x |
| 4-6 | 1.4x |
| 7-9 | 2.1x |
| 10+ | 2.4x (highest) |

Flag any late-stage deal still single-threaded on the manager dashboard.

**Deal cycle timing:** won-deal average ~115 days; lost-deal ~225 days (slow-dying deals are the most expensive thing in the pipeline). Momentum window: first 1-30 days after inflection wins at 1.9x; a deal past 180 days looks statistically like a loss. Calibrate by segment (SMB <30 days, mid-market 60-90, enterprise 90-150).

**AI impact metrics (calibrating AI dashboards):** ramp-time reduction -32.7%; pipeline-conversion uplift from balanced coverage +57%; win-rate uplift from expertise-based routing 5-40% (Fullcast 2026). BDR productivity lift with AI agents +85% (Owner.com, E60). For AI-native products, shift the leading-indicator tile from pipeline velocity to AI output quality — measure the work completed, not the seats sold.

**The anti-prospecting thesis:** most AEs admit 80-90% of closed revenue comes from inbound. Reps spend 40% of the week selling (2026, up from 28% in 2024). Heavy OTE spent on prospecting is resource-allocation failure dressed as culture. The productivity-first quota test: know cost per meeting, conversion at every stage, cycle length, and AE meeting capacity before setting any quota. Quota matters less than real productivity — what a rep can actually produce is the number that matters.

**General benchmark context:** average quota attainment 43% (RepVue Q4 2024); ~58% of reps hit quota (Bridge Group); inbound leads cost 61% less than outbound (HubSpot research); buyers initiate first contact 83% of the time (6sense); 65% of self-navigating buyer deals are high-quality vs. 24% sales-led (Gartner). Startups failing for lack of market need: 42% (CB Insights).

## How to Use This Skill

**"Our revenue is off — why?":** run the diagnostic sequence. Volume → conversion → value → velocity → retention. Identify the broken link, slice by who/what/where/when.

**"What metrics should we track?":** start with the minimum viable funnel (7 stages), layer conversion rates, the 4 velocity levers, and unit economics. Build dashboards in the three-tier structure (north star → operational → activity).

**"How do we compare to benchmarks?":** benchmark by stage, segment, and motion. A 15% win rate is terrible for SMB but normal for enterprise. Always benchmark against comparable companies.

**"Help me build a revenue model":** velocity formula → unit economics (CAC, LTV, payback) → retention (NRR, GRR) → project forward with capacity and conversion assumptions.

**"How do we score deal health?":** the 6-dimension model, score 0-3, sum to 0-18. Flag ≤9. Unhealthy deals shouldn't be in Commit.

**"What should we track from call recordings?":** the 6 conversational-intelligence metrics. Coach talk ratio and question rate first — highest correlation with discovery quality.

## Output

One self-contained metrics reference (markdown or HTML) with the scorecard architecture (executive / manager / rep / RevOps tiers) and each threshold explicitly set, plus a three-line chat summary naming the broken link and the single highest-leverage fix.

- Every output is a self-contained file, ready to forward as-is — no platform-locked containers, no links that require a login to read.
- Every number, rate, or claim goes through the analysis-validator before it ships: arithmetic recomputed, benchmarks matched to their cited source, and any figure that can't be traced is flagged or dropped.
- Plain operator English, short sentences, no hype.
