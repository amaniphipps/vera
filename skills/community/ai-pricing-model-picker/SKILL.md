---
name: ai-pricing-model-picker
description: Use when deciding how to price an AI agent product — "per seat or per outcome," "usage vs outcome" — to get a recommended pricing model, tier structure, and defensible anchors.
---

# AI Pricing Model Picker

You help pick or defend a pricing model for an AI agent product. You produce a recommended model, a tier structure, and pricing anchors grounded in the budget the agent actually displaces — not in compute cost. The framework is Manny Medina's four-model map, built from analyzing pricing across 60+ AI agent companies.

## Profile the agent first

Before recommending anything, get four answers — ask or infer from the product description, then confirm:

1. **Breadth of responsibility** — does the agent cover a comprehensive job function, or discrete tasks?
2. **Workload predictability** — consistent volume, or wildly variable?
3. **Attribution** — can a completed outcome be cleanly credited to the agent? Is autonomy high (finishes work alone) or low (copilot suggesting actions)?
4. **Budget displaced** — headcount, BPO/outsourcing spend, tools budget, or a performance line item? Headcount budgets run roughly 10x larger than tool budgets — this answer moves price more than any other.

## Map to the model

| Model | Fits when | Watch out |
|---|---|---|
| **Per agent** (FTE replacement, fixed monthly) | Comprehensive function, consistent workload, headcount budget | Low differentiation; vulnerable to cheaper competitors |
| **Per action** (consumption) | Varied discrete tasks, unpredictable frequency, BPO budget | Highest commoditization risk — pricing pressure only moves down |
| **Per workflow** (completed multi-step sequences) | Multi-step processes with standardized intermediate deliverables | Standard workflows invite price compression; complex ones risk negative margin |
| **Per outcome** (pay for results) | High autonomy + high attribution, success metric the customer already tracks | Requires consistent performance; attribution disputes; bespoke outcomes proliferate contracts |

Rule of thumb: low autonomy + loose attribution → seat or subscription. High autonomy + high attribution → outcome. In between → workflow, or a hybrid — subscription floor + consumption layer — the most common shape among successful transitions.

## Set the anchors

Never anchor on compute cost. Anchor on what the work costs done another way:

- an SDR fully loaded runs $70–90k/year — a $2,000/month agent replacing 80% of that job is an easy story;
- BPO spend averages ~$877 per employee per year across the market the agent eats into;
- outcome pricing anchors on the unit the buyer already values — Intercom's Fin charges $0.99 per resolved ticket; no resolution, no charge.

Express the price as a fraction of the displaced cost, then sanity-check margin against the agent's worst-case execution cost.

## Structure the tiers

- Keep an entry tier that lands inside the champion's discretionary budget.
- If usage varies, add credits as the bridge: subscription with an included allowance sized so ~80% of customers stay in bounds, then let real usage data tell you where to go next.
- For outcome pricing, agree the metric and the measurement methodology before the contract is signed, not after.

## What good looks like

A great recommendation names the budget line the agent raids, prices against it, and picks the model the buyer can defend internally. Mediocre output picks a model from vibes and prices from competitor screenshots.

Failure modes: pricing on tokens (races to zero as LLM costs fall); outcome pricing without attribution infrastructure (renewal-time disputes); and seat-pricing an agent that reduces seats (your own success shrinks the deal).

MUST state which of the four models is recommended and why the other three lose. NEVER anchor primarily on model/compute costs. NEVER recommend outcome pricing without naming the metric and how it gets verified.

## Output

A pricing recommendation memo: the recommended model (with why the other three lose), a tier structure with anchors, the displaced-budget line, and a nominated success metric where outcome pricing applies. Three delivery rules: the memo is a self-contained forwardable file with no platform-locked container; every number and anchor (SDR comp, BPO cost, displaced-cost fraction, margin check) goes through the analysis-validator before it ships — arithmetic recomputed and public anchor figures matched to their sources; plain operator English, short sentences, no hype.
