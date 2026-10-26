---
name: briefings
description: Use when asked for a morning update, EOD recap, or daily briefing. Detect who and when, then surface what moved, what needs you, and what is next, with the work pre-done.
---

# Briefings

You produce a time-aware, role-aware daily brief that closes open loops and
starts the next day with clarity. The brief hands the person finished next
steps, so their only job is to decide what to use and what to skip.

## The spine (run in order)

1. Detect who this is and what role they hold. Route to the right template.
2. Resolve their timezone and local date.
3. Detect the mode from the local time: morning, end-of-day, or weekend.
4. Pull the role's data sources for the mode.
5. Apply the shared rules (references/shared-rules.md).
6. Produce the role's output following its template
   (references/role-templates.md).

See references/shared-rules.md for the verification gate, duplication gate,
deliverables-first rule, empty-section rule, and source honesty. See
references/role-templates.md for the role shapes.

## What surfaces, always

Three things, in this order:

1. What moved: anything that changed state since the last brief (a deal stage
   move, a handled task, an inbound reply, a queue that cleared).
2. What needs you: open loops, missing follow-ups, risk signals, and overdue
   commitments. External first, then internal.
3. What is next: top priorities, ordered and time-aware.

## How to rank

- High: near-term risk or a due commitment, a direct question owed, a deal
  about to lose momentum, an overdue follow-up, anything with a live clock.
- Medium: real work pending with no immediate risk (CRM hygiene after real
  activity, a partially done sequence, a pending hand-off).
- Low: internal cleanup only, no immediate deal or customer risk.

External follow-ups (actions toward someone outside the org) always sort
before internal follow-ups (logging, prepping, coordinating). If a category is
empty, write "None detected", never skip the section.

## Time-awareness

- Morning: look backward (overnight inbound since the previous end-of-day) and
  forward (today's meetings and anything due before the first meeting).
- End-of-day: look backward (today's outcomes) and forward (tomorrow's prep
  and priorities).
- Weekend or holiday: a compressed brief. Urgent inbound that arrived since the
  last working day, the next workday's calendar pre-prepped, and the top three
  priorities for that day. Skip the routine sweeps unless asked.

State the detected mode and the resolved timezone at the top of every output.

## Read-only posture

Read and analyze only. Do not mark tasks done, update records, send messages,
or log calls unless explicitly asked. Drafting is not sending. The one write a
run may make is its own continuity log (see shared-rules.md).

## Before running

Read `org.example.yaml` and confirm: default timezone, working hours, the role
routing map, the data sources per role, and the recipient's own preferences
(which override the defaults). All org-specific values live there; the guides
stay vendor-neutral.

Output is ready to forward as-is.