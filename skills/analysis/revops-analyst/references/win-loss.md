# Win-Loss Analysis

Analyze why deals were lost. Be honest about the seller's part, and do not
overclaim on a small sample.

## Scope boundary

This is lost-deals analysis. It does not cover customer churn or recurring-
revenue contraction. If a question mixes the two, split them and handle only
the lost-deal side here.

## Three sources, always

1. Rep-entered loss reason: what the rep filed. Fast signal, often incomplete
   and self-flattering ("budget", "went dark"). Read it, never classify from
   it alone.
2. AI-synthesized loss reason: built from the full deal history when your CRM
   offers it. The primary classification input when present.
3. Full conversation evidence: call transcripts, emails, notes, tasks. The
   ground truth. Use it when the AI field is blank and for every deep-dive and
   high-value deal.

The gap between source 1 and source 3 is itself a finding: the rep reason
says "budget", the transcripts show the economic buyer was never engaged.

## The two-bucket framework

Every loss has two kinds of contributors. Classify both, never just one.

- Seller-side: what the org did or failed to do. Examples: single-threaded
  champion, no business case built, wrong counter-position to the named
  competitor, delayed follow-up in the post-demo or post-pricing window, rep
  departed with no warm hand-off, a billing or systems error during
  evaluation, legal inflexibility, a known product gap not surfaced at
  qualification.
- Buyer-side: their decision and context. Examples: competitive displacement
  (named), champion left, budget denied by the economic buyer, initiative
  deprioritized, restructuring, build-in-house, genuine product gap, not a fit,
  incumbent inertia, deferred to a later budget.

The categories are illustrative, not exhaustive. When the evidence surfaces a
pattern not listed, name it from the evidence. Do not force it into the
nearest bucket.

## Next-step validity check

A rep's "next step" field on a closed-lost deal is often stale, describing
something already done. Before using it as evidence of deal state, check the
last actual contact and the most recent email or call. A stale next step on a
lost deal is itself a seller-side signal: the rep stopped managing it.

## Honesty and sample size

- State the coverage rate first: how many deals have a real classification vs
  a one-line rep reason vs no signal.
- Aim for 95%+ classification. Deals with no signal anywhere are flagged as a
  data-hygiene gap, never smuggled into a loss-reason bucket.
- "MIA" and "unresponsive" are outcomes, not reasons. Dig into the evidence to
  find the cause.
- On a small cohort, use count-and-direction language ("observed across N
  deals"), never "data confirms". A table built on five deals does not
  generalize.
- Never aggregate competitors into "other". Name every one.

## Modes

1. Pattern analysis: all losses in a period, default trailing 12 months. Break
   out by seller-side, buyer-side, competitor, owner, and deal-size tier.
2. Single-deal post-mortem: chronological timeline from first contact to loss,
   both buckets with citations to the specific call or email, and the gap
   between the rep reason and the evidence.
3. Competitive analysis: losses grouped by named competitor: count, value,
   average deal size, stage at loss, and the seller-side pattern that gave the
   competitor the opening, plus one counter-position each.
4. Active-pipeline risk match: run the loss profile on the last 6 months, then
   score open deals against the loss signals (hold language, budget concern,
   named competitor, executive change, stale next step).

## Output shape

1. Coverage block: period, deals analyzed, AI-field vs blank rate, stale
   next-step rate, hygiene and coaching gaps.
2. Top-line finding: lead with the single most important claim.
3. Seller-side table and buyer-side table: pattern, count, share, value.
4. Competitive table: named competitor, deals, value, top owner, stage.
5. Owner rollup and deal-size rollup.
6. Interventions: for the top three seller-side patterns, one specific action
   tied to the actual frequency and value, not generic advice.

Output is ready to forward as-is.