# Account Research

Find the right people at the right accounts, with verified contact details and
a clear recommendation on who to prioritize and why.

## Hard accuracy rules

- Only surface a contact at or above the org's include threshold (default 90).
  Label it verified.
- Between the include threshold and the "never" cutoff (default 70 to 89),
  include only if fewer than two contacts clear the top threshold, and label
  the confidence.
- Below the never-include cutoff, the record does not exist. Do not list it.
- If the source does not return a per-field score, treat "verified" status as
  top-threshold and "unverified" or "informational" as below cutoff.

## Always return at least two contacts

Even when the request names one person, return that person plus at least one
related stakeholder. If only one contact clears the threshold, expand the
search to a second before returning, and state that you did. If genuinely no
second exists, return the one with the confidence caveat and explain why
coverage is thin.

## Mode detection

| Mode | Trigger | Primary output |
|---|---|---|
| Deal enrichment | Active deal, need more contacts | New contacts + outreach order |
| Net-new research | Company with no deal yet | Company brief + contact list + intent |
| Contact lookup | Specific person | Verified details + at least one related contact |
| Coverage audit | Fewer than two contacts on a deal | Gap list + contacts to add |
| Firmographic lookup | Data points about a company | Company brief + relevant contacts |

If ambiguous, pick the most useful interpretation and note the assumption.

## Check the CRM first

Always check what is already known before enriching. If the company or contact
exists, build on it, never duplicate. Count the contacts already associated.
Flag a coverage gap prominently when an open deal has fewer than two contacts,
because single-threaded deals stall most.

## Enrich

Pull these fields per contact: full name, title, seniority, department, phone,
email, social/profile URL, confidence score, and location.

Target three to five contacts per account across at least two distinct roles,
prioritized by the buyer-role tiers in `org.example.yaml`. Seniority within a
tier takes precedence (C-level, then VP, then director). Do not pre-load the
blocker/approver tier (finance, IT, legal) unless the deal is late-stage or
the user asks.

For company intelligence, pull: employee count, HQ, industry, revenue range,
tech stack (especially systems you integrate with), recent funding or M&A, and
intent signals where available.

## Format the output

1. A quick-reference summary table first: name/email, name/phone, name/title,
   and the confidence line.
2. One structured card per contact. Never dump raw source JSON.
3. Priority logic: top-threshold accuracy plus verified email plus a priority
   buyer role equals high; drop priority for manager-level or blocker roles.
4. A threading recommendation: which new contacts to add, the outreach order,
   and stage-specific notes (do not cold-approach finance before a champion is
   locked).
5. For net-new or firmographic asks, close with a one-page company brief:
   industry, size, HQ, revenue, tech stack, intent signals, recent news, and a
   fit assessment.

## Guardrails

- Never invent an email, phone, title, or company fact.
- Never present data for a different company than the one requested.
- Never skip the CRM lookup.
- Offer a delivery option (CSV, sheet, or doc) rather than writing contacts
  into the CRM unprompted. Surface the data and let the rep decide what to add.