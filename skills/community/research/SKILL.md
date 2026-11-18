---
name: research
description: Use when asked to research a company, person, buying committee, GTM motion, news, domain, financials, tech stack, or competitor mentions — pick the right facet, match depth to the ask, and return a cited, confidence-flagged answer.
---

# Research

You research a target on demand — a company, a person, a buying committee, a signal, a domain, a stack, financial context, or a competitor mention — and you produce a focused answer with sources and confidence notes. It is target-driven and needs no org config to run: you route to the right facet, match depth to the ask, and stop when the surface area is covered. Over-researching when a sentence would do is the most common failure mode.

## Step 1 — Route to the facet

| Ask shape | Facet |
|---|---|
| Generic company / "what does X do" | Company |
| Named person | Person |
| Mapping the people inside one account / buying committee | AccountTeam |
| How the target sells / GTM / pricing posture | GTMmotion |
| Recent news / signals / last-30-days | News |
| Domain / traffic / SEO / digital footprint | Domain |
| Financial / funding / revenue / runway / ownership | Financial |
| Tech stack only | TechStack |
| Where the target mentions competitors / displacement signals | CompetitorMentions |

Ambiguous asks default to Company. A chain of facts ("company plus the buying committee") may load two facets — but always pick a primary. Cheap-before-expensive applies across every facet: check what's already known in your data layer and the CRM first, reach for free preview signals before paid enrichment, and enrich only when the cheap signals left a real gap.

## Step 2 — Match depth to the ask

- "/research acme" / "what does acme do" → brief (3–5 lines, the essentials).
- "deep brief" / "full dossier" / pre-meeting prep with a VP+ → run the facet end-to-end.
- "quick — is acme an ICP fit" → micro-answer, one paragraph.

Default to brief. Scale up only when the user signals depth or the situation (board prep, founder intro, executive outreach) demands it. Reading the room beats running every facet.

## Facet playbooks

**Company** — the default. Build a tight read: who they are, what they sell, who they sell to, what's happening now. What-they-do = one sentence synthesized from the homepage H1, subhead, first product section, and top CTA (two fetches max). Firmographic frame = industry, employee band, HQ, founded, funding stage. Recent signals = the strongest 1–3 from the last 30 days, dated and source-cited, or "no notable events." End with a one-sentence positioning angle for outreach and a confidence line. Use a prior brief <30 days old as the base and refresh only what's stale.

**Person** — person-level dossier for high-stakes outreach only, never volume. Enrich the structured profile (role, tenure, history, location), read their recent activity (active or dormant, what they post about, what gets traction), scan 1–3 high-signal web mentions (talks, press, podcasts, personal site), and flag work-history patterns — long stints (3+ years) suggest a builder, short stints a fixer; same vertical for 10+ years signals deep domain identity. Compose: role, career arc, recent activity, what they care about, warm paths in, and a one-sentence outreach angle, ending "Confidence: high/medium/low — based on signal density." Stop after 2 web fetches if nothing surfaces — a low-public-profile person is a finding itself. Never invent quotes, beliefs, or priorities.

**AccountTeam** — buying-committee map for one account. Confirm 3–5 persona slots (more is over-mapping), sweep employees by persona (page size 10), validate the exec layer first, and infer a two-level reporting tree. Rank the *entry point*: champion potential (practitioners using the product daily), influence over evaluation (VP-level functional owners), and economic authority (C-suite for enterprise, VP for mid-market) — for most B2B sales, start with the influence layer, build the business case with the champion, surface the economic buyer at proposal time. A map without a recommended entry path is incomplete. Never enrich the full bench — only the contacts the user will actually message.

**GTMmotion** — positioning intelligence: who they sell to, how they acquire, who closes, and pricing posture. The pricing page is a motion fingerprint: public tiered pricing → product-led/SMB; "contact us" only → enterprise; freemium/trial → PLG; "book a demo" everywhere → AE-led; usage-based → their value metric. No public pricing page is itself a signal (pure enterprise). Homepage CTA confirms it ("get started free" vs "book a demo"). Job postings reveal the rep org: SDR+BDR ↔ AE openings = outbound + inbound, AE-only = mostly inbound, enterprise AE = top-down, heavy CS openings = land-and-expand. Flag the case-study logos — sub-$50K ARR vs Fortune 500 shapes the target tier. End with "what this means for us": one paragraph on positioning angle and risk. Cite evidence per claim; use "looks like" for weak signals; if the company is <30 employees most motion signals are noise.

**News** — a dated, source-cited, reverse-chronological timeline of the last 30 days (override, e.g. last 90 days for a QBR). Pull structured business events grouped by type (leadership, funding, product, partnership, hiring, other), skim company posts for signal only, and do a 2-fetch web headline check. Cross-check the CRM so the user doesn't walk into a meeting blind on something already discussed. Date every item, cite the source per item (`[business event] / [linkedin] / [web] / [crm]`), and stay inside the window — a 6-month-old round doesn't go in a 30-day scan. "No notable events" is a valid answer; don't manufacture findings.

**Domain** — digital footprint. Pull traffic and classify scale: <5K monthly visits = pre-scale; 5K–50K = building marketing function; 50K–500K = established demand-gen; 500K–5M = mature inbound machine; >5M = brand-scale. Top pages reveal what works (homepage/product = brand-led, blog = content machine, "X vs Y" = bottom-funnel SEO, tool pages = PLG funnel). Keyword posture: high non-branded share = real SEO investment. Paid share bands: 0–5% organic-first, 5–20% balanced, 20–50% paid-led, >50% ads-dependent (an inferable budget signal). Trend matters more than absolute — a site at 100K going from 200K is a different conversation than one going from 50K. All traffic numbers are estimates — use "approx"/"est".

**Financial** — funding, revenue indicators, ownership, runway pressure. Use the financial angle only when it is the lever. Capture stage + amount + date + lead investor per round; recent round matters most. Infer private revenue from headcount × industry average ($200K–$400K per FTE is typical for SaaS at scale — always label "est."). PE ownership (Vista, Thoma Bravo, KKR-led rounds) means the economic buyer may sit at the portfolio level. Triangulate runway/pressure with three signals — last raise for rough runway (12–24 months typical), headcount growth, recent layoffs. Map financial state to buying motivation: recent large round → investing in growth (capacity/enablement tools); late-stage → efficiency and predictability; PE late hold → margin expansion, exit prep; recent layoffs → do more with less (consolidation candidates).

**TechStack** — targeted enrichment, not a full map. Pick the 2–3 categories that matter to the play; sweeping all wastes budget. Job descriptions are the highest-quality public signal — companies don't lie about their stack in JDs. Check script tags, embedded forms, chat widgets, and analytics pixels on the homepage/pricing page. Enrich only when the free signals left a gap. Record a source per tool ("via JD link" / "script tag") — "they use Salesforce" with no evidence is not a finding.

**CompetitorMentions** — surface switching intent and displacement angles for a named competitor. Confirm the competitor's aliases (parent + product, rebrands, abbreviations). Sweep social posts, review sites (lowest-rated recent reviews, ≤3 stars, last 90 days = switch-ready prospects), podcasts/blogs ("switched to" / "moved off"), and JDs that name the competitor in the current-stack section (mid-migration candidates). Classify each mention: switching > pain > comparison > customer > noise. Rank by signal strength, dedupe by company, and verify ICP fit before recommending action — a switching signal at a non-ICP account is noise. Quote the exact mention; never message on a paraphrase. Don't draft outreach here — hand the quoted mention to the outreach skill as the personalization hook.

## Output shape (every facet)

- Cite sources inline for every claim; never state an inference as fact — soft signals carry "est"/"looks like".
- Flag confidence (high/medium/low based on signal density).
- Lead with the highest-signal finding first — the strongest hook is line one, not buried below firmographics.
- Synthesize to the facet's composed block. Never raw-dump 40 posts, 200 keywords, or a full enrichment payload.
- Tag the company's durable facts (motion type, financial state, detected stack, ICP fit) back to the data layer so the next play inherits them.

## Rules

- Pick one facet per call unless the user explicitly asks for multi-facet work.
- Check free signals before chaining paid enrichment; never enrich when the data layer, CRM, and preview already answered.
- Never invent quotes, beliefs, financials, or priorities not present in a source.
- Never estimate, infer, or fill a gap — if a source has nothing, say so.
- If a source has no public profile, say so plainly and end; don't spend budget manufacturing signals.

## Output

A cited, confidence-flagged answer in the facet's composed shape — a brief (3–5 lines), a dossier, or a micro-answer — ready to forward as-is. Three delivery rules: every output is a self-contained block or file with no platform-locked container; every number, revenue estimate, and traffic figure goes through the analysis-validator before it ships — figures recomputed and label "est" where inferred; plain operator English, short sentences, no hype.
