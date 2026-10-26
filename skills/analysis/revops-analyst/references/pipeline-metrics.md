# Pipeline Metrics

Score and tier the active pipeline, and report conversion, velocity, and
health. Every definition here is an org slot; set them once in `org.example.yaml`
and reuse across runs.

## Pull the active pipeline

- Positive filter on active stages only. Never rely on "exclude closed"; a
  closed-but-future-effective deal will leak in.
- Deduplicate by record ID. Pagination can repeat a row.
- Resolve owners live. Never use a stored owner-ID table; it rots.
- Bound every second-source query to the pulled record IDs and a time window.
  Never run an unbounded scan.

## Multi-signal scoring

Score each deal on several signals, each carrying points. Stage and forecast
category are often collinear (commit equals late stage), so treat them as one
signal, not two. Representative signals:

| Signal | What it reads | Direction |
|---|---|---|
| Seller conviction | stage x forecast category, plus the rep's explicit flag | higher is better |
| Buyer replies | count of inbound buyer messages | higher is better |
| Meetings | meeting count, upcoming meeting, buyer-booked meeting | higher is better |
| Conversation sentiment | terminal / soft-negative / neutral / strong-positive | negative pulls down |
| Buyer language | next-step text with commitment phrases | lock phrases add |
| Multithreading | number of contacts | fewer than 2 is a penalty |
| Recency | days since last contact | older is worse |
| Stage momentum | days in current stage vs the live median | stale is worse |
| Why-buy | recorded pain, timeline, motivation | incomplete is worse |

Loss-pattern penalties (from the win-loss mode) are additive. A named
competitor is a flag, not a penalty; price the risk through loss patterns.

## Tier assignment

Define tiers by score bands plus stage and staleness gates. The bands and
names are org slots. A standard shape: a top tier (lock), an action tier, a
build tier, a watch tier, and a forced-risk tier for terminal-negative,
departed-owner, or effectively-dead deals. One deal gets one tier; on a tie,
keep the higher tier.

## What "healthy" looks like (org-tunable)

These are default reads, not laws. Tune to your org:

- Coverage: total addressable pipeline should be a multiple (often 3x to 4x)
  of the target. Below that is a gap.
- Stage mix: most of the closeable value sits in the late stages, not the top
  of the funnel.
- Velocity: time-in-stage near or under the median for that stage. Median is
  computed from the current pull, not a stored constant.
- Aging: a rising share of deals older than the typical sales cycle is a stall
  signal.
- Single-threaded share: a high share of deals with one contact predicts loss.
- Dark share: a high share of late-stage deals with no recorded call.

## Calibration check (every run)

After tiering, sanity-check the distribution. If the top tier exactly equals
one single field (for example, "DS5 commit"), the other signals are not
contributing and a second source likely failed. If one tier holds most of the
deals, note it. Never adjust thresholds mid-run to make the distribution look
better.

## Conversion metrics

- Stage-to-stage conversion: deals advancing from stage N to N+1 over the
  period, over deals that entered stage N.
- Win rate: closed-won over (closed-won + closed-lost).
- Median sales cycle: days from create to close.
- These need a period window and a cohort definition; state both.

## Output shape

1. KPI strip: total deals, total value, tier counts (equal to row counts in the
   tier tables).
2. Tier tables: every deal in each tier, none truncated, names linked to the
   CRM record.
3. By-owner rollup.
4. Loss-intel section (delegated to the win-loss mode, never re-implemented).
5. Footer naming the source, the window, the scoring model, and the calibration
   flag or "nominal".

Output is ready to forward as-is.