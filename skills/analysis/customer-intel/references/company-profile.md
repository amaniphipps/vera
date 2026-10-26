# Company Profile

Build a cited company profile. The research is the product; the one-note rule
is the contract.

## Non-negotiables

1. One profile per company, forever. Before writing, look for the existing
   profile. If one exists, update it in place. Only create when none exists.
   This holds across users and deals.
2. Every claim carries an inline link. Anchor text is the source title. No
   uncited facts.
3. Company only. No deal amount, stage, owner, contacts, or rep instructions.
4. Show source conflicts. When sources disagree on a fact, state both.
5. Recency. Recent-news sections cover the org-configured window (default 6
   months). Older events that still shape the company go in the overview with
   their date.
6. No em dashes in the note or the chat output.

## Resolve the company

- Input may be a deal link or ID, a company name, or a domain.
- From a deal: find the associated company. From a name or domain: search by
  domain first, then name.
- Capture the company ID and name, and note every open deal tied to it.
- If multiple companies match a name, ask which one. Do not guess.

## Find the canonical note (dedup check)

The note carries a marker on its first line so it can be found and updated:

```
<profile-marker> company <company_id>
```

Set the marker value in `org.example.yaml`. Search in this order, stopping at
the first hit:

1. The note attached to the company carrying the marker.
2. The note attached to each open deal carrying the marker.
3. Fallback: pull the company's notes and scan bodies for the marker line.

Outcomes: none found, create. One found, update that note. Two or more found
(a merge or a race), update the oldest and report the duplicate IDs so an
admin can archive them. Only a note with the exact marker counts. Rep-written
notes are never touched.

## Research

Run searches in parallel. Scale to the company: a public-signal-rich company
needs many searches; a small private company may only support a few. Search
each section separately, and check the page's year before trusting an event
listing that may still show last year's event.

Sections and where to look:

| Section | Where to look |
|---|---|
| Overview | Company site (About, Leadership), funding-data snippets, the company LinkedIn page, press on layoffs or restructures |
| News and triggers | News search (last window): funding, M&A, leadership changes, hiring, layoffs, launches, partnerships, filings |
| Events and conferences | Event directories, sponsor lists, conference speaker schedules, the company's own newsroom |
| Products and services | Product pages, recent launch press. Note launches, sunsets, pivots |
| Social activity | The company's social posts, plus employee and investor posts |
| Employee sentiment | Review-site ratings and recurring themes |

## Write the profile

Use `org.example.yaml` -> profile.sections for the section order. A standard set:

1. Executive summary: a few bullets of highest-signal context (capital events,
   ownership changes, workforce growth or contraction, sentiment).
2. Overview and background: founded, HQ, headcount, funding, leadership,
   one-line description.
3. Recent news and trigger events: dated bullets, newest first, one to two
   sentences each. Omit the section if empty.
4. Events and conferences: split upcoming and recent, with dates and role.
5. Products and services: one bullet per offering, what it does and for whom.
6. Social activity: company-page themes with two or three linked posts, then
   employee and customer voice.

Tone: concise, professional, sales-assistive. No editorializing, no
instructions to the rep, no filler openers.

## Create vs update

- Create: write the note with the marker as the first line and start a
  revision log with one entry.
- Update: read the existing note, keep its revision-log entries, rebuild every
  section from fresh research, carry forward any still-valid item whose source
  resolves, drop anything superseded, and append one revision-log entry. Keep
  the most recent ~15 entries. Keep the original timestamp.

## Report back

Mode (created or updated), the note link, deals associated, and the one to
three most important changes versus the prior version. Note any section that
came out thin because a source failed.