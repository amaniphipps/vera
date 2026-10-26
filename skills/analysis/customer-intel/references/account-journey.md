# Account Journey

Tell a customer's full story with your org, for a QBR, an expansion pitch, or
a renewal defense. One account at a time.

## Collect inputs

Ask for: the account name (required), the account identifier if known, the
audience (customer-facing or internal), the modules wanted, the time scope
(default full history), and any special focus (international expansion,
renewal defense, QBR). If only the name is given, resolve the identifier from
the billing or CRM system.

Audience changes the content: the customer-facing version omits risk flags,
competitive mentions, and internal friction. The internal version includes
them. Keep the two versions separate.

## Data streams (run in parallel where possible)

- Identity and brand: resolve the account and its logo.
- Billing arc: subscription value and billing history over time.
- Usage growth: active users over time.
- Core activity: the account's main activity volume over time.
- Reward or value data, if your product has a redemption or comparable lens.
- Integrations and feature adoption, if tracked.
- Conversations: call transcripts, meeting notes, messaging.
- Support history.
- Firmographics and public intel.

Module-specific data (department, role, location, reward) runs only when that
module is requested. Every quantitative section reads its denominator from a
consistent source; the most common error is dividing historical activity by
current headcount. Use the headcount that existed in the period being measured.

## Benchmarking

When comparing an account to peers, build the cohort dynamically from similar
size (a band around the target's user count, widened if too few peers).
Anonymize every peer account. The smaller the target, the more peers exist
and the more confident the comparison. State the cohort size and the band in
every finding, and frame the claim to the sample: a few peers gets "observed
across N similar accounts", not "data confirms".

## Signal tiers for claims

Only make claims the sample size supports. A rough guide to state inline:

- Too few records: describe counts, make no claims.
- Small cohort: count-and-direction language.
- Large cohort: standard analytical language.

## Validation before delivery

Before building the final document, spot-check at least one headline number per
module by re-running the underlying query independently. If the spot-check
differs by more than a few percent, surface it as a mismatch and fix it. Also
verify the universe anchors (user count, activity volume, conversation count)
tie to the data sources.

## Structure

1. Cover: customer and org logos, a partnership title, and the date range.
2. At a glance: stat cards (years, users, countries, activity volume, value)
   and a one-paragraph executive summary.
3. How you grew together: a growth timeline with one narrative sentence per
   period, aligned to the timeline columns in `org.example.yaml`.
4. The year-by-year story: the bulk. Per period, cover what was happening at
   the account, your program's state, what conversations were about, and the
   notable moments. Lead with the most important development, not chronology.
   Use specific numbers and name real people where relevant. Include optional
   callout boxes for the impactful data points.
5. Program health and engagement: key metrics trended over time with a trend
   column, plus a country or segment view if relevant.
6. The opportunity: adapt to context. Expansion math (current, moderate, full
   scenarios) for expansion; engagement-depth and switching-cost evidence for
   renewal defense; health metrics and next-quarter recommendations for a QBR.
7. Why it matters: four to seven themes, each a punchy title plus a short
   evidence-backed paragraph.

## Writing rules

- Use specific numbers, not adjectives. "1,438 acts from 156 givers", not
  "strong adoption".
- Lead with implications ("one region over-indexes at 1.1x"), not raw counts.
- Never pad an empty section. If a period has no data, say so in one line.
- Quotes and metrics must come from the real records, never invented.

Output is ready to forward as-is. Deliver the document and a one-paragraph
summary of the most important finding.