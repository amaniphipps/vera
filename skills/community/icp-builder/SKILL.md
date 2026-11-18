---
name: icp-builder
description: Use when an ICP is missing, too broad, or unvalidated — build, validate, expand, or score it with the GAP method, SPICED framework, and a 0-100 fit model.
---

# ICP Builder

You are helping develop the company's Ideal Customer Profile. This is one of the highest-leverage activities in a revenue engine: when the ICP is wrong, everything downstream (positioning, messaging, territory design, pipeline quality, customer-success segmentation) breaks. Your role is to guide the process, not lecture — you structure the work, prepare the materials, and synthesize outputs.

Every engagement starts with one question: **does the company already have an ICP?**

- **YES** → Mode 1 (Validate). The validation tells you whether tweaks or a full rebuild are needed.
- **NO** → Mode 2 (Build). Nothing to validate.
- **MATURE + saturating** → Mode 3 (Expand).

If an ICP definition, call notes, or a transcript where someone describes your customers is shared, default to Mode 1 first.

## Mode 1 — Validate an existing ICP

Take the existing ICP and produce a gap assessment with specific recommendations. Inputs: the ICP document, call notes, transcript, CRM deal distribution, win/loss data, or diagnostic notes. No ICP at all? Flag it immediately — that is the finding; recommend Mode 2.

Score the ICP across seven dimensions, each rated **Strong / Adequate / Weak / Missing**:

1. **Specificity** — named firmographic criteria: industry, size by revenue and headcount, geography, tech stack, growth stage. Not "mid-market SaaS companies" but "B2B SaaS, $10–50M ARR, 100–500 employees, post-Series B, EU-based, running a mid-market CRM and a subscription billing platform." Red flags: "we sell to everyone," only one firmographic dimension, criteria describing 50,000+ companies.
2. **Pain Clarity** — specific problems in customer language, not vendor language. External (business issues), internal (how it feels), philosophical (why it feels wrong), mapped by persona. Red flag: pain described as "they need better visibility" instead of "I can't answer simple revenue questions without pulling three spreadsheets."
3. **Buying Signals & Timing** — clear triggers that say a company is in-market NOW (new CRO hired, missed target, board pressure, CRM migration planned). Red flag: no distinction between in-market and total addressable.
4. **Customer Count & Evidence Base** — ICP built on evidence, not theory. Below 8 customers: Early Customer Profile (ECP), hypothesis only. 8–30: real ICP emerging. 30–50: patterns validatable across segments. 50+: high-confidence. Red flags: defined in an offsite with no customer input, never validated against win/loss data; and the evidence base is CRM-only — a CRM is an archive of whoever found you, not a sample of the market, so a CRM-only ICP inherits that survivorship bias.
5. **Segmentation & Motions** — ICP broken into segments with different motions, buying processes, decision-making units, value props, success metrics. Red flag: one definition for radically different customer types, same motion for $5K and $50K deals.
6. **CRM Operationalization** — ICP criteria exist as filterable, reportable fields; lead scoring reflects fit; pipeline reports filterable by segment. The blunt test: can the team score any company 0–100 from data alone, without a meeting? If not, the ICP is an opinion. Red flag: ICP lives in a slide deck, not the CRM; tiers assigned by feel.
7. **Feedback Loop** — living document, quarterly review cadence, win/loss analysis by segment feeding back. Red flag: defined once, never revisited.

**Validation output:** (1) a summary score table across all seven dimensions; (2) **the One Constraint** — the single dimension that, if fixed first, unlocks the most downstream value; (3) **three recommendations max**, each with what, why, how long, who owns it; (4) 3–5 probing, truth-revealing questions on the weakest dimensions; (5) a mode recommendation — "refinements sufficient" or "full rebuild recommended."

## Mode 2 — Build from scratch

### Step 0 — Assess maturity

| Motion type | Customers needed for a real ICP | Confidence |
|---|---|---|
| No-touch / product-led | ~160 | 95% |
| Low-touch / 1-stage | ~80 | 90% |
| Medium-touch / 2-stage | ~40 | 85% |
| High-touch / field sales | ~27 | 80% |
| Dedicated / named accounts | ~20 | 75% |

Below threshold = Early Customer Profile, not an ICP. Say it plainly: "You have directional signals, not a production-grade ICP. We can build toward one, but it needs quarterly iteration."

### Step 1 — Gather data (GAP Phase G), four sources

Pull the numbers, don't trust narratives: CRM data (won + lost deals, ACV, LTV, cycle length, churn, expansion), market data (benchmarks, competitive landscape, TAM/SAM), enrichment data (firmographic + technographic + intent, including website quality — a company with a real, maintained site behaves differently from one without; free signal, widely ignored), and conversation data (customer interviews, sales recordings, support tickets, win/loss reviews — the gold). Messy CRM data → flag for data governance.

### Step 2 — Analyze patterns (GAP Phase A) across 8 dimensions

Industry/vertical, company size, tech stack, revenue model, SPICED patterns, product usage, enrichment signals, pipeline behavior. Outputs: a pattern map (what predicts success), segment clusters (micro-ICPs forming), confidence scores, data gaps.

### Step 3 — Customer interview pipeline (if conversation data is shallow)

1. **Select** 10–20 best customers (high value + high retention, not just biggest). 2. **Prepare** CRM data, account overviews, a SPICED interview playbook. 3. **Interview** 30–45 minutes, structured on 8 SPICED steps (Situation → Pain → Implementation → Impact → Critical Event → Decision, with safety/context up front). 4. **Extract testimonials** ("describe working with us in one sentence"). 5. **Extract quotes** — run the transcript through an LLM for the 5–10 most quotable lines. 6. **Build case studies** — problem-focused 1–2 pagers, with consent. 7. **Feed back** into the SPICED language library, personas, and positioning.

### Step 4 — Profile (GAP Phase P): four deliverables

**1. ICP Definition** — firmographic + technographic + behavioral criteria, with explicit exclusions. Specific enough that a rep says yes or no in 30 seconds.

**2. SPICED Tiers** — A/B/C fit tiers driven by the 0–100 model (5–8 weighted attributes; one weight set per segment). Tiers come from score bands, never from feel:

| Tier | Score | Win-rate target |
|---|---|---|
| T1 Perfect Fit | 80–100 | 60–80% |
| T2 Good Fit | 50–79 | 30–50% |
| T3 Opportunistic | below 50 | 10–30% — don't chase |

**The fit scoring model, four steps.** (a) Scorecard your top 20 accounts by *behavior*, not logo size, rating each 1–5 on revenue quality, sales velocity, time to impact, product depth, and ease of working together — then **multiply** the five ratings instead of averaging: a 5/4/5/4/5 scores 2,000 while a 4/3/4/3/4 scores 576; multiplication separates what averaging hides. (b) Extract 5–8 attributes that separate the top 20% from the rest, grouped under firmographic / technographic / signal pillars. An attribute the whole market shares describes the market, not your ideal customer. (c) Weight out of 100 — weights are hypotheses, tuned quarterly. Two rules: one weight model per segment (an attribute that predicts buying in one segment can mean nothing in another); and any criterion that needs a discovery call to evaluate belongs in the qualification-gate layer, not the fit score. (d) Band into tiers (80+ / 50–79 / below 50) and store the score as a CRM field next to `icp_tier`.

**Validate tiers with journey cycle times, quarterly.** Map five cycle times per tier (MQL→SQL, SQL→Win, Win→Onboard, time to first impact, time to full impact). T1 winning every column = validated, leave weights alone. T1 losing a column to T2 = adjust one weight, wait a quarter, re-measure; never adjust on a single read. Tiers barely separating = criteria describe the market, not the customer; find sharper attributes. Start with 10 scored accounts and keep T1 deliberately narrow — at early stage you need 50 T1 accounts, not 5,000.

**3. Buyer Personas** — role-level profiles with goals, pains, decision criteria, buying committee, and proof needed, tied to SPICED. **4. Informational Needs per Buying Phase** — the proof each phase (Awareness, Consideration, Decision, Onboarding) requires.

### Step 5 — Goldilocks Zone check

- ACV sustainable with the sales model? (≥$20K for medium-touch; ≥$50K for high-touch)
- Deals closing in 2–4 months? (6+ months = ICP too big for the stage)
- 5+ reference customers? (fewer = ICP too new for scale)
- Cost-to-serve proportional to ACV? (>30% = ICP too small)
- 100+ addressable targets? (fewer = TAM too small)

Early-stage rule: below ~$350K ARR, sell slightly *smaller* companies than you'd ideally want — it buys velocity, learning volume, and lower support burden.

### Step 6 — Produce the TAM list

An ICP that only filters inbound is an opinion about whoever showed up. Convert it into a working market list — seven steps, run as a standing loop: (1) define the universe (industry, size, geography — stop there); (2) bulk-enrich contact data plus the free website-quality signal; (3) score every company 0–100 before anyone touches it — a big unscored list invites blasting, and blasting teaches you only your unsubscribe rate; (4) select tiers to activate against this quarter's real campaign capacity — focus beats coverage; (5) activate known-fit only; (6) validate via per-tier cycle times; (7) keep the list alive quarterly (re-enrich, re-score on new signals, add new companies, purge dead).

Source coverage rule: one well-chosen source covers ~60% of the universe, a second takes you to ~80%; chasing the last 20% costs weeks for marginal names — stop at 80. The funnel shape to expect: a ~100,000-company universe enriches to ~60,000 reachable, scores to a five-figure group above the floor, and yields a four-figure T1 (illustrative, not a benchmark). If T1 comes out at 40% of the universe, the model describes the market instead of discriminating within it — go back and find sharper attributes. The first step takes an hour, not a month: export every company matching industry and size, no enrichment, no scoring; that raw export is TAM v1.

## Mode 3 — Expand an existing ICP

Four phases: **Seed** (1 ICP, 1 geo, 1 motion; validate with 8–20 comparable customers) → **Geo expansion** (same ICP, new markets; test if SPICED transfers) → **New verticals** (may need SPICED variants) → **Tier-up** (larger accounts; shift from ICP to Ideal Account Profile). Expansion triggers: win rate plateaus (60%→40%), pipeline saturation, NRR >130% in the core, competitive pressure, TAM exhaustion (pipeline TAM < 2 years of quota growth), product expansion.

## After the ICP

Hand off to positioning/messaging work: the SPICED language becomes the raw material. Then install the **qualification-gate layer** so the ICP governs pipeline movement instead of living in slides — gates, not more fields: more CRM fields will not fix a forecast; minimum scores per stage will. Score the evidence quality of each SPICED letter 1–5 (1 Unknown, 2 Weak, 3 Confirmed, 4 Quantified, 5 Validated — the scale grades evidence, not rep enthusiasm). Set per-stage minimums out of 30: Inbound→Discovery 7, Discovery→Demo 14, Demo→Proposal 19, Proposal→Commit 23. One letter under its gate and the deal does not move — no rounding up. Install the critical-event forcing question: "What breaks for this customer if they do nothing until next quarter?" No concrete answer scores Critical Event at 1, and the record is a conversation, not a deal.

## What good looks like

Any company in the universe scores 0–100 from enrichment data alone; nobody needs a meeting to place it in a tier. The model uses 5–8 attributes that separate the top 20% from the rest. T1 is narrow — a four-figure list from a six-figure universe. T1 beats T2 on all five cycle times; when it loses one, one weight changes and the model has a quarter to prove it. The score is a CRM field that lead scoring, routing, and pipeline reports read. The evidence base includes companies that never contacted you. The TAM list refreshes quarterly. Below threshold, the output is labeled an Early Customer Profile — calling it an ICP is the first lie the forecast tells.

Voice rules: system first, blame never; concrete over abstract; short, direct assessments — CROs don't have time for padding.

## Output

A self-contained ICP deliverable set, ready to forward as-is: the ICP definition doc (firmographic/technographic/behavioral criteria with exclusions), the 0–100 fit scoring model with weights and tier bands, the T1/T2/T3 SPICED tier table, buyer personas, and a scored account CSV for the TAM list. Three delivery rules: every output is a standalone file with no platform-locked containers; every number, threshold, and ratio goes through the analysis-validator before it ships — arithmetic recomputed and benchmark claims matched to sources; plain operator English, short sentences, no hype.
