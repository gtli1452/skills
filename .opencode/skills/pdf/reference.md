# PDF-to-Markdown Advanced Reference

Supplementary techniques for the PDF-to-Markdown skill. See SKILL.md for the primary tool decision tree and standard workflows.

## pdfplumber Advanced Table Extraction

When the default `pdfplumber.find_tables()` misses tables or merges cells incorrectly, tune the extraction strategy:

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    # Custom settings for borderless or complex tables
    table_settings = {
        "vertical_strategy": "lines",    # or "text", "explicit"
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15,
    }
    tables = page.extract_tables(table_settings)

    # Visual debugging — renders detected lines/cells
    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

### Extracting Text by Region

Useful when a PDF mixes columns or sidebars and you need text from a specific bounding box:

```python
with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    # (left, top, right, bottom) in PDF points
    region_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

---

## Rendering Pages to Images (OCR Prep)

When a PDF has no text layer and you need to feed pages to an OCR engine:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("scanned.pdf")
for i, page in enumerate(pdf):
    bitmap = page.render(scale=2.0)  # 2× for better OCR accuracy
    bitmap.to_pil().save(f"page_{i+1}.png", "PNG")
```

Or via CLI with poppler-utils:

```bash
pdftoppm -png -r 300 document.pdf pages/page   # pages/page-01.png, …
```

---

## Extracting Embedded Images

When the Markdown output needs `![](images/...)` references and docling/marker are not available:

```bash
# List embedded images (no extraction)
pdfimages -list document.pdf

# Extract all images in original format
pdfimages -all document.pdf images/img
```

---

## Troubleshooting

### Encrypted PDFs

Conversion tools silently produce empty output on encrypted files. Decrypt first:

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
if reader.is_encrypted:
    reader.decrypt("password")  # then pass decrypted pages to converter
```

### Corrupted PDFs

If a converter crashes on a malformed file, repair the structure first:

```bash
qpdf --check document.pdf          # diagnose
qpdf --replace-input document.pdf  # in-place repair
```

### OCR Fallback for Scanned PDFs

If docling/marker/MinerU are unavailable, a minimal OCR pipeline:

```python
import pytesseract
from pdf2image import convert_from_path

def ocr_pdf_to_text(pdf_path: str) -> str:
    images = convert_from_path(pdf_path, dpi=300)
    return "\n\n".join(
        pytesseract.image_to_string(img) for img in images
    )
```

---

## Performance Tips

| Scenario | Recommendation |
|----------|---------------|
| Large PDF (100+ pages) | Process page-by-page; avoid loading entire document into memory |
| Text extraction only | `pdftotext` (poppler) is fastest; fall back to pdfplumber for tables |
| Image extraction | `pdfimages` is faster than rendering every page |
| Batch conversion | Use `docling ./folder/ --to md` for native batching |

---

## Library Licenses

| Library | License |
|---------|---------|
| pypdf | BSD |
| pdfplumber | MIT |
| pypdfium2 | Apache / BSD |
| poppler-utils | GPL-2.0 |
| qpdf | Apache-2.0 |
| pytesseract | Apache-2.0 |
| pdf2image | MIT |