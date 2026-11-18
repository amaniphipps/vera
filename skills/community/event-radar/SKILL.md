---
name: event-radar
description: Use when attendee data lands after a webinar, conference, dinner, or booth — qualify it against the ICP and draft contextual follow-up inside the 48–72 hour freshness window.
---

# Event Radar

You turn event attendance into pipeline. When prospects attend a webinar, conference, dinner, booth, or a monitored industry event, you qualify them and draft follow-up that references the specific event. The trigger is most often an attendee list from an event platform (or a hard-uploaded CSV), a scheduled scrape of a public attendee list, or attendance already stored in the CRM. The 48–72 hour window after an event is the highest-converting time to reach out — act inside it.

## Step 1 — Classify the event type

The play differs sharply by event class:

| Event class | Attendee signal | Play |
|---|---|---|
| Your owned event (webinar, conference, dinner) | High — they chose you | Follow up on the topic they came for |
| Industry conference where you exhibited | Medium-high — you met them | Reference the booth interaction |
| Conference attended only — no booth interaction | Medium — same industry, same time | Casual outreach citing the event |
| Competitor's event | Low-medium — in the market | Soft displacement angle, no aggression |
| Partner / adjacent vendor's event | Medium — same buyer pool | Joint-buyer angle |

## Step 2 — Pull attendee detail

The payload should include name + email + company + (ideally) session attended or interactions logged. Company-only data is a softer signal. The golden data is *which sessions they watched, which questions they asked, booth visits logged* — that's the personalization.

## Step 3 — Qualify to ICP

Look up each attendee's company and filter out non-ICP. Conferences attract everyone; not everyone is worth chasing. For lists over 30, switch to code: batch-enrich the companies not already in your data layer, filter by ICP firmographics, and print the top 20 by fit score.

## Step 4 — CRM context per attendee

Outcomes, in order:
- Already in an active sequence → flag for the rep, don't re-fire.
- Customer → route to CS as an advocacy/expansion signal.
- Open deal → route to the deal owner; attendance is an acceleration signal.
- Net new → cold play with the event as the anchor.

## Step 5 — Match content to angle

For owned events, the topic of the session they attended IS the angle — don't pivot. For exhibited conferences, the booth interaction (what they asked, what they took, who they spoke to) IS the angle — pull it from CRM notes or the rep log; reps should be capturing this during the event. For attended-only conferences (no booth), the angle is the shared experience: "We were both at [event] last week. The most surprising takeaway for us was [X]. Curious what stuck with you."

## Step 6 — Draft the post-event message

Templates:
- **Webinar:** "Hi [name] — thanks for joining [session title]. The question we got most after was [specific Q]. Curious how you're thinking about it at [company]. Would love to compare notes."
- **Booth visit:** "Hi [name] — good chatting at [event] about [specific topic]. As promised, here's [thing you said you'd send]. Would 20m next week be useful to dig in?"
- **Competitor's event:** "Hi [name] — saw [event] was last week. We weren't there, but the question we hear most from [persona] when [topic] comes up is [your wedge]. Worth a quick chat?"
- **Attended-only:** "[name] — fellow [event] attendee. [One-line insight from the event you'd share]. Curious if [related question for them]?"

## Step 7 — Build the sequence

For unowned ICP-fit, hand off to the sequence builder: 2–3 touches max; event freshness fades quickly. For owned events, create a task for the rep with the attendee record, session detail, and suggested message.

## Step 8 — Bulk vs individual

For large events (100+ ICP-fit attendees), don't reach out one at a time — bulk-personalize via code, writing each sequence action with the personalization hook (session attended, company context) in batches of ≤50.

## Step 9 — Log

Tag the company with event attended + date. If a deal converts, tag the event as the source — over time, the org learns which events convert.

## Rules

- Act within 72 hours of event end; after that the freshness is gone.
- Reference the event specifically — "thanks for coming" is the laziest possible follow-up.
- Qualify to ICP before mass reach-out; events attract a huge non-ICP tail.
- Never fire competitor-event follow-ups with aggressive displacement — soft angle only.
- Never pretend you spoke to someone at the booth if you didn't. Rep notes matter.
- Anonymous attendance (no email) → don't fire individual outreach; tag the account and watch for return signals.

## Tighten over time

After 3–5 events, read reply-rate data filtered to this play's executions and identify which event classes (owned vs exhibited vs attended-only vs competitor) yielded best. Recommend dropping classes that didn't yield, raising the ICP-fit floor on attendee lists, or investing in the sessions that drove the highest-converting follow-ups.

## Output

A qualified, ICP-filtered attendee list (CSV) plus drafted post-event messages (or queued sequence actions) per attendee, each anchored to the specific session or interaction. Three delivery rules: the list and message drafts are self-contained forwardable files with no platform-locked container; every count, ICP match, and conversion stat goes through the analysis-validator before it ships — the top-20-by-fit ranking and event-yield comparisons recomputed; plain operator English, short sentences, no hype.
