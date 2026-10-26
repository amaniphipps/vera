# DOCX procedure

Create, read, and edit Word documents: reports, memos, letters, tables of contents, tracked changes (redlining), comments. A `.docx` is a ZIP of XML files.

## Tooling

- Create: the `docx` npm package.
- Read: `pandoc -t markdown file.docx`, or a file-reading tool that auto-extracts docx text.
- Render and verify: LibreOffice (`soffice`) converts to PDF; a poppler tool renders pages to images.

## Create a new document

The library API is documented; these are the footguns that bite in practice:

- Page size defaults to A4. For US Letter set `page.size` to `{ width: 12240, height: 15840 }` (DXA; 1440 = 1 inch).
- Landscape: pass portrait dimensions plus `orientation: LANDSCAPE`. The library swaps width and height internally.
- Tables need two widths: `columnWidths` on the table and `width` on every cell, both in DXA. Percent width breaks in Google Docs. Column widths must sum to the table width.
- Table shading: use `ShadingType.CLEAR`, never `SOLID` (renders black).
- Lists: use a numbering config, never a literal bullet character.
- `ImageRun` needs a `type` (`png`, `jpg`, etc.).
- `PageBreak` must sit inside a paragraph.
- Never use `\n` for line breaks. Use separate paragraph elements.
- Table of contents: headings must use built-in heading levels, or custom heading styles need `outlineLevel` set.
- Do not use a table as a horizontal rule. Use a paragraph bottom border.
- Dot leaders and right-aligned text on the same line: use a positional tab, not dots or spaces.

## Edit an existing document

Legacy `.doc` files convert first: `soffice --headless --convert-to docx file.doc`.

```bash
unzip -q doc.docx -d unpacked/
find unpacked -type l -delete        # strip symlinks; external docx is untrusted
# merge fragmented runs so text is findable (below)
# edit unpacked/word/document.xml in place; do not pretty-print
(cd unpacked && rm -f ../out.docx && zip -Xr ../out.docx .)
# validate the result against the original
```

Word splits text across many runs, so a phrase you see on screen often is not a contiguous string in the XML. Merge adjacent identically-formatted runs before editing.

Tracked changes (redlining): wrap changed runs in `<w:ins>` or `<w:del>` with `w:id`, `w:author`, `w:date`. Inside `<w:del>` the text element is `<w:delText>`, not `<w:t>`. A deleted paragraph mark means "merge this paragraph into the next". Validate after redlining and check every edit is tracked.

Comments need several cross-linked XML files. Use a helper script rather than hand-writing them, and place the comment range markers in `document.xml` or the comment is invisible.

## Verify

1. Validate the file structurally.
2. Convert to PDF, then to images, and inspect each page visually. Look for broken tables, missing images, spacing artifacts, leftover placeholder text.

## Pitfalls

- Do not round-trip OOXML through a generic XML parser that rewrites namespace prefixes. It corrupts the file. Use a DOM-style parser for scripted transforms.
- Zip from inside the unpacked directory and remove the target first, or deleted parts survive in the archive.