---
name: closed-won-replication-play
description: Use when a deal closes won and you want to turn the win into pipeline now — extract the win profile, find lookalikes, and draft anonymized outreach the deal owner reviews before anything sends.
---

# Closed-Won Replication Play

Every closed-won deal is a targeting signal. The moment a deal closes, you use the winning company's profile to find a small set of lookalike companies and draft outreach while the story is fresh — and a human reviews and approves before anything sends. Nothing in this play ships automatically; the human review is the core safety.

## Input

A deal record that just moved to Closed Won, with its associated company and contact.

## Step 1 — Extract the win profile

From the deal and its company, extract: industry/vertical, company size (headcount range), geography, tech stack (CRM, marketing tools, data tools if available), go-to-market model, the use case or pain point that drove the purchase (check deal notes and contact activity), and the **deal owner** (name + email — you'll need them for the drafts). If a field is missing or unclear, make a reasonable inference and move on — don't block on incomplete data.

## Step 2 — Build the lookalike search profile

Construct a specific search profile — "B2B SaaS, 50–200 employees, US-based, uses a mid-market CRM, scaling a GTM team." Generic is weak; be specific. Run a company search for companies that: match the industry and size, sit in the same geography or equivalent market, share a similar GTM model or stack when inferable, and are NOT already in the CRM (not a customer, not active pipeline, not a contact record's company).

Find **exactly** the configured count (default 5). If you can't hit it, broaden one criterion at a time — geography first, then size range. If you still can't, proceed with however many you found and flag the count in the review task.

## Step 3 — Research each lookalike

For each company: (1) confirm ICP fit — does it actually look like the kind of company you sell to? (2) identify the right contact — same persona as the champion in the won deal (if the champion was a VP of Sales, find that role here); (3) enrich the contact for LinkedIn URL and email; (4) note one specific, relevant detail about the company or contact for personalization.

## Step 4 — Draft outreach

One message per company. Rules:
- **Sender:** the deal owner, in their name and voice.
- **Channel:** LinkedIn preferred; fall back to email.
- **Win reference: ALWAYS anonymized.** Never name the customer — reference by industry/profile only: "We just helped a B2B SaaS company scaling their outbound motion do X."
- **Tone:** casual, direct, peer-to-peer, not a vendor pitch. Reference something specific about their company or role to show genuine relevance.
- **CTA:** soft — open a conversation, not close a deal.
- **Length:** 3–5 sentences max for LinkedIn; email can be slightly longer but still tight.

Never mention that you found them because of another customer win — the win informs the angle; don't expose the mechanism.

## Step 5 — CRM updates

For each new lookalike company and contact: if the company already exists in the CRM, skip creating it (but still draft outreach if there's no active deal). Net-new companies get created with source "Closed-Won Replication" and a note referencing the triggering deal. Create/associate the contact linked to the company. Tag each company with `closed-won-replication` and `lookalike-[winning-company-domain]`.

## Step 6 — Create the review task

A single batch review item for the deal owner: title `Closed-Won Lookalike Outreach — [Winning Company Name]`, with a 2–3 bullet win-profile summary, a table (company | contact name + title | LinkedIn/email | matching attributes | outreach draft), any skipped/replaced companies, and a flag if fewer than the target count were found. Notify the deal owner with the batch of drafts ready to review.

## Exit conditions

- Company already in CRM as customer or active deal → skip, find a replacement.
- Fewer than 3 lookalikes found after broadening → create the task anyway, flag the low count, suggest the rep identify additional targets manually.
- Contact opted out or suppressed → skip that contact, find another at the same company.
- Deal has no associated company → log a note on the deal and skip the play.

## What good looks like

One review task the rep can approve in five minutes: the full count of true lookalikes — companies that resemble the win across industry, size, motion, and stack, not just the same vertical — each net-new to the CRM, each with the right-persona contact enriched and one genuinely specific personalization detail, and drafts that read like the rep wrote them: anonymized win reference, soft CTA, no hint of the mechanism.

Mediocre looks like: generic same-industry logos, contacts at the wrong seniority, drafts that name the customer or read like a vendor pitch, a padded list instead of a flagged short one, or one task per company instead of a single batch.

## Output

A single batch review task for the deal owner with the win profile, the lookalike table, sources noted in the CRM, and anonymized outreach drafts — nothing queued to send. Three delivery rules: the review task and any draft-export are self-contained forwardable items with no platform-locked container; every count (lookalikes found vs target, skips, replacements) goes through the analysis-validator before it ships — counts recomputed against the searched set; plain operator English, short sentences, no hype.
