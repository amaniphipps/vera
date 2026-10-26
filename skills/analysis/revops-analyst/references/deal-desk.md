# Deal Desk

Answer pricing, discounting, payment-terms, and contract-posture questions so
the org wins or keeps the deal without making a position up.

## Route first

| Request | Handling |
|---|---|
| Contract posture ("can we accept X", "what is our stance on Y") | Answer directly |
| Redline review | Table-driven position + approval |
| Signed-agreement or prior-terms lookup | Agreement search |
| Quote or commercial review | Check against the rate card |
| Vendor form, tax form, insurance cert, NDA | Populate from the business-info page |
| Billing question | Point at the billing reference |

Hand off anything with its own deep procedure (RFP completion, security
questionnaire) to that procedure rather than answering inline.

## Learn the account before answering

Every request that names a company gets a light pre-read:

1. Is this a customer or a prospect? Customers are retention and move first.
2. Deal context: stage, amount, owner, close date.
3. Existing notes on the company and the deal.
4. Conversation history, so the answer does not contradict what a rep or buyer
   already said.
5. Any prior agreement, if the question touches terms or renewal. New
   agreements override old ones.

Keep only what changes the answer. The requester wants the answer, not the
research.

## Approval logic shape

Use a per-request table: what they asked, your standard position, who approves
an exception. The thresholds and owners are slots in `org.example.yaml`
(`deal_desk`). Standard rows:

| Request | Position | Approval |
|---|---|---|
| Discount below floor | Push back or approve up to floor | Commercial owner |
| Payment terms beyond ceiling | Approve up to ceiling, escalate beyond | Finance |
| Redline on a small deal | Decline, standard response | Escalate only if they threaten to walk |
| Anything new | Bring to the deal desk | Varies |

Hard rules:

- Never quote pricing or a discount from memory. Check the rate card.
- Never grant or imply an exception. Name it and route it to the decider.
- Never fabricate a certification, a control, a legal position, or a
  capability. If unsure, say so and escalate.
- Push back only on clauses that are both high-risk and likely. Avoid
  back-and-forth on trivia.

## Margin guardrails

These live in `org.example.yaml` and are the floor the analyst never breaks on
their own:

- Discount floor (percent).
- Payment-term ceiling.
- Minimum deal size below which redlines and heavy work are declined.
- The named approvers for commercial, legal, and security exceptions.

State the guardrail in the answer when it applies, so the requester knows why
you said no or escalate.

## Output

Lead with the answer and the language the requester can use, add the source in
one line, and flag only what genuinely needs a human, with that person or role
named. Shorter is better when it is accurate. Output is ready to forward as-is.