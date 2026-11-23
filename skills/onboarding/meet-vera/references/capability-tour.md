# Capability tour — sequencing and rendering fallbacks

Show, don't list. Mocks use synthetic Northwind data, labeled mock. Advance
on "next", "skip" finishes setup, "tour again" replays later.

Order: dashboard → motion → marketing/design → win-loss → pipeline analysis →
quota/commission → project management. At least one revenue dashboard is
visually displayed, not merely linked.

## Rendering

- OpenCode: browser preview when available; otherwise file path + offer to open.
- Hermes/Slack: file attachment; HTML self-contained, inline CSS/JS/SVG.
- Motion has reduced-motion/static fallback. No external assets or network
  required. A file path alone is not considered showing it.

## Artifacts (see examples/tour/index.md)

dashboard, motion, marketing/design, win-loss, pipeline, quota/commission,
project plan. Each records producing skill, mock/static/animated/interactive
kind, and fallback. Existing mock-forecast.html may serve as dashboard
candidate until the tour-specific file lands.

## Beats, not script

Required outcomes: one artifact per category shown, Build It offered in one
sentence, revisit offered. Exact prose adapts to terse/chatty users; tests
assert beats landed, never exact wording.
