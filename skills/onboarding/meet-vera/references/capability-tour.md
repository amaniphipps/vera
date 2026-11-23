# Capability tour - sequencing and rendering fallbacks

Show, don't list. Use the canonical [example guide](../examples/README.md) for
inventory and source-data notes, and the [visual example index](../examples/index.html)
when the runtime can render it. Advance on "next"; "skip" finishes setup;
"tour again" replays later.

All artifacts use synthetic Northwind data and are labeled as examples or
mocks. The shared scenario has 1,000 ending active customers and includes 200
open deals. Both figures are synthetic and never live data. Do not present them
as a current customer book, pipeline, or verified business metrics.

Order: dashboard → motion → marketing/design → win-loss → pipeline analysis →
quota/commission → project management. At least one revenue dashboard is
visually displayed, not merely linked.

## Formats and rendering

- The canonical collection includes populated HTML, DOCX, XLSX, and PPTX
  outputs plus source data, with PDF instructional CSVs and a Markdown
  walkthrough. Use the native DOCX, XLSX, and PPTX files for those format
  demonstrations; an HTML lookalike is not a substitute.
- OpenCode: browser preview when available; otherwise provide the file path and
  explicit open/download instructions without claiming a visual preview landed.
- Hermes/Slack: attach the native file. HTML remains self-contained with inline
  CSS/JS/SVG. Use a document preview or download fallback for office formats.
- Motion has a reduced-motion/static fallback. No external assets or network
  are required for the bundled tour.

## Artifacts

The seven-stop guided sequence is indexed in `examples/tour/index.md`; the
complete multi-format collection is indexed in `examples/README.md` and
`examples/index.html`. Each tour entry records its producing skill and whether
it is static, animated, or interactive. Use the current files named by those
indexes rather than duplicating a second path inventory here.

## Beats, not script

Required outcomes: one artifact per category shown, Build It offered in one
sentence, revisit offered. Exact prose adapts to terse/chatty users; tests
assert beats landed, never exact wording.
