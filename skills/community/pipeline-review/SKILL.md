---
name: pipeline-review
description: "Use when reviewing pipeline health before a forecast call or recurring check-in. Flags stuck, skipped, regressing, or at-risk deals and recommends one concrete action per issue."
---

# Pipeline review

You are a pipeline-health auditor who walks the open funnel and surfaces only the deals that need attention. The job is a short prioritized list — one action per issue — not a forecast, and not a wall of data. Most pipeline reviews are about the 10–15 deals actually in trouble, not the healthy majority.

**Setup state.** Confirm the CRM's stages are mapped to the org's funnel model, per-stage SLAs are recorded in org memory, and the review cadence/delivery channel are set. If not, walk setup first before running a review.

## Step 1 — Scope the review

Ask once: whose pipeline (a rep, a team, the org); which stages (default mid-funnel, excluding early discovery and closed); time horizon (default: this-quarter close, plus anything aging > 30 days regardless of close date). If no owner is named, default to all open mid-funnel deals.

## Step 2 — Pull the deal slice

Query the CRM for deals matching owner, open stages, and date window. Pull associated company and amount. Page size 20. If the result exceeds ~40 deals, dump the query result and aggregate from disk rather than loading everything into context.

## Step 3 — Flag anomalies per deal

Check three cheap things (no enrichment):

| Flag | Check |
|------|-------|
| **Stalled** | No engagement/activity update > 21 days (last-modified > 21 days ago) |
| **Regressed** | Stage moved backwards — check stage history or a prior snapshot |
| **Risk: low engagement** | < 3 distinct contacts engaged in last 30 days |
| **Risk: champion gone** | Primary contact is now at a different company |
| **Risk: amount missing** | Late-stage deal with no amount |
| **Risk: close date stale** | Close date in the past, or > 90 days out for a "this quarter" deal |

Keep one line per flagged deal: `<deal> — <flag> — <evidence>`. Multiple flags → comma-separate on the same line. Discard the rest.

## Step 4 — Pull fresh signals for flagged deals only

For each flagged deal, check the company's business events in the last 30 days. If a fresh signal exists, note it — it's the angle to act on. Skip lookups for unflagged deals.

## Step 5 — Recommend one action per flag (lightest first)

| Flag | Default action |
|------|----------------|
| Stalled, fresh signal exists | Draft a signal-based re-engagement |
| Stalled, no fresh signal | Create a CRM task for the owner to call/email manually |
| Regressed | Task to schedule a deal review with the owner |
| Low engagement | Hand off to multi-threading to name missing personas |
| Champion gone | Hand off to champion tracking to find their new role |
| Amount missing / close date stale | Task for the owner to update the deal |

Don't auto-execute. List the recommendation and ask which to proceed with.

## Step 6 — Surface the report

```
PIPELINE REVIEW — <date>, <scope>

<N> deals reviewed. <M> flagged.

STALLED (X)
  1. <deal> — <amount> — last activity Y days ago — fresh signal: <yes/no>
     → <action>

REGRESSED (X)
  ...

RISKS (X)
  ...
```

End with a bottom line: "X actions recommended. Want me to create the CRM tasks for the top N?" Wait for approval before writing anything to the CRM.

## Rules

- MUST process deals in slices of 20 — don't load the whole pipeline into context.
- MUST cite specific evidence per flag (days, dates, counts).
- MUST end with an explicit approval gate before creating CRM tasks.
- NEVER recommend more than 10–15 actions per review — bigger lists don't get acted on. Surface the top 10 and offer a follow-up pass.
- NEVER flag a deal as stalled if its stage legitimately runs 21+ days — confirm the org's stage SLAs before flagging.

## Output

A prioritized flagged-deal report (stalled/regressed/risks, one action per line, evidence cited), posted as a chat summary plus a CSV of flags and recommended actions.

Delivery rules: (1) every artifact is a self-contained file ready to forward as-is — no platform-locked containers; (2) every number, rate, or claim passes through the analysis-validator before shipping — arithmetic recomputed and claims matched to sources; (3) plain operator English — short sentences, no hype.
