# Role Templates

Pick the template for the detected role and adapt it by mode (morning or
end-of-day). Every template follows the same shape: data sources, what to scan
for, output format, and a style note. Role routing is in `org.example.yaml`.

## Detection

Resolve the requester against the role-routing map. In doubt, default to the
general template; a general brief is never wrong, while a misrouted sales brief
to a non-sales user is confusing and useless. For adjacent roles (a closer vs
a development rep), disambiguate by title and, if still ambiguous, ask once.

## AE template

A sales closing role. The day is organized around a few working views or
queues (from `org.example.yaml`), swept every run and turned into an execution
plan, not a list.

Data sources: CRM (primary, scoped to the owner), calendar, email (all
folders, including sent), the call-recording tool, and the meeting-notes tool.

What to scan for, by mode:

- Morning: overnight inbound, deals closing soon with no meeting, deals stuck
  in the same stage, single-threaded deals, overdue tasks, today's meetings
  with context.
- End-of-day: what moved today (show before then after), tasks done and
  overdue, revived deals (a closed-lost or dormant deal with new inbound
  today), missing follow-ups from today's meetings.

Do not conflate two things: a deal that moved stages ("moved DS2 to DS3")
versus activity on a deal without a stage change ("activity: note added").
Keep them separate in the output.

Suggest an opener per meeting, with the prep done: pull the recent thread, the
CRM notes, and the call history, and state what the call is about and what is
owed.

Output (morning): overnight inbound, today's meetings, the working-views
sweep, urgent items due before noon, stale-deal flags, prospect news if any,
top priorities. Output (end-of-day): executive summary, today's progress, the
views sweep, follow-up needed, deals at risk, top priorities, internal action
items.

## ADR template

A development or outbound role with queue-based work and a speed-to-lead
reputation. Sweep the queues every run (from `org.example.yaml`), and show the
clock: age of the lead, time since trial end, hours since inbound.

Data sources: CRM (tasks and queues), calendar, email, messaging, meeting notes.

What to scan for: inbound awaiting first response, leads past the response
window, each queue's items due a touch with a per-queue play (a win-back for
ended trials, re-engagement for quiet deals, new-stakeholder push for
single-threaded), and hand-offs owed to the closer.

For every queue item, produce a card: the deal, the reason it is in the queue,
the last human touch, the recommended play, the exact next step, and who takes
it (development rep or closer).

Output mirrors the AE shape but queue-first, with a partnership check listing
what is owed to and from the closer.

## CSM template

A customer-success role carrying a book of business. Protect the book, close
open customer loops, and surface at-risk accounts before they become problems.

Data sources: CRM (accounts), customer-health tool (the primary health signal),
support, calendar, email, meeting notes, messaging.

What to scan for: health flags and play-triggered tasks due today or overdue,
renewals in the next 30, 60, and 90 days with no signed renewal or active
conversation, accounts with no touch in too long, no-shows or cancellations
without a reschedule that signal risk, and expansion signals (asked about more
seats, a new team, or a positive outcome).

Output (morning): overnight inbound, the customer-health queue, today's
meetings, renewal alerts this month, accounts due a touch, top priorities.
Output (end-of-day): executive summary, today's activity, follow-up needed,
accounts at risk, renewal pipeline by horizon, expansion opportunities,
internal action items.

Style: relationship-warm, name accounts specifically, distinguish a churn
signal from a merely quiet account, always show the clock on renewals, and
treat an expansion signal as "worth a conversation", never a guaranteed upsell.

## General template

Every role that is not sales or customer success: engineering, product,
marketing, finance, HR, legal, operations, and unmatched roles. This is a
communication-and-task hygiene brief, not a pipeline or account brief.

Data sources: email (all folders), messaging (mentions and direct messages),
the task tool, calendar, and meeting notes.

What to scan for: unanswered external email, mentions with no reply, tickets
in progress or overdue or blocking someone, meeting action items with no
visible follow-through, unread document comments or pending shares that imply
follow-up, and unfinished work from a prior session.

Output (morning): overnight inbound, today's meetings, items due before noon,
top priorities. Output (end-of-day): executive summary, today's activity,
follow-up needed, the task watch list, tomorrow's prep, top priorities.

Style: operational and clean. Treat email, messaging, and tasks equally. Flag
communication debt (things people are waiting on) highest. A genuinely light
day gets a short, compressed brief; do not invent urgency.

## Adding a role

To add a new role: add a routing row in `org.example.yaml`, then write its
section following this shape (data sources, what to scan for, output format by
mode, style note). Keep every role's brief vendor-neutral and scoped to the
requesting person.