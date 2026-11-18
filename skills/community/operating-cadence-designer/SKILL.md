---
name: operating-cadence-designer
description: Use when the user asks about operating cadence, meeting architecture, decision rules, or says "our meetings are status updates" / "nobody makes decisions" / "nothing gets done". Designs and installs the weekly/monthly/quarterly rhythm that makes the revenue system real.
---

# Operating Cadence Designer

This skill designs and installs the operating cadence: the calendar that makes the revenue operating system real. It connects strategy (the strategy scorecard), visibility (the revenue dashboard), and execution (weekly/monthly rituals).

Without a cadence, leaders waste time in meetings that produce no decisions. With one, every ritual has a clear purpose, owner, and output. You are the cadence architect: your job is to design a rhythm with as few meetings as possible, each of which produces a decision or a logged action.

## When This Skill Activates

1. **No existing cadence** — no consistent rhythm for revenue decisions; leadership time fragmented across ad-hoc threads. Design task: build weekly + biweekly + monthly + quarterly rituals from scratch.
2. **Broken or inconsistent cadence** — some rituals happen, some get canceled; no clear escalation path. Design task: audit, apply the 5P gate, consolidate, install escalation rules.
3. **Cadence exists but no decision rules** — meetings happen, data gets reviewed, nothing changes. Status theater, not a control system. Design task: install signal-based decision rules and route triggers to rituals.

## The 5P Standard

Every meeting must pass the 5P gate. If any P is missing or fuzzy, the meeting should be canceled or rescheduled.

1. **Purpose** — one sentence: "By the end of this meeting, we will…" ending in a concrete outcome (decision, list, design, changed plan), not an activity (discuss, review).
2. **Product** — a tangible artifact: 3 decisions in the Decision Log with IDs and owners; a prioritized problem list; an A3 draft; an updated experiment backlog. Not "discuss pipeline" (verbs, not products).
3. **People** — the smallest set of roles that can create the product and own the actions. No spectators. Invite by role ("one VP Sales"), not "everyone from Sales".
4. **Process** — 2-5 bullet agenda with timeboxes; which dashboard panels; who facilitates, decides, takes notes.
5. **Proof** — the facts and pre-work so time is spent deciding, not discovering: metrics, customer quotes, win/loss summaries, A3 snippets. Pre-reads at least one working day before decision sessions.

**5P gate rule:** a healthy cadence has a non-zero cancel rate — 5-15% typical (practice-based). Zero means the gate isn't enforced; >20% means the calendar is overloaded.

## Cadence Design Workflow

### Phase 1: Assess Current State
Map existing meetings (owner, frequency, duration, attendees, stated purpose) → run the 5P audit on each → identify decision gaps (decisions made in side channels? is there a Decision Log?) → assess data readiness → interview key roles (CRO, CEO, CMO, VP Sales, Head of CS). **Output:** a 1-page current-state document with three ranked pain points and a sketch of what should exist.

### Phase 2: Design the Calendar

**Weekly (7 rituals, ~4.5 hours total):**
1. **Revenue Dashboard: Pipeline and Decisions** (75 min, CRO) — review bowtie, pipeline health, constraints; make at most 3 decisions or A3 assignments.
2. **Marketing Demand and Efficiency Loop** (45 min, CMO) — demand quality and SDR efficiency; adjusted campaign focus, new experiments with stop rules.
3. **Sales Pipeline and Efficiency Loop** (45 min, VP Sales) — pipeline health; clean pipeline, stuck items framed as A3s.
4. **CS Value and Efficiency Loop** (45 min, Head of CS) — retention and expansion; account attention list, countermeasures.
5. **Coaching and Revenue Craft Loop** (45 min, Sales + CS leaders) — turn customer conversations into better plays; coaching actions with check-in dates.
6. **Breach and Incident Huddle** (30 min, RevOps) — catch and contain SLO breaches; an owner and containment plan per breach.
7. **AI and Automation Integration** (45 min, RevOps + Platform, from Week 3) — embed AI at four levels (L1 signal tagging, L2 breach-detection agents, L3 experiment generation, L4 autonomous agents within guardrails); prioritized automation experiments with kill rules.

**Bi-weekly (1 ritual, 60 min):** Demo and Retro — show shipped experiments/countermeasures; decide keep/kill/scale.

**Monthly (2 rituals, 150 min):** Strategy and Lever Review (90 min, CEO + CRO — review scorecard, choose levers, adjust WIP and SLOs); Data Spine and Definition Review (60 min, RevOps + Data — check data freshness/completeness, confirm reverse-ETL activation: which signals route to which systems).

**Quarterly (1 ritual, 180 min):** Quarterly Reset (CEO) — refresh the strategy scorecard, confirm cadence, align next-quarter targets and SLOs.

**Key design rules:** keep weekly rituals short (no meeting >75 min); most rituals feed the same revenue dashboard — no parallel streams; reduce, never add (if tempted to add a meeting, cancel one first); schedule decision sessions early in the week.

### Phase 3: Build Ritual Cards
For each ritual, a one-pager: purpose, inputs, outputs, RACI (Driver/Approver/Contributors/Informed), tollgates, cancel rule, pre-work checklist. Print and post in the revenue-dashboard room.

### Phase 4: Install Signal-Based Decision Rules (Weeks 8-10)
Choose 8-12 signals where you already have data → set thresholds from 6 months of history → route triggers to rituals. Examples: pipeline coverage <2.5x for 3 weeks → Marketing Demand Loop; win rate drops >5pp → open A3 in Sales Pipeline Loop; decision latency >14 days → Strategy and Lever Review; 5P cancel rate 0% for 4 weeks → challenge in Strategy and Lever Review. No new meetings — clearer escalation rules.

### Phase 5: Transfer Ownership (Weeks 11-12)
A Cadence Owner (usually CRO or RevOps lead) becomes accountable for the calendar, enforcing the 5P gate, logging decisions, monitoring cadence health, and proposing changes only in the Quarterly Reset.

## 90-Day Installation Program

- **Phase 1: Stand-up (Weeks 1-2)** — audit, interviews, design calendar + ritual cards; brief leadership. Output: signed-off calendar.
- **Phase 2: Co-host (Weeks 3-6)** — run all rituals with you co-facilitating; enforce 5P strictly; log everything; build/update the revenue dashboard. Output: live cadence, 4 weeks of logged decisions.
- **Phase 3: Hand-off (Weeks 7-10)** — team leads, you coach; install signal-based rules. Output: team running cadence independently.
- **Phase 4: Certification (Weeks 11-12)** — team runs all rituals; transfer the Cadence Owner role; schedule quarterly reviews (tuning only in Quarterly Reset).

## Cadence Health KPIs

Review monthly in the Strategy and Lever Review; tune only in the Quarterly Reset.

1. **Decision latency** — insight → logged decision → live countermeasure. Target <7 days.
2. **5P cancel rate** — 5-15% healthy; 0% = gate not enforced; >20% = overloaded.
3. **SLO hit rate** — share of weeks key handover p95 SLOs met. Target >80%.
4. **Freshness attainment** — share of weekly data-spine checks passing. Target >95%.
5. **Forecast accuracy** — share of periods actual sits within forecast bands. Target >70%.
6. **Kill rate** — share of experiments killed by stop rule. Target 20%+ per quarter; <10% means no real stop rules.
7. **Coaching uptake** — share of coaching actions completed on time. Target >80%.

## Meeting Architecture & Ceremony Agendas

### The Data Pyramid

```
         BOARD (Quarterly, narrative + KPIs)
                |
         LEADERSHIP (Monthly/QBR, trends + decisions)
                |
         TEAM (Weekly, pipeline + forecast)
                |
         ACTIVITY (Daily, calls/deals/logs)
```

If activity is garbage → pipeline data lies → forecasts fail → board gets surprises.

### The 7-Question Meeting Architecture

| Element | Bad Answer | Good Answer |
|---------|-----------|-------------|
| Purpose | "Check on things" | "Lock forecast by Friday noon" |
| Frequency | "Weekly because that's what we do" | "Weekly for accountability, monthly for trends" |
| Participants | "The whole team" | "Sales managers + CRO only" |
| Inputs | People wing it | Pre-built forecast model + deal-aging report |
| Agenda | Meandering | 15 min data, 30 min decisions, 5 min actions |
| Outputs | "We'll figure it out" | Logged forecast, deal actions with owners |
| Accountability | Nobody | Action log with due dates + owner names |

**Rule:** if a meeting doesn't produce decisions or logged actions, send an email instead.

### Core Ceremony Agendas

**Daily Sales Pipeline Pulse (15 min):** surface blockers, coordinate same-day wins. RevOps not in the room; pre-built CRM views make it self-serve.

**Weekly Pipeline Review (45 min):** packet = stage movement (7 days), deal aging, forecast accuracy vs. prior week, win/loss summary. Agenda: 0-5 min context; 5-35 min deals >7 days old + red flags; 35-40 min commit vs. best case; 40-45 min logged actions.

**Weekly Forecast Roll-up (30 min, CRO + managers + RevOps):** 10 min company forecast vs. target; 15 min gap-closing actions; 5 min log decisions. Output: locked company forecast.

**Bi-weekly Funnel Review (60 min, Marketing + Sales + CS + RevOps):** MQL quality (15 min Marketing), lead-to-opp (10 Sales), opportunity velocity + close rates (15 RevOps), retention/expansion (10 CS), cross-functional actions (10).

**Monthly Business Review (90 min):** 8-10 slide deck — revenue vs. plan, pipeline health, efficiency (CAC/payback/LTV:CAC), retention/expansion, performance, risks, asks. Max 1 chart per slide.

**Quarterly QBR (half-day):** morning = revenue health, GTM performance, pipeline confidence, retention, steers; afternoon = board-deck dry run.

**Quarterly Board Meeting (2-3 hours):** 8-10 slides — Executive Summary + Asks → Revenue vs. Plan → Pipeline & Forecast → Efficiency → Retention & Expansion → GTM Update → Strategic Initiatives → Asks & Decisions. Golden rules: lead with narrative, show trends not snapshots, max 3 metrics per slide.

### Anti-Patterns

| Anti-pattern | Cost | Fix |
|---|---|---|
| Meetings without pre-read | 15 min wasted reading slides | Slides 24h before |
| Reviews without actions | Decisions forgotten by Wednesday | Log every action: owner, due date, success metric |
| Forecast as negotiation | Forecasts become useless | Make it analytical, not emotional |
| Dashboard theater | 40 metrics shown, 5 matter | Max 3-5 metrics per meeting, each tied to a decision |
| Cadence without accountability | Actions slip | Name owner, publish due date, review next meeting |
| Activity data not validated | Everything above the pyramid is garbage | Monthly CRM audit: who logs, are stage changes real |

### Framework Additions

**Closed-loop feedback:** upward flow Activity → Team Metrics → Leadership Review → Board; downward flow Board decisions → Strategy → Manager coaching → Rep behavior. Decision authority scales daily (rep) → weekly (manager/director) → monthly (VP) → quarterly (CRO/Board). Coaching happens *during* reviews — the cadence IS the coaching system.

**Discipline as AI prerequisite:** the #1 differentiator between top and average performers using AI is not which tools — it's operating discipline. Before any AI investment conversation, ask "how tight is your operating rhythm?"

**Operating Rhythm Assessment:**

| Dimension | 1 (Weak) | 3 (Adequate) | 5 (Strong) |
|-----------|---------|--------------|------------|
| Deal review frequency | Ad-hoc/monthly | Weekly, inconsistent | Weekly, never missed, structured |
| Pre-meeting data | None | Some manual | Automated packet 24h before |
| Decision logging | No actions | Noted, not tracked | Logged, owned, reviewed next meeting |
| Forecast accuracy | ±25%+ | ±15-20% | ±5-10% |
| Cross-functional sync | Teams don't talk | Monthly alignment | Bi-weekly funnel review, shared metrics |
| Coaching integration | Separate | Some in reviews | Pipeline review IS the coaching system |

**Scoring:** 24-30 = ready for AI investment; 15-23 = fix cadence first; <15 = cadence rebuild required.

### The 10-Minute Board Defense

A structured alternative to the 40-slide deck. Five questions: (1) Are we on track? — one number, one trend line, no spin. (2) Why? — win rate by segment and motion; top 3 loss reasons. (3) What changed? — actions taken this quarter, measured impact. (4) What do we need? — resource asks with projected ROI tied to conversion gaps. (5) What's the risk? — top 3 risks, specific.

The framework: 10-minute defense → 30 minutes to prepare → board gets answers immediately → trust compounds. The anti-pattern (40 slides → 2 hours prep → board skips to bad news) erodes trust.

## Quick Reference: Ritual Triggers

| Situation | Ritual to run | Why |
|---|---|---|
| No meetings at all | Weekly Revenue Dashboard | The hub everything else feeds |
| Meetings but no decisions | 5P audit on existing meetings | If a meeting fails 5P, cancel it |
| No one knows when to escalate | Signal-based decision rules | Explicit rules: signal fires → escalate here |
| Experiments never killed | Demo and Retro + Decision Log | Kill rate is a visible health metric |
| Strategy unclear, disconnected | Strategy and Lever Review + scorecard | Connects quarterly strategy to weekly countermeasures |
| Data outdated by decision time | Data Spine and Definition Review | Make data freshness a first-class ritual |
| Rituals keep getting canceled | Reduce the calendar, apply 5P strictly | Keep only rituals that produce decisions |

## Output

A self-contained cadence design — the ritual calendar (weekly/biweekly/monthly/quarterly with owners and products), ritual cards for each, the 8-12 signal-based decision rules with thresholds and routing, the cadence-health KPI set, and the operating-rhythm assessment score — plus a three-line chat summary naming the biggest decision-latency gap and the first ritual to fix.

- Every output is a self-contained file, ready to forward as-is — no platform-locked containers.
- Every number, rate, or claim goes through the analysis-validator before it ships: arithmetic recomputed, thresholds matched to their source.
- Plain operator English, short sentences, no hype.
