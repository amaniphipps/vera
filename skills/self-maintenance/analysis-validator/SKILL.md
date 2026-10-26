---
name: analysis-validator
description: Use before publishing ANY output with numbers, claims, or data - reports, briefings, analyses, Slack summaries with metrics. Runs the two-gate QA (data correctness + output quality) plus a significance awareness check. Nothing with a number ships without passing.
---

# Analysis Validator

The final QA pass. Runs after every quantitative output and before anything
is published, shared, or delivered. Its job is to catch what the analysis
itself cannot see: arithmetic errors, claims that outrun the data, formatting
failures, and samples too thin to support the language used.

**The model: two hard gates + one awareness check.**

```
GATE 1 - DATA CORRECTNESS    Hard gate. Fail = RERUN or HOLD. Do not publish.
GATE 2 - OUTPUT QUALITY      Hard gate. Fail = FIX. Do not publish.
AWARENESS - SIGNIFICANCE     Never a gate. Tells the reader what weight to
                             give the findings. Always in the trail.
```

**Decisions:** both gates pass -> PASS, stamp, publish. Gate 1 fails but is
auto-correctable (re-query, filter fix, term swap) -> RERUN silently, note
what changed, re-validate. Gate 1 fails and cannot be corrected -> HOLD,
surface specifics, do not publish. One rerun attempt; if it still fails,
surface to the user.

**The score is internal.** Readers see a `Validated by Vera` stamp and a
collapsible validation trail. The report is the product; the trail is the
receipt.

## When it runs

- **Full mode:** any completed deliverable containing counts, rates,
  percentages, or trends. All checks, both gates, the trail.
- **Lightweight mode:** follow-ups, single-metric answers, quick checks after
  one full run in the session. Silent: arithmetic spot-check (C1), claim
  language scan (C6), terminology scan (C8). Failures surface immediately.
- **Does not run on:** pure prose with no data, single-row lookups, or when
  the user says "skip validation."
- **No exceptions for quick work.** A fast answer with a wrong number is
  still a wrong number delivered with confidence.

## Gate 1 - Data Correctness (12 checks)

**C1 - Arithmetic.** Recompute every percentage, rate, and ratio. Confirm the
denominator is stated and consistent. Flag suspiciously round numbers
(exactly 50%, 33%, 25%) and verify them. Flag non-additive metrics (unique
users) summed across intervals. Flag rates computed on a subset but stated
as the universe.

**C2 - Canonical filter compliance.** Every query matches the org's canonical
patterns (org.yaml: `canonical_filters`). Soft-delete flags, sample-data
flags, status enums, scoping rules. Known trap shapes: `IS NULL` on a text
soft-delete flag (silently returns nothing useful), boolean active-flags
that are NULL for most rows (silently drops the population), case-sensitive
status enums. Any deviation = RERUN with the corrected pattern.

**C3 - Temporal currency.** Any rolling-window metric is re-queried at
validation time. Drift over 5% = update before publishing.

**C4 - Source-of-record integrity.** Every data class pulled from its
approved source (org.yaml: `sources_of_record`). Retired or stale sources =
HOLD. Join paths match the documented canonical path.

**C5 - Chart provenance.** Every chart series traces to a per-interval query
run in this session. No approximated, interpolated, or carried-forward
values. Untraceable series = RERUN.

**C6 - Claim language.** Claims must match the tier of data behind them:

| Claim | Requires | Else |
|---|---|---|
| "confirms" | 80%+ coverage of scoped universe | soften to directional |
| "increasingly" / trend | 2+ comparable periods | add comparison or remove |
| "should" (prescriptive) | 50%+ coverage + causal basis | remove or qualify |
| causal ("because X, Y") | causal evidence | HOLD |
| "N% of X" | correct arithmetic | pass |

**C7 - Segmentation disclosure.** Mixing distinct populations (e.g.
self-serve vs sales-led, active vs cancelled, org.yaml: `segments`) without
explicit disclosure = failure. A finding about one segment never reads as a
finding about all.

**C8 - Canonical terminology.** Terms match the org glossary (org.yaml:
`terminology` + `knowledge/seed/saas-terms.md`). Non-canonical terms are
corrected before publishing. Undefined metrics ("engagement", "active")
must carry their definition.

**C9 - Currency normalization.** No SUM/AVG on monetary columns without a
currency filter or conversion. Cents-vs-dollars and multi-currency
aggregation are the classic silent inflators.

**C10 - Population sanity.** Counts sit within plausible range for the
entity, calibrated against LIVE universe queries run at session start
(anchors in org.yaml are expectations, never denominators). A count far
above the plausible bound almost always means a missing filter.

**C11 - Reconciliation.** Any movement table (roll-forward, funnel, budget)
must reconcile: opening + gains - losses = closing, within tolerance
(default 1%, org.yaml). Category doctrine (e.g. reactivations fold into
expansion) comes from org.yaml. Over tolerance = HOLD with the reconciliation
printed line by line and the most-likely-cause list.

**C12 - Evidence coverage for claims.** A claim about activity, engagement,
or responsiveness requires the evidence was actually pulled - across
channels, not one. Absence in one system (no logged calls) is not evidence
of absence (emails and meetings may exist). Claim without coverage = RERUN
with the pull, then re-assess.

## Gate 2 - Output Quality (6 checks)

**C13 - Contrast.** 4.5:1 body text, 3:1 large text. Same-family
text-on-background (gray on light gray, amber on white) = failure.

**C14 - Responsiveness.** No fixed width over 480px without an override;
tables scroll or restructure on narrow viewports; no font under 12px; tap
targets 44px.

**C15 - Typography.** Body line-height >= 1.5; prose line length <= 75
characters; no all-caps paragraphs.

**C16 - Completeness.** No `[TBD]`, placeholder text, lorem ipsum, empty
sections, headings with nothing under them, charts with no data.

**C17 - Attribution.** Every output carries its stamp: `Built by Vera` +
date (or the org's configured stamp, org.yaml: `stamp`).

**C18 - ID resolution.** No raw IDs, UUIDs, or system codes as visible
values. Every ID resolves to a human-readable name before publishing.

## Awareness - Statistical significance (never a gate)

Compute coverage per section: sample vs LIVE-queried cohort denominator.

| Coverage | Level | Reader note |
|---|---|---|
| < 25% | INSUFFICIENT | count only, note coverage |
| 25-50% | DIRECTIONAL | early indicator, not a pattern |
| 50-80% | MEANINGFUL | representative |
| 80%+ | HIGH CONFIDENCE | reflects the cohort |

Minimum raw-N floors (org.yaml: `min_n`) override coverage percentages on
tiny counts. Then the **overclaim scan**: in INSUFFICIENT/DIRECTIONAL
sections, flag universal claims ("customers prefer"), superlatives,
"across all", significance language ("clear pattern", "confirms"), and
trend language without comparators. Simple fixes (adding "among the N
analyzed") apply automatically; restructures surface for review but do not
block.

**Pre-flight:** if the whole analysis population is INSUFFICIENT before
work begins, stop and offer options (widen window, broaden filter, or
count-only output) instead of producing a report that cannot support its
own claims.

## The trail (appended to every Full Mode output)

```
VALIDATION TRAIL
Analysis: [title]   Run: [date]   Validator: analysis-validator v1
GATE 1: C1..C12 one line each (checked / n verified / flags)  -> PASS/RERUN/HOLD
GATE 2: C13..C18 one line each                                 -> PASS/FIXED
SIGNIFICANCE: section, sample, denominator, coverage, level; overclaim flags
FINAL: PASS / PASS WITH NOTES / HOLD
```

## Part of learning

This validator is also the gate for what Vera learns. Any quantitative
procedure entering `skills-live/` - and any draft the skill-vetter considers
for promotion - gets its canonical example run through these checks. A new
"canonically correct" way of doing something that fails validation is not
canonical; it goes back as a draft note, not a learned behavior.

When the user corrects a validation finding (a methodology the validator
did not know, a definition applied wrong), that correction is a learning:
patch the org layer (terminology, filters, thresholds), log it, and let the
vetter carry it forward. "Proceed anyway" is not a correction.
