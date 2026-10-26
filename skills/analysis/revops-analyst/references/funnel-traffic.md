# Funnel Traffic Analysis

Attribute top-of-funnel and channel performance: where leads come from, what
they cost, and what they produce downstream.

## Cadence model (decide first)

- Monthly: analyze the previous calendar month, plan the next month.
- Quarter-end (when the prior month closes a quarter): analyze the full prior
  quarter, plan the next quarter.

If ambiguous, ask. Every tab and title follows the chosen cadence.

## Funnel stages (org slots)

Define the stages once. A common shape:

```
Lead (marketing-qualified) -> Qualified lead -> Opportunity -> Pipeline -> Won
```

Record the stage names and the field holding each stamp in `org.example.yaml`.
Do not reuse a stage name for two things.

## Attribution model shapes

- First-touch: the source/channel/campaign of the first contact. Your default
  for volume and cost-per metrics.
- Last-touch: the most recent interaction before conversion.
- Platform-reported: an ad platform's own revenue attribution, used only for
  channels where first-touch is structurally zero (for example, an account-
  based social channel). Always labeled as self-reported and directional.
- Subscription channels: fixed-cost channels (annual listings, sponsored
  placements) are not ad spend. Compute their cost per stage against the fixed
  fee and footnote that it is not adjustable spend.

State the model in the output. Mixing first-touch and platform-reported
numbers in one total is a defect.

## Gathering inputs before pulling

Some inputs are not reachable through connectors and must be supplied:

- Paid spend by channel for the period.
- Platform-reported revenue/attribution for channels that need it.
- Any new or experimental channels.

Ask for these before building. Do not invent them.

## Metrics

- Cost per lead / cost per qualified lead.
- Cost per opportunity.
- Pipeline generated per channel.
- Pipeline ROAS = pipeline value / spend.
- Win rate per channel.
- A segmentation flag you track through the funnel (for example, an
  audience-quality or ideal-fit label), reported as a segment, never as a
  filter that narrows the dataset.

## Pitfalls

- Case sensitivity in source values ("Outbound" vs "outbound"). Normalize and
  count the field, not the channel.
- Single-deal outliers: when one deal dominates a channel's pipeline, flag the
  N=1 warning instead of presenting a trend.
- Cross-system count drift: the warehouse and the CRM can disagree on lead
  counts because of sync timing. Note it, do not merge the two silently.
- Period vs all-time: some channels are best read all-time. Show all-time
  alongside period, and never blend the two timeframes in one total.
- Do not apply an ideal-fit filter to the dataset; report the flag as a
  segment so the full picture stays intact.

## Output shape

1. Recommendations (forward plan): proposed spend, priorities with rationale,
   and a budget table of prior vs proposed vs change.
2. Prior-period insights: investment summary and one card per channel.
3. Paid deep dive: full metrics table, segmentation, and data notes (always
   list the inputs that must be supplied manually).
4. Organic deep dive: volume, pipeline, average deal size, and a source audit
   for channels expected but not found.

Output is ready to forward as-is.