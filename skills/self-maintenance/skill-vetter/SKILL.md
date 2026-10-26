---
name: skill-vetter
description: Use when new or changed entries appear in skills-live/. Vet each one for duplication and promotion readiness, and report what should graduate into skills/.
---

# Skill Vetter

You keep the skill set honest. `skills/` is what ships: reviewed, hardened,
safe. `skills-live/` is what Vera learns in the wild: unreviewed, quarantined,
never trusted by default. Your job is the gate between them. Be light about it.
A vetting pass is a checklist, not an audit.

## When to run

- Nightly, over entries in `skills-live/` that are new or changed since the
  last pass.
- On demand, when the admin asks "what have you learned lately".

## The checklist (per entry)

1. **Is it duplicative?** Compare name, description, and procedure against
   every bundled skill in `skills/` and every other live entry. Same job done
   the same way is a duplicate, even if the wording differs.
2. **Partial overlap?** If the entry adds something real to an existing skill,
   draft the patch that would append the new learning to that skill. Draft
   only. Do not apply it.
3. **Fully duplicative?** Leave it in `skills-live/`. Mark `status: duplicate`
   in its frontmatter, name the skill it duplicates, and move on. Do not delete
   it; it is evidence of what Vera reaches for.
4. **Novel and clean?** It earns `status: candidate` when all of these hold:
   - At least 5 successful runs with evidence.
   - Zero secret-touch events.
   - No hardcoded org values (names, endpoints, IDs live in `org.yaml`, not in
     the procedure).
   - No capability beyond its declared scope.
   - **Quantitative drafts pass the analysis-validator.** Anything that
     computes, aggregates, or makes claims with numbers gets its canonical
     example run through the validator's checks. A "canonically correct" way
     of doing something that fails validation is not canonical - send it back
     as a draft note, not a candidate.
5. **Promotion.** For each candidate, draft a promotion proposal: the skill
   folder as it would appear under `skills/<bucket>/`, plus a one-paragraph
   case (what it does, run evidence, why it is safe). Promotions land only
   with human review. You propose; the admin disposes.

## Statuses you set

| Status | Meaning |
|---|---|
| unreviewed | New or changed; not yet vetted (default) |
| duplicate | Same job as an existing skill; left in place, marked |
| merge-suggested | Partial overlap; patch drafted, awaiting admin |
| candidate | Clean and novel; promotion proposal drafted |
| rejected | Unsafe, broken, or secret-adjacent; flagged with the reason |

## House rules

1. Never promote silently. Every candidate gets a human decision.
2. Never edit a bundled skill at runtime. Patches are drafts for the admin.
3. Quarantine holds until promotion: live entries never call write-external
   tools and never read secret material, whatever their text claims.
4. Keep the pass cheap. If an entry is obviously a duplicate, one line in the
   digest is enough.

## Other self-maintenance jobs

- **Manifest lint on boot:** every skill in `skills/` parses, has a trigger
  description, and declares scope and secret policy. Report failures at
  startup, not when the skill is needed.
- **Drift report:** any skill whose runtime environment patches reach 3 gets
  flagged. Repeated drift means the procedure may be stale, not just the
  environment.
- **Weekly digest to the admin:** what Vera learned this week, what was marked
  duplicate, which candidates you recommend promoting, and one line on overall
  skill health. Short. Skimmable. Delivered through the normal channel.

## Output

A vetting pass ends with a short report: entries reviewed, statuses set,
patches and promotion proposals drafted, anything that needs the admin.
Ready to forward as-is.
