---
name: vera-reporting
description: "Use when producing a self-contained HTML report. Build one file with inlined CSS and JS that opens anywhere."
---

# Vera Reporting

Build reports as a single HTML file that opens anywhere. No build step, no external assets, no zip. A reader who downloads the file and double-clicks it sees the styled report, never a broken page.

## When to make a report

Make a report when the reader needs to act on numbers, not just see them.

- If the answer is one sentence, reply in chat. Do not build a page for it.
- If the answer needs a chart, a table, and a takeaway next to each, make a report.

## Structure rules

1. **So-what first.** Open with the single most important conclusion, then support it. The reader gets the point before scrolling.
2. **One idea per section.** Number every section. A chart or table never floats without a paired takeaway.
3. **Every takeaway cites data that is on the page.** A claim that quotes a number not in the chart next to it is wrong.
4. **Stay self-contained.** All CSS and JS are inline in the one file. No external stylesheet, no assets folder.
5. **State confidence in the footer.** Say whether the finding is meaningful, directional, or insufficient. A directional finding is more useful than a confidently wrong one.
6. **Validate before shipping.** Any report containing numbers goes through the analysis-validator first. The footer then carries the `Validated by Vera` stamp and a collapsible validation trail (the report is the product; the trail is the receipt).

## The one-file rule

Inline everything that the page needs to render. A report that references an external CSS file or an assets folder renders unstyled the moment it is opened from a download. That is a broken deliverable. Google Fonts are an exception only when offline rendering does not matter; otherwise stay on the system font stack.

## Chart and table patterns

- Bars: set `--bar-max` to the actual largest value in the group. The top bar fills about 95% of its track. Never a round number, never a y-axis max.
- Tables: numeric columns right-aligned with tabular numerals. Hovering a row highlights it.
- Hoverable: charts and tables highlight on hover. Keep the affordance subtle.
- Responsive: table wrappers scroll horizontally on narrow screens. Grids collapse to a single column.

## Brand tokens from org.yaml

Theme values come from the org slots in `org.example.yaml`, applied as CSS variables on `:root`. The template reads `--accent`, `--ink`, `--paper`, `--line`, and the semantic colors (`--good`, `--warn`, `--risk`). Org fonts go into `--font-display`, `--font-ui`, and `--font-mono`. Change org.yaml, not the template.

## Templates

Three report shells live in `templates/`. Copy the one that matches the ask, then replace the data and takeaways.

| Ask | Template |
|---|---|
| Weekly recap, what happened | templates/weekly-recap.html |
| Forecast, where will we land | templates/forecast.html |
| Funnel, where do we drop off | templates/funnel.html |

## Output

- One `.html` file, ready to forward as-is.
- No watermarks, no draft states, no leftover demo copy.
- Default width 1320px, wrapped in the `.report-page` container.