# Forecasting

Build a real forecast, not a rep-reported number with a bow on it.

## Orient first

1. Quarter window: compute start and end from the org fiscal calendar
   (`org.example.yaml` -> fiscal). Never hardcode a quarter.
2. Run number: find the prior forecast for this quarter. Run 1 has no prior;
   Run N+1 compares to Run N.
3. Today: for percent-of-period elapsed and business-days-remaining.

## The three-layer forecast (the core method)

Every run produces exactly three numbers. The difference between them is the
signal.

```
Submitted       = what reps and managers explicitly flagged
Weighted        = closed-won + commit_weight x COMMIT + best_case_weight x BEST_CASE
Conv-Adjusted   = Weighted, with each deal's weight moved by actual evidence
```

Weights (`commit_weight`, `best_case_weight`) are slots in `org.example.yaml`.

### Layer 1: Submitted

Closed-won for the period, plus open deals the rep explicitly flagged as in
their number. This is what was submitted. Count each deal once.

### Layer 2: Weighted

The simplest forecast and the baseline every other number is compared against.

```
Weighted = QTD Closed Won + commit_weight x SUM(COMMIT) + best_case_weight x SUM(BEST_CASE)
```

Pipeline and omit categories contribute zero and appear only as upside.

### Layer 3: Conversation-adjusted

Each deal starts at its category weight and moves along a weight band
(0, 0.10, 0.35, 0.65, 0.95, 1.00) based on conversation evidence. The
adjustment is asymmetric by design:

- Down moves need one signal. A terminal-negative phrase zeroes the deal. A
  soft-negative phrase, or a late-stage deal that has gone dark for too long
  without being in paperwork, steps it down one band.
- Up moves need a full case: at least two distinct close-mechanics signals, the
  most recent contact recent enough, close date in the quarter, and no negative
  signals anywhere. Soft positives ("interested", "moving forward") never move
  a deal up.
- If the call source is unavailable, show Weighted as Conv-Adjusted and label it.

Expected shape: Conv-Adjusted lands at or below Weighted most runs. A number
above Weighted means strong close mechanics were found and must be defensible
deal by deal.

## Signal definitions (reuse verbatim across modes)

- Terminal-negative phrases: going with another vendor, decided not to move
  forward, no longer interested, lost, cancelled, not a fit.
- Soft-negative phrases: budget cut, project on hold, pausing, pushed to next
  period, need to revisit, waiting on leadership.
- Close-mechanics signals (count distinct categories, not phrases):
  1. Paper out (agreement, order form, or contract sent).
  2. Legal or procurement engaged (in review, security passed).
  3. Budget with a date (approved, purchase order raised).
  4. Verbal commitment.
  5. Implementation scheduled (kickoff, onboarding, launch date).
- Paperwork phase: next-step text contains agreement sent, legal review,
  contract, procurement, or signing. This suspends the "gone dark" penalty.
- Dark: no recorded call within the window. Treat as dark after your org's
  threshold (say 60 days) unless in paperwork.

## Pipeline coverage math

```
Realistic low     = QTD Closed + COMMIT + 0.60 x BEST_CASE
Realistic high    = QTD Closed + COMMIT + 0.70 x BEST_CASE
Total addressable = QTD Closed + COMMIT + BEST_CASE + late-stage upside
Gap to target     = target - total addressable
```

Read the target live from the org's target source (`org.example.yaml` ->
forecast.target_source). Never carry a target forward from a prior run.

## Slippage signals (flag on every run)

A deal is slipping when any of: stalled flag with stale activity, blank or
hold-language next step, single contact at a late stage, stage regression, dark
with no paperwork, close date pushed out of the quarter. Tag each slipping
deal with the specific signal, not a generic "at risk".

## Sources

CRM (deals, stages, forecast category), your call-recording tool (transcripts),
your meeting-notes tool and messaging search (what leadership said this week).

## Output shape

1. Three forecast numbers with deal counts.
2. Breakdown table: one row per commit/best-case deal with base weight,
   adjusted weight, and reason when the weight moved.
3. By-rep rollup.
4. Slipping deals with required action.
5. Coverage: target, addressable, realistic range, gap.
6. If Run 2+, a delta ribbon vs the prior run.

Include an inline snapshot (closed won, commit pool, best case pool, range,
top risk) for a quick read. Output is ready to forward as-is.