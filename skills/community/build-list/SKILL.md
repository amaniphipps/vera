---
name: build-list
description: Use when asked for a prospect list of target accounts, ICP-fit companies, or decision-maker contacts — run a cost-tiered column plan that kills noise with free filters before any paid enrichment.
---

# Build List

You build prospect lists of companies, contacts, or both, and you build them the cheap way first. The core idea is a **column ladder**: a table where every column knows what it reads, what it costs, when it runs, and what to write when it can't resolve. You never "search and figure out what to do with the results" — you write the column plan, show it to the user, then run it. Cheap filters kill the most rows; only survivors reach the expensive columns.

## Step 0 — Lock the brief, push back on fuzz

Before any tool call, restate the brief as WHO + WHAT + WHY + SIZE:
- **WHO** — which ICP segment + which persona(s). Multiple segments and none picked? Ask.
- **WHAT** — which constraints are hard (must) vs soft (nice-to-have).
- **WHY** — which motion (cold blast, ABM, signal-trigger, event follow-up, competitor displacement).
- **SIZE** — target row count.

Push back hard if the brief contradicts the org's saved ICP segments. Don't silently obey "build me a list of dentists in Ohio" when the org sells observability to engineering teams — call it out and ask whether this is a real off-ICP experiment or a misfire. If the brief is "lots of SaaS companies that might want X," that's not a brief. Ask which sub-segment, what size band, what signal.

## Step 1 — Size the audience first

Always run a sizing call (`size: 1`) against the candidate filter set before any full pull, and read the `total` field.
- Audience <50 companies → surface it before proceeding. Thin niches need broader filters or a fundamentally different sourcing path, not more retries of the same query.
- Audience >5,000 → the brief is too loose. Ask for a tighter filter before pulling anything.

Sizing first prevents the failure mode where you discover after 20 calls that the niche is empty.

## Step 2 — Write the column plan and show it to the user

Draft the ladder before sourcing. Fill in motion-specific columns, drop what the motion doesn't need:

```
INPUT  (free preview)
  domain, name, employee_band, industry, geo, linkedin_url

FREE ELIMINATION  (no cost — pure code/formula filters)
  dedupe_keep        drop duplicate domains (normalize www, lowercase)
  in_geo             hard-filter geo from the preview field
  in_size_band       re-filter employee count to the exact threshold
  not_in_crm_active  drop records already in active sequences
  name_sniff_test    cheap LLM scan on name+domain: "plausibly fits the brief?"
  -> icp_pass = AND(all of the above)

CHEAP ENRICHMENT  (~1 credit each — only IF icp_pass)
  + enriched_headcount, enriched_hq_city, enriched_tech_stack
  -> icp_pass_strict = AND(icp_pass, enriched columns confirm)

AI RESEARCH COLUMNS  (LLM tokens — only IF icp_pass_strict; one narrow question each)
  + sells_dtc  /  has_signal_X
  -> research_pass = AND(icp_pass_strict, sells_dtc=yes, ...)

TIER  (free)
  + tier = A/B/C/D from research_pass + signal strength
  -> drop tier=D before any contact work

PEOPLE DISCOVERY  (free preview — only IF tier in {A,B,C})
  + contact_rows filtered to persona(s)
  -> people_pass = persona match + LinkedIn URL present

CONTACT ENRICHMENT  (paid — only IF tier in {A,B} AND people_pass)
  + verified_email (waterfall: cheapest -> next -> coalesce -> verify)
  + phone (A-tier only, only if a cold-call motion exists)

ACTIVATION  (only after explicit user approval of size + cost)
  -> save as a list tagged with segment + source
  -> A-tier: priority outreach; B-tier: standard nurture; C-tier: low-touch
```

Show the table and confirm columns plus the explicit `icp_pass` definition before running. A 30-second clarification now saves hours of misaimed enrichment later.

## Step 3 — Execute the ladder

Run columns top-to-bottom. The moment the pool crosses ~50 rows, stop reasoning over rows in conversation — dump to a file, merge by normalized domain, and run each column as a code pass. Provider-call rules:
- **Autocomplete before search** for enum-like filter values (industry, location, size band) — guessing enums causes silent zero-result or 422 errors.
- **Multi-source for coverage.** One source ≈60% of the universe, two ≈85%, three ≈92%. Default order: the native business-data preview → CRM closed-lost/churned/dormant → a specialty source only if the first two left obvious gaps. Same provider with different filters is NOT multi-source.
- **Companies first, then people.** Never start with a broad people search like "VP Sales at SaaS companies." Build the company set, then find people at those specific companies.

## Step 4 — Free elimination is the most important step

Run this before any paid call, in code: (1) domain dedupe (normalize, drop dups); (2) hard re-filter preview fields — if the user asked "20+ employees" and the preview band is "11–50," that bucket is ambiguous; drop it or flag it for enrichment, never treat a soft bucket as proof of a hard threshold; (3) geo precision — state ≠ city, flag don't count; (4) CRM cross-check — drop anything in an active sequence or recent open opportunity, duplicate touches kill deliverability; (5) cheap LLM sniff test on names + domains. This step kills 60–80% of the pool and is the single biggest cost save in the flow. Skipping it and going straight to enrichment is the most expensive failure mode.

## Step 5 — AI research columns as delegated sub-agents

One narrow question per column per row — never combine "is this DTC AND in SF AND sells electrical" into one prompt; that's three columns. Prompt shape: visit the domain, answer ONE question, look at these specific pages, return yes / no / unclear, don't guess. Rules: run only on rows that passed `icp_pass`; pilot on 10 rows first — if 80%+ return "unclear," the question is wrong, rewrite before scaling; use the cheapest viable model; always include an "unclear" fallback so an unreachable page doesn't crash the column.

## Step 6 — Tier, then discover contacts

Tier rule: **A** = passes ICP and has an active signal (funding, hiring, intent, news); **B** = passes ICP, no active signal; **C** = partial fit, worth nurture; **D** = fails ICP, drop immediately. Drop D before contact discovery. Contact caps per play: cold blast / single-thread = 1 contact per company; ABM / multi-thread = 3–5 spanning the buying committee.

## Step 7 — Email waterfall on the slice that matters

Only on A/B-tier contacts, cheapest provider first, fall back only on a miss. For >20 rows, batch in code (max 50 actions per batch). Validate after coalescing, never during; drop `invalid`. Treat `catch_all` as risky — ship only if the user accepts the deliverability hit. Drop role-based emails (`info@`, `support@`, `hello@`, `admin@`, `contact@`) before activation. Phone enrichment only on A-tier with a cold-call motion.

## Step 8 — Dedupe, show cost, activate

Dedupe by normalized domain at company level, by verified email (fall back to LinkedIn URL) at person level, and cross-check the CRM for active sequences. Show the user list size, tier breakdown, column completeness, and estimated cost — wait for explicit approval. After approval, save the list tagged with segment + source and route per activation defaults. The skill is **not done** until the list exists or the user explicitly abandons it — don't end on "want me to proceed?" with no list created.

## Universal rules

1. No paid column without `icp_pass = true` — every paid column has an explicit run-when Boolean.
2. Size before sourcing — the first call is always a `size: 1` check.
3. Companies first, then people.
4. Autocomplete before search — never guess enums.
5. Cheapest filter first — free elimination kills 60–80% before any cost is incurred.
6. One question per AI column.
7. Pilot on 10 rows before scaling any new column or provider.
8. Show the plan before running, and size + cost before activating.
9. Push back on briefs that contradict the saved ICP.

## Anti-patterns

- Running the same provider four times with different filters and calling it "multi-source."
- Skipping autocomplete on enum values — causes silent 422s.
- Treating an "11–50" preview band as a match for "more than 20 employees."
- Letting state-level matches pass when the user asked for a city.
- Enriching the full pool before free elimination — the biggest cost leak.
- Combining three questions into one AI research prompt.
- Ending on "want me to proceed?" with no saved list.
- Quietly obeying a brief that contradicts the saved ICP.

## Output

A saved, deduplicated prospect list (CSV) tagged with segment and source, plus a one-page readout showing list size, tier breakdown, column completeness, and estimated cost. Three delivery rules: the list is a self-contained forwardable file with no platform-locked container; every count, percentage, and coverage claim goes through the analysis-validator before it ships — tier counts and coverage ratios recomputed; plain operator English, short sentences, no hype.
