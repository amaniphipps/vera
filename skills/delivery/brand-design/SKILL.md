---
name: brand-design
description: "Use when creating any branded deliverable. Apply the org's tokens, voice, and do/don't rules before content ships."
---

# Brand design

Every deliverable that someone will read, send, or share carries the org's brand. This skill makes the brand repeatable. It teaches how a brand system is organized, and how to apply it to any output from a chat answer to a full document.

The example brand used throughout is a neutral placeholder called **Northwind**. Replace it with the org's real brand by filling in `org.example.yaml`.

## How the brand system is organized

A brand system is four parts, each in its own slot:

1. **Tokens** — colors, fonts, and logo paths. The only place these live is `org.example.yaml`. Nothing else defines them.
2. **Voice rules** — how copy sounds. Adjectives plus a ban list.
3. **Do / don't** — concrete choices that make output look and read like the org.
4. **Application** — a checklist run against every artifact before it ships.

## Tokens

The Northwind example tokens, as CSS variables any HTML output can consume:

```css
:root {
  --accent: #3559D6;   /* primary: headers, actions */
  --accent-2: #0F8A75; /* secondary: alternate series */
  --ink: #1B1F27;      /* text */
  --paper: #F4F5F7;    /* light background */
  --dark: #14182e;     /* dark surface */
}
```

Fonts stay on a system stack so output renders offline. Logos always come from the `logos` slots. Never reconstruct a logo from description.

## Voice rules

- Sentence case on all headings. Not Title Case.
- Short sentences. Plain words over jargon.
- Specific over abstract. "Handles 3 tools at once" beats "streamlined workflows".
- Second person ("you") when addressing an audience. First person plural ("we") for the brand's own voice.
- No em dashes. Use commas, colons, or parentheses.

Banned words live in `org.example.yaml` under `voice.banned_words`. The default ban list is: unleash, elevate, seamless, next-gen, transformative, revolutionize, robust, cutting-edge, leverage, powerful solution. If you are about to write one, stop and name the concrete outcome instead.

## Do / don't

**Do**

- Lead with the outcome, then the mechanism.
- Use approved colors and fonts only. No new colors invented mid-output.
- Pull the logo from the `logos` slots, on the correct background.
- Keep display text short. Max two emphasis words per heading.

**Don't**

- Never invent product behavior, numbers, or customer quotes. Miss a fact before you fake it.
- Never approximate the logo.
- Never use a banned word or an em dash.
- Never ship placeholder copy. Output is ready to forward as-is.

## Applying brand to an artifact

Run this checklist before any deliverable ships:

1. Tokens: correct colors and fonts from `org.example.yaml`?
2. Logo: present, pulled from a slot, correct background variant?
3. Voice: sentence case, short sentences, no banned words, no em dashes?
4. Traces: every number and quote traces to source data?
5. Ready: no watermarks, no draft states, no placeholder demo copy?

When the artifact is HTML, apply tokens as CSS variables on `:root` and reference them everywhere. When it is a text answer, apply the voice rules but skip visual tokens.

## Updating the brand

To give Vera the org's real brand, edit `org.example.yaml`:

1. Set `brand.name` and `brand.tagline`.
2. Fill `colors` with the real palette.
3. Fill `fonts` with the real font stack.
4. Set `logos` to real file paths.
5. Set `voice.adjectives` and add real ban words.

Do not hard-code brand values into skills. The org slots are the single source of truth, so one edit updates every deliverable.