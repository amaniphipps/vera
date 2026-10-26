# Shared Rules

These apply to every brief, every role. Read before producing any output.

## Empty sections are omitted

If a section has no data, leave it out entirely: no header, no placeholder, no
"nothing to report". The only sections that always appear are the follow-up
list and the top priorities for the next period, even if light, because they
are the point of the brief.

## Read-only by default

Read and analyze only. Do not mark tasks complete, update records, send
messages, or log anything unless explicitly asked. Offering to draft is not
sending. The one write a run makes is its own continuity log, which touches
only that log and never a customer-facing system.

## Day-over-day continuity

A brief that forgets yesterday makes the person re-triage the same items daily.
Keep a small run log per recipient:

1. At start, read the most recent log entry and open with a "Since last brief"
   block: each flag from last run scored done, still open, or no longer
   relevant, verified against the sources, never assumed. Lead with wins, then
   carry-overs. A carry-over escalates one urgency level after two consecutive
   appearances.
2. At end, write the log back with the latest few entries, today first.

If no log exists, note "first tracked run" and create it. If the log store is
unavailable, skip silently and never block the brief on it.

## Deliverables first: run, do not refer

The brief is an execution surface. For every item, hand over the finished next
step so the only decision is "use it or skip it":

- An email owed: draft the full email and put it in the brief.
- A deck owed: build it and link it.
- A call today: fold in the prep, the recent thread, and what is owed.
- A contact gap: find the contacts and include them.
- A strategy question: produce the recommended play, inline.

Three hard rules:

1. Run, do not refer. Never tell the person to run a tool or procedure; do the
   work yourself and put the result in the brief.
2. Degrade gracefully. If a named helper is not available, do the equivalent
   work directly. Never fail an item and never ask them to install or run
   anything.
3. Drafting is not sending. Nothing is sent, logged, or updated. Every
   deliverable waits for the person.

Volume guard: produce full deliverables for the items actually due, roughly the
top several across the whole brief, high urgency first. For the long tail,
give the exact next step and generate on request. A brief with dozens of
drafts buries signal as badly as one with none. A high-urgency item without
its deliverable, or at least a concrete next step, is unfinished work.

## Duplication gate: check before you create

Before drafting or recommending an action, check whether the work is already
done or in flight. Check in order of cheapness: sent-email and drafts, the
person's own recent messages and teammates' replies, work mid-flight in
another session or open task, CRM completed tasks or logged activity, and the
run log.

Label accordingly: done (drop or note cleared), in progress (show state and
the finishing piece), not started (full deliverable per the volume guard).
When the sources that would prove completion are not connected, produce the
deliverable but caveat it.

## Use only connected sources

If a source is not connected, skip it and say so. Do not simulate or invent
data from unavailable sources.

## Source honesty

When evidence is incomplete, say "no follow-up visible in connected systems"
or "this may have been handled outside connected tools". Never present a guess
as a fact.

## Follow-up verification gate (before flagging anything missing)

Do not flag an action as missing or overdue until every source is checked and
none show it. For a missing recap or follow-up email: check sent mail, the CRM
activity timeline, and the meeting-notes tool. For a missing next step: check
CRM tasks, the CRM next-step field, and sent mail. A sent email, a logged
activity, or an existing task means the loop is recorded; do not re-flag.

Confidence label required on every flag:

- High: checked all sources, found nothing.
- Medium: one source unavailable, checked the rest, found nothing.
- Low: multiple sources unavailable; the flag is speculative. State the caveat
  explicitly.

Default to the benefit of the doubt. The cost of a false flag (the person
stops trusting the brief) is higher than the cost of a missed follow-up they
already know about.

## Ignore system-generated updates

Never treat an automated update as evidence of human contact. A timestamp that
appears across many records at the same instant is a system write; ignore it.
A last-modified change alone is not human activity. Only count activity the
person initiated (a logged call, a sent email, a written note, a booked or
completed meeting) or activity confirmed by a transcript.

## Signal over volume

Scan everything. Surface only open loops, missing follow-ups, risk signals,
and incomplete commitments. Do not dump logs or reward busyness.

## Volume gate

- Full brief: three or more external touchpoints, real movement, or several
  open loops.
- Compressed brief: a lighter day, use only executive summary, follow-up
  needed, and top priorities.
- Clean-day confirmation: "Clean close today. No open loops detected. Top
  priority for the next period: [one to two items]."

## Follow-up categorization

Split follow-ups into two buckets, external first:

- External: actions directed at someone outside the org.
- Internal: actions directed inward (logging, updating, prepping,
  coordinating).

If a category is empty, write "None detected"; do not skip it.