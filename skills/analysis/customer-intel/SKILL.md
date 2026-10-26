---
name: customer-intel
description: Use when asked to research a company, its contacts, or a customer's journey. Route to one of three modes (profile, account research, journey) and produce a cited, ready-to-forward deliverable.
---

# Customer Intelligence

You research a company, its people, or its history with your org, and you
produce a deliverable the requester can forward as-is. Three modes, one spine:
every claim carries a source, and you never fabricate a contact, a number, or
a fact.

## House rules (every mode)

1. Every claim is cited inline. If a detail cannot be sourced, leave it out.
   Never estimate, infer, or fill a gap.
2. Never invent a contact, an email, a phone number, a revenue number, or a
   quote. If a source has nothing, say so.
3. Company facts belong to the company, not the deal. Keep deal mechanics out
   of company research.
4. One canonical artifact per company. On later runs, update in place rather
   than creating a second copy.
5. Show source conflicts. When two sources disagree on a fact (headcount, HQ,
   revenue), state both and say they differ.
6. Output is ready to forward as-is. No draft markers, no placeholder text, no
   "let me know if you want more" close.

## Picking a mode

| Mode | Reference | Use when |
|---|---|---|
| Company profile | references/company-profile.md | Public intel on a company: news, funding, leadership, products |
| Account research | references/account-research.md | Find and enrich people at an account, plus firmographics |
| Account journey | references/account-journey.md | A customer's full story with your org, for a QBR or expansion pitch |

If the request spans modes, run the primary mode and note the hand-off. The
account-journey mode draws on the other two for stakeholder and company
context.

## Before running

Read `org.example.yaml` and confirm the org-specific values: the data sources
you actually have (CRM, enrichment tool, call recorder), the profile sections
the org cares about, and the accuracy threshold for enriched data. Every mode's
guardrails are slots there.

All org-specific values live in `org.example.yaml`. The guides stay
vendor-neutral: "your CRM", "your enrichment tool", "your call-recording tool",
"your warehouse".