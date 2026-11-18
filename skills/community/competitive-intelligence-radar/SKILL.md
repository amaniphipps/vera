---
name: competitive-intelligence-radar
description: "Use when you want a standing weekly watch on competitors — pricing, SERP rank, positioning, news, sentiment, funding, and hiring — with a source URL on every claim, plus an on-demand strategic war room that debates the findings and converges on ranked moves."
---

# Competitive intelligence radar

You run a standing competitive watch that turns a weekly fan-out over live web data into one cited briefing — plus an on-demand "war room" where four analysts debate the findings and converge on ranked moves. The credibility contract is absolute: every factual claim carries a source URL actually fetched this run, and anything unverifiable is recorded as not-found or blocked, never guessed.

## The three operations

1. **Setup** — one-time onboarding. Live-tests the data source and the publishing target with one real call each (never assumes), collects business context (domain, tracked keywords, competitor list, geo), shows the proposed competitor/briefing schema and creates it only after approval, and checks the war-room prerequisites.
2. **Gather** — the weekly run. Runs autonomously end to end.
3. **Council** — the on-demand war room. Token-heavy; always asks before it runs.

## The weekly gather

One scout worker per competitor, fanned out in parallel (**capped at 8 per run**). Each scout independently gathers a cited JSON dossier: SERP rank for your tracked keywords, pricing and positioning scraped from the competitor's own pages, and fresh news — plus opt-in deep sources (social sentiment, financials, hiring) only when enabled. Scouts never talk to each other; they gather, cite, and report back.

Every dossier field is an object of `value`, `source_url`, `fetched_at`, and `status`. A value that can't be found is `null` with `status: not_found`; a blocked page is `blocked`. Never a guess, never a URL that wasn't fetched this run — model knowledge is not a source.

The orchestrator then diffs against last week, comparing only fields fresh on both sides: pricing and SERP re-fetched every run; news, sentiment, and hiring within 30 days; funding within 90. Changes are classified — **Rising, Falling, Price, News, New** — ranked by materiality, and merged into one briefing where every claim carries its source and fetch date, headed by a "what changed" digest and a three-item focus list.

## The war room

Where the gather uses independent workers that only report back, the council is a real debate between four analyst roles that read the briefing and challenge each other directly:

- **Pricing analyst** — where each rival's price sits relative to yours, who changed packaging, where you're exposed, what concrete pricing move follows (new tier, repackage, price test).
- **Product-gap analyst** — what rivals emphasize and ship, where one is clearly ahead, where a gap nobody covers could be owned; reads hiring as a leading indicator of product direction.
- **Threat-and-sentiment analyst** — ranks the week's rising danger from SERP momentum, funding, news, hiring, and mood; separates one bad review from a pattern.
- **Devil's advocate** — doesn't propose the plan; stresses it. Attacks the weakest link in each read, hunts for anchoring on the first plausible story, flags any move resting on a stale or missing source, and surfaces the move nobody proposed because it was uncomfortable. A move that can't survive the challenge gets cut or downgraded.

The lead then synthesizes a Strategic War Room addendum: a consensus summary, the top recommended moves each with a one-line rationale and its supporting source, and a dissents-and-risks list. Keep the two parallelism primitives distinct: independent workers for the gather, a debating council for the analysis — never swap them.

## Output surfaces, every run

1. A local `outputs/` folder: the briefing markdown, the combined raw dossier JSON, and the war-room addendum.
2. A connected knowledge base: a Competitors database upserted by domain with week-over-week change tracking, and a Briefings page per run.
3. A self-contained HTML dashboard — inline CSS/JS, no dependencies, no network — openable in any browser.

## Rules

- **No fabrication:** every factual claim carries a real source URL fetched this run. A single invented number destroys the product promise.
- **Freshness:** stale data is labeled "as of \<date\>", never presented as current.
- **Cost control:** batch calls over per-URL calls; competitors capped at 8; lean scout depth by default; the expensive scraping path only as a fallback for blocked pages.
- **Checkpoints:** database creation and the token-heavy council always ask for an explicit yes first; the gather runs autonomously.

A good run reads: every claim links to a page actually fetched that run; anything unverifiable says not-found or blocked; the focus list is three ranked items, not a wall of data; each council move survives a devil's-advocate challenge with a citation attached; the owner reads it in five minutes and knows exactly where to look this week.

## Output

A weekly cited briefing (a "what changed" digest + a three-item focus list), a combined raw-dossier JSON, and an optional war-room addendum — published to a local folder, a connected knowledge base, and a self-contained HTML dashboard, with a source URL and fetch date on every claim.

Delivery rules: (1) every output is a self-contained file ready to forward as-is — the briefing, dossier, and dashboard need no platform to open; (2) every number, rate, or claim passes through the analysis-validator before shipping — arithmetic recomputed and claims matched to the fetched source URL, never to model memory; (3) plain operator English, short sentences, no hype.
