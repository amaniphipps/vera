---
name: documents
description: "Use when producing Word, Excel, or PDF deliverables. Pick the format and follow its procedure."
---

# Documents

Create, edit, and verify Word, Excel, and PDF deliverables. This skill teaches which format to pick and routes to the procedure for each.

## Pick the format

| Need | Format | Read |
|---|---|---|
| Prose, reports, memos, letters, tracked changes | Word (.docx) | references/docx.md or `skills/community/docx` |
| Tabular data, formulas, models | Excel (.xlsx) | references/xlsx.md or `skills/community/xlsx` |
| Fixed layout for distribution, forms, signatures | PDF | references/pdf.md or `skills/community/pdf` |
| Slide decks, presentations, pitches | PowerPoint (.pptx) | `skills/community/pptx` |

Rules of thumb:

- Word for documents people will edit. Use when the reader needs tracked changes or comments.
- Excel for anything that computes. Use when the deliverable contains formulas that must recalculate.
- PDF for anything the reader must not edit, or that must look identical everywhere.

## Shared delivery rules (all formats)

- Verify before you hand it over. Render the Word or PDF to images and look at them. Recalculate the Excel and confirm zero formula errors.
- Match an existing file's conventions. When asked to edit a file, follow its fonts, styles, and structure. Do not redesign.
- Use professional fonts from the org slots (org.example.yaml) unless the user says otherwise.
- Keep templates in the templates dir from org.example.yaml.
- No placeholder text, no leftover demo copy. Output is ready to forward as-is.