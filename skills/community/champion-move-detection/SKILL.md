---
name: champion-move-detection
description: "Use on a monthly cadence to detect champions and heavy users of your paying customers who changed jobs, verify each move against live LinkedIn data, score the new company, and surface qualifying moves as MQLs — while catching churn risk on the account they left."
---

# Champion move detection

You run the monthly machine that turns "a known buyer took your product to their next company" — one of the highest-converting signals in B2B — into a deterministic, deduped MQL, with hard guards against the classic failure modes: stale headlines, same-name profiles, and warm familiarity mistaken for advocacy. Secondary purpose: catch churn risk on the account the champion left.

## Scan set (which accounts run each month)

Run across BOTH: (1) every account in your Closed Won stage — the customer base; (2) any company carrying an active carried-forward champion (tagged `champion-move` AND holding an active `[CHAMPION WATCHLIST]` entry marked `carried-forward`). The latter are NOT customers — they're companies a proven serial champion moved into, tracked so you catch the person's NEXT move. A serial champion is your highest-value signal — never drop them just because their current employer isn't a customer.

Expect the first run to be slow and partial; it builds a watchlist from messy records. Report coverage gaps honestly in the digest — coverage compounds monthly.

Writes permitted: memory updates, state summaries, the `champion-move` tag, MQL stage moves, and alerts — nothing else. **Never send outreach from this skill. It recommends; humans send.**

## Phase 1 — Build / refresh the champion watchlist (per account)

For each Closed Won account, keep a watchlist of up to **5** people, persisted under the header `[CHAMPION WATCHLIST]`. If the header exists and was refreshed within the last **90 days**, reuse it and skip to Phase 2 for that account.

A person qualifies via **either** bar:

1. **Champion / economic buyer** — named champion in account memory, state summary, or the CRM's deal history (deal contacts, meeting attendees who drove the purchase).
   - **Realized-value requirement (do not soften).** Only watchlist under this leg if the relationship actually demonstrated value: EITHER the account reached **Closed Won**, OR the person was a **materially active** user (real usage, per the heavy-user bar below). A named contact or "economic buyer" on a deal that **never closed**, or a registered user of a free/never-activated workspace with negligible usage, is **warm familiarity — NOT a champion.** Brand recognition is not advocacy.
2. **Heavy user** — a registered user of the customer's workspace who is **materially active**: a top-2 consumer of product usage over the last **90 days**, or clearly driving the account's workflows. A senior GTM title is NOT required — the heaviest hands-on user is often the strongest future champion regardless of title; that's the point of this leg.
   - **Floor (exclude even top consumers):** pure non-GTM roles — Engineering/IT/DevOps, Support, Finance/Accounting, HR/People, Legal. They operate the tool for reasons unrelated to buying and rarely carry it to a new GTM org.
   - **Keep** anything GTM or GTM-adjacent: sales, marketing, content, growth, RevOps, GTM/product ops, demand gen, founders, GTM-technical roles. Ambiguous title → keep them (a false include costs one monthly lookup; a false exclude misses the signal). Resolve titles via the CRM first, then LinkedIn.

**Heavy-user identification:** use per-person usage attribution from product analytics (individual events/credits/seat activity). Org-level totals cannot attribute usage — never use them. Treat self-declared titles in product data as a persona hint; confirm seniority via the CRM/LinkedIn, never as ground truth.

**Watchlist rules (do not soften):** the heaviest user is often NOT the recorded champion — always check usage, never rely on the champion record alone. **Exclude external consultants** (a workspace user whose email domain differs from the customer's — an agency or RevOps consultancy is not part of that company). Resolve each person's LinkedIn URL at build time — the next phase depends on it; prefer vanity URLs, store whatever resolves, enrich only when missing.

Persist: `[CHAMPION WATCHLIST] — refreshed [date]` with lines `- [Name] | [title] | [email] | [LinkedIn URL] | [champion / economic buyer / heavy user: ~N usage/90d] | last verified [date]`.

## Phase 2 — Move detection (the monthly LinkedIn check)

**Skip guard (dedup — check FIRST).** Skip any entry already marked `MOVED → [company], processed [date]`. That move already fired once; re-detecting it re-surfaces the same MQL. Those entries are historical records, not active targets. Only the person's current-employer entry (active, or `carried-forward`) is live for detection.

For every ACTIVE watchlist person, verify current employment against **live LinkedIn** (a profile lookup that returns the full experience section).

**Live lookup is authoritative.** You are detecting recent moves, and cached enrichment lags exactly there. So: cached enrichment may only help LOCATE a profile at watchlist-build time — never decide employment status. If live lookup errors, retry once with adjusted input; **if it fails twice, classify UNCERTAIN and record the verbatim error in the digest** — a failed lookup is an UNCERTAIN classification, not a ticket. **Never fall back to cached enrichment or generic web research for a STILL/MOVED decision.** Batch lookups aggressively; delegate across sub-agents when the watchlist is large.

**Verification rules (do not skip):**
1. Read the EXPERIENCE section, not just the headline — headlines go stale. Current employer = the most recent experience entry with no end date.
2. MOVED requires affirmative evidence — the profile must explicitly list a NEW current employer. Absence of the old company alone is NOT a move.
3. **Wrong-person guard (HARD RULE).** A MOVED classification additionally requires the destination profile's OWN experience history to contain the ORIGIN company. A name + destination match alone is NEVER sufficient — confirm it's the same human. If the origin doesn't appear → UNCERTAIN. (A real sweep once matched a departed champion to a same-name profile at a different company and fired a false high-tier MQL.)
4. Advisor, fractional, board, and "managing partner" roles are NEVER a MOVED → UNCERTAIN, note the role type; a fractional consultant/agency operator is a potential partner lead instead. **Dual-role exception:** if the person lists BOTH old and new companies as current, classify MOVED but flag `dual-role` — and soften all churn language on the old account (they haven't left; they've added a role).
5. Profile not found → UNCERTAIN. Never guess. UNCERTAIN people go to the human-review list and retry next month.

Classify each person: **STILL** (update "last verified") / **MOVED** (record new company, new title, move date) / **UNCERTAIN**. Ignore moves where the new company is another existing customer — internal reshuffle, not a new-logo signal; note it, don't create an MQL.

### Batch mode (delegated sweeps)

When run as a delegated batch sub-agent (a monthly sweep fanned across accounts), execute Phases 1–2 ONLY — no stage moves, no tier tags, no CRM writes, no channel posts, no tasks of any kind. Return classifications + evidence in the requested format, and put operational problems (lookup failures, missing workspaces, unresolved profiles) in a PROBLEMS section, never into tasks or alerts. Phase 3 runs only when explicitly instructed, for named verified movers.

## Phase 3 — On every confirmed move

Every task/alert this phase produces is assigned to the **MQL owner**. The prior-relationship owner is NOT an automatic sender — surface them as a recommendation inside the task ("consider having [prior deal owner] send — they owned the relationship at [Old Account]"). The MQL owner decides who sends.

**A. The old account (losing a champion):**
1. Prepend `[CHAMPION DEPARTED] [date] — [Name] ([title]) left for [New Company] ([new title]). Was: [qualification reason]`.
2. **Mark the entry processed (dedup):** update the person's line to `MOVED → [New Company], processed [date]`. Do not delete it — that record is what makes the run idempotent month over month.
3. If the account is an active paying customer and that person was its primary user/champion → flag **churn risk** in the digest and state summary.
4. **Compound-departure escalation:** two or more watchlist people from the same account gone (this run or prior) → flag **critical churn risk** prominently.

**B. The new company:**
0. **Champion-qualification gate (run FIRST).** The machinery (tier floor, MQL, tag) applies only to a person who actually realized value at origin. Confirm BOTH: **realized value** (origin is Closed Won, OR the person was materially active there), and **origin deal is not a recent loss** (Closed Lost within the last 90 days fails — they're leaving a company that just declined you). **Either check fails → STOP: no tier floor, no MQL, no tag, no scoring run.** Log the move to both companies' memory and, only if GTM-relevant and the new company is a plausible ICP fit, post a soft FYI to the digest as a potential future warm intro — never a sales motion, never an MQL. Still carry the person forward per C (trajectory tracking is independent of this gate).
1. **Competitor / never-prospect check FIRST.** New company is a direct competitor → log to memory only; no scoring, no MQL. Also respect standing never-prospect entries in org memory.
2. **Verify employee count and funding with real sources** (LinkedIn company page; enrichment for funding). **Never guess funding** — routing hinges on it. If funding can't be sourced and headcount is near the self-serve threshold, classify routing NEEDS-REVIEW in the digest instead of deciding.
3. **Score the new company — this trigger behaves like every other signal-driven trigger.** Run the account-scoring skill in full, feeding the champion move in as the triggering **high-intent, first-party signal with relationship context** (who the person is, which customer they championed, what they did with the product, new title + company, and who owned the prior relationship). The scoring skill owns everything downstream.
   - **Tier floor:** a confirmed champion move is demonstrated first-party history; any result that would land mid-tier is raised to **one tier above your standard mid-tier** (never lifts the lowest tier).
   - **Gate precedence:** the tier floor does NOT override the scoring skill's hard gates. If the self-serve gate fires (**<50 employees AND ≤$10M raised**), there is NO MQL — post an FYI: a champion joining a small startup is future pipeline deserving a personal note from the old owner, not a sales motion. Same precedence for vendor/partner, government, VC/PE, and competitor gates.
4. **When scoring lands at or above the floor with no gate fired**, it produces an MQL through its normal flow. This skill only contributes provenance: apply the `champion-move` tag to the new company; ensure the champion exists as a contact with their LinkedIn URL and a note capturing the prior relationship. Don't duplicate the scoring skill's steps.
5. **Multiple movers to the same destination = ONE stronger signal**, scored once. Never fire several MQLs for one company.
6. Prepend to the new company's memory: `[CHAMPION ARRIVED] [date] — [Name] joined as [new title]. Ex-[Old Account] ([qualification reason]). Scored [tier]. MQL: [yes/no + why].`

**C. Carry the champion forward (track serial movers forever):**
A proven mover — someone who already carried the product company to company — is your highest-value person; their NEXT move is hotter, not colder. The champion travels with the person, not the account.
1. Add the person to the NEW company's watchlist as a live `carried-forward` entry. This entry is ACTIVE for detection — next month Phase 2 verifies them at the new company and catches the next move, firing a fresh MQL there. The chain continues indefinitely.
2. This applies **regardless of gate outcome** — even an FYI-routed or gated move still carries forward, because tracking is about the person's trajectory, not this company's score.
3. The `champion-move` tag (B.4) + the active `carried-forward` entry are what put the company into next month's scan set. Both required.
4. **Watchlist-rebuild interaction:** the 90-day rebuild refreshes an account's native champions/heavy users from current CRM + usage. It must NOT delete `carried-forward` or `MOVED → processed` entries — preserve them; only refresh the natively-sourced lines.

## Phase 4 — Monthly digest

End with ONE summary: accounts scanned, watchlist size, moves confirmed (with tiers + MQL status), FYI-routed moves, UNCERTAIN people needing human review, churn-risk flags (compound first), NEEDS-REVIEW routing calls, and coverage gaps.

## Guardrails

- Never fire the MQL flow on UNCERTAIN — false alerts erode trust in the signal.
- Never send outreach from this skill.
- Credit discipline: keep watchlists tight (Phase 1 filters + 90-day reuse) rather than checking every contact every month.

## Output

A monthly digest (moves confirmed with tier + MQL status, churn-risk flags, UNCERTAIN human-review list, coverage gaps) posted to the digest channel, plus a self-contained CSV of move classifications with evidence and watchlist deltas.

Delivery rules: (1) every output is a self-contained file ready to forward as-is — no platform-locked container; (2) every number, rate, or claim — including every MOVED/UNCERTAIN call and tier result — passes through the analysis-validator before shipping (evidence matched to the live-LinkedIn read, funding sourced, never guessed); (3) plain operator English, short sentences, no hype.

A monthly run should read like a machine, not a hunch: every active watchlist person got a live LinkedIn check; every MOVED survived the experience-section read, the affirmative-evidence bar, and the wrong-person guard; warm familiarity never got promoted to champion; a mover into a competitor or a tiny startup produced a memory note and an FYI, not an MQL; one company with three arriving champions fired exactly one scoring run; and a human reviewed every UNCERTAIN instead of the machine guessing.
