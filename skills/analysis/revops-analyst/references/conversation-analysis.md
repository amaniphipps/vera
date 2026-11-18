# Conversation Analysis

Read sales and service conversations for deal truth, and validate that calls
map to the right deals.

## Why conversations are the ground truth

CRM fields record what someone logged. Conversations record what actually
happened. The gap between the two is where deals hide their real state.

## Source priority (always this order)

1. CRM logged activity first: what was captured and actioned.
2. Meeting notes second: what the rep noted in the room, filling CRM gaps.
3. Call transcripts last: the verbatim record, used to surface commitments or
   signals the first two missed.

Never treat the three as interchangeable. A commitment present in a transcript
but absent from CRM and meeting notes is a high-confidence open loop.

## Sentiment and close-mechanics signals

Reuse the signal definitions from the forecasting guide verbatim. The pipeline
report and the forecast must never disagree about the same call. Terminals and
soft-negatives pull a deal down; close-mechanics (paper out, legal or
procurement engaged, budget with a date, verbal commit, implementation
scheduled) are what count toward an up move. Soft positives never move a deal
up. When there is no call, that is "no calls", distinct from "a call with no
signal".

## Validating call-to-deal mapping (integrity check)

Run this when asked to verify data integrity between the call-recording tool
and the CRM:

1. Orphan calls: calls present in the call system that map to no open deal.
   Report the count and a sample. These inflate activity and hide gaps.
2. Duplicate conversation keys: the same call key appearing more than once.
   Report the count; duplicates corrupt coverage numbers.
3. Coverage: what share of late-stage deals actually have a recorded call.
   Never assume 100%. Compute it, and state the stage definition used.
4. Join on the deal identifier, never on the owner identifier. Owner IDs in
   the call system and owner IDs in the CRM are different name spaces and do
   not join.
5. Use the current stage, not a stage-entered timestamp, to decide whether a
   deal is late-stage.

## Output shape

- Orphan count plus sample references.
- Duplicate-key count.
- Late-stage coverage percentage, with the stage set named.
- Per-deal recency where relevant (last call date), which feeds the "dark"
  flag in forecasting.

Keep the read-only stance: report findings, do not rewrite mappings unless
asked for a specific fix. Output is ready to forward as-is.