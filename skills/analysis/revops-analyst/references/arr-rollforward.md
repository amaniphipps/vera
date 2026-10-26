# ARR Roll-Forward

Answer questions about recurring revenue movement: why ARR moved, churn,
expansion, contraction, reactivation, and retention (gross and net).

## The identity every roll-forward must satisfy

```
Ending ARR  =  Starting ARR
             + New ARR
             + Expansion ARR
             - Contraction ARR
             - Churn ARR
             + Reactivation ARR
```

Each bucket is defined in `org.example.yaml` under `arr`. Read those
definitions before computing anything. The most common error is a bucket
counted twice, almost always an upgrade that shows up as both new and
expansion, or a renewal that is counted as new on top of the expansion it
already contains.

## Picking the data source

Recurring-value data lives in more than one system, and they disagree. Decide
the source of truth per bucket before pulling:

- Current state (ending ARR, active accounts): your customer-health or billing
  system's current snapshot.
- Point-in-time movements (new, expansion, contraction, churn, reactivation):
  your billing system's event stream or a versioned subscription history.
- Historical opening balances: a versioned subscription table or a daily
  snapshot table, when one exists.

If no point-in-time opening snapshot exists, use the residual method:

```
Opening ARR = Ending ARR - New - Reactivation + Churn - Net Expansion
Net Expansion = Expansion - Contraction
```

This is a workaround. Flag it in the output and, if the org will report this
repeatedly, recommend standing up a daily ARR snapshot table so opening
balances stop being derived.

## Reconciliation checks (run all before reporting)

1. Closing ARR ties to the canonical current snapshot. If it does not, stop and
   find the gap.
2. Sum of buckets equals the total movement: `Ending - Starting`. Any residual
   is leakage and must be named, not absorbed.
3. Each account appears once per bucket type in a period. An account that
   expanded twice shows once with the net expansion.
4. Churn and reactivation are allowed together for one account (it left and
   came back). That is correct, not a double-count.
5. Units are normalized. If one system stores cents and another dollars, pick
   one and convert everything before summing.

## Common traps

- Double-counting upgrades: an upgrade logged as a subscription-change event
  and again as a new invoice. Pick one source per bucket and stay with it.
- Double-counting renewals: a renewal that carries an expansion should count
  only the expansion delta, not the full renewed value.
- Status-case mismatches: "active" vs "Active" vs a numeric code. Normalize.
- Period-boundary leakage: a movement dated outside the window included, or a
  movement at the boundary counted in two periods. Use half-open windows
  (start inclusive, end exclusive).
- Missing the internal/test exclusion: demo and internal accounts inflate
  churn and new. Apply the org exclusion rule to every bucket.
- Surviving-accounts bias: computing churn only over accounts still in the
  current roster misses accounts that left entirely. Use the event stream.

## Retention ratios (report-level)

```
Gross Revenue Retention  = (Beginning ARR - Churn ARR) / Beginning ARR
Net Revenue Retention    = (Beginning ARR - Churn ARR + Net Expansion ARR) / Beginning ARR
Logo Retention           = (Opening logos - Churned logos) / Opening logos
```

State which definition of churn you used. Some orgs split "all churn" from
"considered churn" (excluding fraud and account merges). Record that split in
`org.example.yaml` and be explicit in the output.

## Output shape

1. Period and sources, one line each.
2. The bucket table: New, Expansion, Contraction, Churn, Reactivation, with
   ARR and logo count per bucket.
3. The reconciliation line: Starting, Ending, and that the buckets tie.
4. Retention ratios if asked.
5. Any gaps or workarounds, stated plainly.

Keep it concise. The reader wants the movement and the cause, not the query
log. Output is ready to forward as-is.