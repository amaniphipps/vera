# Community skills

Third-party skills, imported with permission of their license and reshaped to
Vera's format. They ship at `tier: draft`: reviewed at import, marked
community-import in their manifests, and promoted through the normal tiers
(candidate, hardened) only after they prove themselves in use.

## Current sources

- **[swan-gtm/gtm-skills](https://github.com/swan-gtm/gtm-skills)** (MIT) -
  open GTM skills from practitioner authors, ranked by real install counts.
  Selected for fit with how Vera works (RevOps analysis, deal intelligence,
  signals, planning), deduplicated against her authored skills, converted to
  vendor-neutral language, and given Vera output contracts. Full per-skill
  credit: [ATTRIBUTION.md](ATTRIBUTION.md).
- **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT) -
  Matt Pocock's engineering and productivity skills. `ask-matt` routes any
  coding intent to the right skill or flow in his catalog (and installs
  missing ones on demand); `diagnosing-bugs` is his feedback-loop-first bug
  discipline; `teach` is a stateful multi-session learning workspace.
  Full per-skill credit: [ATTRIBUTION.md](ATTRIBUTION.md).
- **[anthropics/skills](https://github.com/anthropics/skills)** (Apache-2.0) -
  production document creation and editing skills for Word (`docx`), Excel (`xlsx`),
  PDF (`pdf`), and PowerPoint (`pptx`) with schema validators and recalc engines.

## The rules for anything in this bucket

1. Attribution travels. Every manifest carries `source_repo`,
   `source_author`, `source_license`. ATTRIBUTION.md is the human-readable
   index.
2. Vendor-neutral always. Skills speak in GTM verbs ("the CRM", "the
   enrichment tool"), never product names.
3. Vera's output contract applies: self-contained files, validated numbers,
   plain voice.
4. Draft until proven. The skill-vetter and human review promote; nothing
   here skips the line.
