# Product and UI mockups

Build HTML mockups of a product screen that look like the real app, not a generic SaaS template.

## When to use

- "Mock up <feature>" or "show what <idea> would look like in the product".
- Demo flows and feature walkthroughs.
- Product concept pitches that must look like the real product and carry real data.

Do not use for marketing or brand collateral, or for prototypes of a product that does not exist yet.

## Prime rule: production is the ground truth

A mockup is graded against the production app, not against any skill token table. Skill palettes drift from the live app. Grounding order: production code first, then live screenshots, then fresh design files, then token tables. Never invent a visual language when a production reference exists.

## Step 0: reference check (mandatory, every run)

Before any design work, establish what production actually looks like today. No reference check, no mockup. Sources in order:

1. Production code. Search the app's own repo for the screen's views, components, and models. Confirm current layout, real navigation, terminology, and business rules. Code beats memory.
2. Screenshots of the live app. Read them with a vision tool.
3. Design files, freshest only. Apply a recency rule (e.g. 12 months).
4. Token tables. Fallback only. Flag conflicts with 1 through 3.

Write down before coding: page anatomy, nav structure, token table, terminology, and business rules that shape the screen.

## Fidelity ladder (default is replica)

- Tier 1, screen exists in production: replicate it as closely as possible. Same anatomy, elements, copy patterns. Creativity is a defect here.
- Tier 2, variation of an existing screen: keep production anatomy exactly; change only the content the user asked about.
- Tier 3, net-new feature: compose only from existing production elements. Any new element is built from the current token set and labeled in the delivery note as invented.

## Never ship these

- Demo-instrumentation copy as UI text. If a sentence explains the demo, it does not belong on screen.
- Foreign UI fragments bleeding in from other screens.
- Scale contradictions. Numbers on one screen must agree.
- Orphaned controls. Buttons or arrows with no context.
- Vendor names in user-facing copy.

## Real assets

Pull real assets from the production source. Copy the official logo from the design source or a screenshot; never redraw it. Crop product images from screenshots when no clean source exists, and embed them. Re-verify the token set each run and note the date you checked.

## Procedure

1. Reference check (Step 0). Write down anatomy, tokens, terminology, business rules.
2. Pull real data.
3. Build one self-contained HTML file. Inline SVG or base64 assets, no external dependencies beyond a font. Note the fidelity tier in the design plan; list tier-3 inventions explicitly.
4. Verify in a browser. Open the file, exercise every interactive path, then do a visual QA pass. Check that every number on screen agrees and every sentence is shippable product copy. Fix and re-check until clean.
5. Deliver. Note the fidelity tier and any invented elements.

## Pitfalls

- Design file APIs rate-limit hard. Space paged calls, honor Retry-After, avoid parallel scans. Large files can blow a long-running job; use background jobs writing to scratch.
- Editing tools may refuse to overwrite a file you have not read this task. Read first, or back up and rewrite.
- Emoji icons read as off-brand. Use inline SVG line icons instead.
- Node ids: URLs and APIs can use different id formats. Confirm which is which.