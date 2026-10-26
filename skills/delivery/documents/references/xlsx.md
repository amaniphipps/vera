# XLSX procedure

Create, read, and edit Excel workbooks: formulas, formatting, charts, data cleaning, format conversion. Every formula-bearing output must be recalculated and error-free before delivery.

## Tooling

- Create or edit with formulas or formatting: `openpyxl`.
- Bulk data in or out: `pandas`.
- Quick look at a sheet: a markitdown-style extractor (one section per sheet, no cell coordinates).
- Recalculate formulas: LibreOffice.

## Requirements for every output

- Professional font throughout unless the user says otherwise.
- Zero formula errors. Never ship while a recalculation reports errors. If an error predates you, prove it by loading the original and looking at that cell.
- Use formulas, never hardcoded results. The sheet must recalculate when inputs change.
- Follow the user's spec literally: exact tab names, exact column headers, the formula they spelled out. A redesign that computes something else fails, however elegant.
- Document every assumption and hardcoded number where the reader will see it, with the source.
- A workbook you create for someone to fill in needs a short legend naming the cells to edit and one example row of realistic values.
- Editing an existing file: match its conventions. They override every guideline. Find its input cells first (often marked by font color or fill), write only there, and leave formulas untouched.

## Recalculate (mandatory when the file has formulas)

openpyxl writes formulas with no cached values. Until you recalculate, every formula cell reads back as empty to anything reading cached values.

Run a recalculate step (LibreOffice computes every formula and rewrites the file in place) and read its result: status, total formulas, total errors, and an error summary naming cells. Fix what it names and rerun. A clean recalc proves your formulas evaluate, not that they are right. Write a few formulas first and check they pull the expected values before building the grid.

A workbook that links to another file loses those links if you save it with openpyxl and then recalculate. The external reference resolves to a separate file on disk; if that file is absent, the cached value is the only thing holding the data, and recalc overwrites it with an error. Copy those cells' values out of the original before saving over them.

## Formulas that survive verification

LibreOffice implements fewer functions than Excel. One it cannot evaluate becomes a literal error baked into the delivered file.

- Prefer Excel-2007-era functions: `SUMIFS`, `INDEX`, `MATCH`, `IFERROR`, `SUMPRODUCT`.
- Newer functions need an `_xlfn.` prefix: `TEXTJOIN`, `CONCAT`, `IFS`, `SWITCH`, `MAXIFS`, `MINIFS`. Written bare, each yields an error.
- Avoid `XLOOKUP`, `XMATCH`, `SORT`, `FILTER`, `UNIQUE`, `SEQUENCE`. Use `INDEX`/`MATCH` for lookups; sort, filter, and de-duplicate in Python before writing.

## openpyxl gotchas

- Reading a model takes two loads: `data_only=True` gives cached values with formulas gone; the default gives formula strings with no values.
- `data_only=True` is destructive if you save: every formula becomes a literal.
- `data_only=True` on a file openpyxl just wrote returns empty everywhere. Recalculate first.
- Merged cells: write the top-left anchor only. Other cells in the range are read-only.
- `.xlsm` loses macros unless you pass `keep_vba=True`.
- A sheet name with a space must be quoted in a cross-sheet reference.

## Modeling convention (when the user asks for clean numbers)

- Color: blue text for hardcoded inputs, black for formulas, green for links to another sheet, red for links to another file, yellow fill for cells the user should fill in.
- Numbers: currency with the unit named in the header; zeros as a dash; negatives in parentheses; percentages stored as fractions (`0.15` renders `15.0%`).
- Structure: every assumption in its own labeled cell, referenced by the formulas that use it; formulas consistent across every period; guard denominators that can be zero.

## Verify

1. Recalculate and confirm success with zero errors.
2. Spot-check a few computed cells against expected values.
3. Extract a quick read and scan for missing sheets, misplaced headers, leftover placeholders.