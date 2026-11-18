# PDF procedure

Create, combine, split, transform, and secure PDFs: merging, page manipulation, form filling, watermarks, encryption, text and table extraction.

## Tooling

- `pypdf` for merge, split, rotate, watermark, encrypt.
- `pdfplumber` for text and table extraction.
- `reportlab` for creating PDFs.
- `qpdf` for command-line merge, split, decrypt.
- `pdftotext` / `pdftoppm` / `pdfimages` (poppler) for text, page images, image extraction.

## Quick reference

| Task | Tool |
|---|---|
| Merge / split / rotate | `pypdf` (or `qpdf` on the CLI) |
| Extract text / tables | `pdfplumber` |
| Create | `reportlab` |
| Watermark | `pypdf` `merge_page` |
| Password-protect | `pypdf` `encrypt` |
| Fill forms | separate form workflow |
| Edit existing text | natural-language edit skill |

## Common operations

Merge:

```python
from pypdf import PdfReader, PdfWriter
writer = PdfWriter()
for f in ["a.pdf", "b.pdf"]:
    for page in PdfReader(f).pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as fh:
    writer.write(fh)
```

Split one page per file:

```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    w = PdfWriter(); w.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as fh:
        w.write(fh)
```

Extract text and tables:

```python
import pdfplumber, pandas as pd
with pdfplumber.open("doc.pdf") as pdf:
    text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    tables = [pd.DataFrame(t[1:], columns=t[0])
              for p in pdf.pages for t in p.extract_tables() if t]
```

Create:

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
doc = SimpleDocTemplate("report.pdf", pagesize=letter)
doc.build([Paragraph("Title", getSampleStyleSheet()["Title"])])
```

Subscript and superscript: never use Unicode sub/superscript characters; the built-in fonts lack the glyphs. Use `<sub>` and `<super>` inside Paragraph objects.

Command line:

```bash
pdftotext -layout in.pdf out.txt
qpdf --empty --pages a.pdf b.pdf -- merged.pdf
qpdf in.pdf --pages . 1-5 -- pages1-5.pdf
qpdf --password=pw --decrypt enc.pdf out.pdf
pdfimages -j in.pdf img
```

Watermark: read the watermark page, then `page.merge_page(watermark)` over each page.

Encrypt: `writer.encrypt("userpass", "ownerpass")`.

## Form filling

Read the form workflow reference before starting. Separate fillable (AcroForm) PDFs from flat scanned forms:

- Check whether the PDF has fillable fields first.
- Enumerate fields, fill fillable fields directly, or overlay text on flat forms.
- Verify placement with a rendered image before delivering.

## Pitfalls

- `extract_text()` returns `None` on image-only pages. Guard with `or ""` and fall back to OCR.
- Encrypted PDFs need the password before pages are readable.
- reportlab coordinates are bottom-left origin, in points (1/72 inch), not top-left.
- When overlaying text on a flat form, render a validation image and check placement before delivering.

## Verify

1. Open the output and assert the expected page count.
2. Re-extract text and confirm the added content is present.
3. For anything visual, render pages to images and inspect.