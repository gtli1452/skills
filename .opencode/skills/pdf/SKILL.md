---
name: pdf
description: Use this skill whenever the user wants to convert a PDF to Markdown, extract text, tables, or images from a PDF, or prepare PDF content for LLM, RAG, or text pipelines. Trigger on any mention of PDF conversion, document extraction, or PDF processing — even if the user does not say "PDF" explicitly. This skill covers text-layer and scanned PDFs, single files and batch runs.
---

# PDF to Markdown

Convert PDF documents into clean Markdown that preserves structure, tables, and image references. Every other downstream use — RAG chunking, summarization, search indexing — starts from good Markdown.

## Acceptance Criteria (Quality Gates)

Every conversion must be checked against these gates before delivery.

### Headings
- Real section headings in the PDF are promoted to `#` / `##` / `###` — never left as bold text or unstyled lines.
- Heading hierarchy reflects the logical outline (chapter > section > subsection).
- **Precision over recall**: lines >80 chars or full sentences are NOT promoted even if bold/large.
- Cross-reference sentences ("See Section …", "Refer to Appendix …", "for more details") are **never** headings.
- Legal / disclaimer prose ("provided as-is", "without warranty", "all rights reserved") is **never** a heading.

### Tables
- Every table renders as `| col |` pipe syntax with header separator.
- Merged / spanning cells are normalized to equal column count. A `<!-- WARNING: merged/spanning cells normalized; verify table accuracy -->` comment is emitted above affected tables.
- Sparse spanning rows (sub-headers / note rows where most cells are empty) are preserved, not dropped. Each such row carries an inline `<!-- spanning row -->` marker.
- If initial conversion misses tables, a pdfplumber fallback extraction is attempted.

### Images
- Raster images are extracted to `images/` and referenced with `![](images/…)`.
- **Placement**: PyMuPDF (fitz) provides bounding-box data for images, so images are placed at their approximate vertical position within the page text. When bounding-box data is unavailable, images fall back to the end of the page.
- Vector diagrams / annotations that cannot be rasterized produce a `<!-- WARNING: vector graphic on page N could not be extracted -->` comment.

### Warnings — Never Drop Content Silently
When fidelity is limited, insert an HTML comment **and** tell the user:

| Condition | Warning comment |
|---|---|
| Multi-column layout | `<!-- NOTE: page N may have multi-column layout; reading order may need manual verification -->` |
| Merged / spanning cells | `<!-- WARNING: merged/spanning cells normalized; verify table accuracy -->` |
| Overlapping text / image | `<!-- WARNING: overlapping elements; layout approximated -->` |
| Vector graphic not extractable | `<!-- WARNING: vector graphic on page N could not be extracted -->` |
| Wide table (≥8 cols) | `<!-- NOTE: wide table (N cols); formatting may be approximate -->` |

---

## Tool Decision Tree

Pick the right tool **before** writing any code. Default to **docling** when uncertain.

```
PDF received
│
├─ Text-layer? (quick-check: markitdown output length > 100 chars)
│   │
│   ├─ YES ─┬─ Need tables or images?
│   │       │   ├─ NO  → markitdown  (instant, zero models)
│   │       │   └─ YES ─┬─ Want to avoid ML models?
│   │       │           │   └─ YES → lightweight script (pdfplumber + PyMuPDF)
│   │       │           └─ NO  → docling  (best tables, image export, MIT)
│   │       │
│   │       └─ Need structure + RAG integration?
│   │           └─ YES → docling  (LangChain / LlamaIndex native)
│   │
│   └─ NO (scanned / image-only)
│       ├─ General document         → docling + tesseract (no GPU needed)
│       ├─ Books / papers           → marker  (GPU preferred, ≥ 4 GB VRAM)
│       └─ Scientific / formulas    → MinerU  (GPU preferred, ≥ 8 GB VRAM)
│
└─ Post-conversion → run verify() or verify_tables(); warn user on failure
```

### Comparison Matrix

| Feature | markitdown | Lightweight script | docling | marker | MinerU |
|---|---|---|---|---|---|
| Text-layer PDF | ✅ | ✅ | ✅ | ✅ | ✅ |
| Scanned PDF (OCR) | ❌ | ❌ | ✅ | ✅ | ✅ |
| Table → Markdown | ⚠️ unreliable | ✅ pdfplumber | ✅ TableFormer | ✅ good | ✅ good |
| Image extraction | ❌ | ✅ raster only | ✅ | ✅ | ✅ native |
| Formula (LaTeX) | ❌ | ❌ | ⚠️ partial | ✅ | ✅ |
| GPU required | No | No | No | Recommended | Recommended |
| Install size | Small | Small | Medium | Large | Very large |
| License | MIT | MIT deps | MIT | GPL-3.0 | AGPL-3.0 |

> **marker** model weights are cc-by-nc-sa-4.0 — verify commercial-use rights before deploying.

---

## 1 · markitdown — Fast Lightweight Path

**When to use**: text-layer PDFs where you need only prose text, no tables or images.
**Limitations**: does **not** extract images; tables often render as indented text instead of `| col |` syntax; returns empty output on scanned PDFs.

```bash
uv pip install 'markitdown[pdf]'
markitdown document.pdf -o document.md
```

```python
from markitdown import MarkItDown
from pathlib import Path

result = MarkItDown().convert("document.pdf")
if len(result.text_content.strip()) < 100:
    print("WARNING: appears scanned — fall back to docling / marker / MinerU")
else:
    Path("document.md").write_text(result.text_content, encoding="utf-8")
```

---

## 2 · docling — Primary Engine (Recommended Default)

**When to use**: general-purpose conversion, enterprise pipelines, any PDF with tables. Best table fidelity (TableFormer model). Handles scanned PDFs via configurable OCR backend. MIT license, CPU-capable.

```bash
uv pip install docling
docling document.pdf --image-export-mode referenced   # → document.md + images/
docling ./pdf_folder/ --to md --image-export-mode referenced  # batch
```

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem
from pathlib import Path

pipeline_options = PdfPipelineOptions(
    do_table_structure=True,
    table_structure_options={"do_cell_matching": True},
)
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

out_dir = Path("output")
img_dir = out_dir / "images"
img_dir.mkdir(parents=True, exist_ok=True)

result = converter.convert("document.pdf")
md = result.document.export_to_markdown(image_mode=ImageRefMode.REFERENCED)

for item, _ in result.document.iterate_items():
    if isinstance(item, PictureItem) and item.image and item.image.pil_image:
        img_name = item.self_ref.replace("/", "_").strip("_") + ".png"
        item.image.pil_image.save(img_dir / img_name)

(out_dir / "document.md").write_text(md, encoding="utf-8")
```

---

## 3 · Lightweight Script — No ML Models

**When to use**: text-layer PDFs where you need tables and images but want to avoid installing ML model weights. Uses `pdfplumber` for text and tables, `PyMuPDF` (fitz) + `Pillow` for raster image extraction.

**Not suitable for**: scanned PDFs (no OCR). Detect and refuse early.

```bash
uv pip install pdfplumber PyMuPDF Pillow
```

Output structure:
```
output/
├── document.md        # text + | table | + ![](images/...)
└── images/
    ├── page1_img1.png
    └── page2_img1.png
```

Quality targets (iterations 1–3):
- **Heading promotion — precision over recall**: Detect PDF text styled as section headings (large/bold font, outline entries) and emit Markdown heading syntax (`#`, `##`, `###`). Never leave real headings as plain bold text or unstyled lines. **Iteration-2 rule**: Do **not** promote a line to a heading if it exceeds ~80 characters or reads as a full sentence/clause of body text. Long prose lines that happen to be bold or large are almost always emphasis within a paragraph, not structural headings. When in doubt, leave the line as bold (`**text**`) rather than risk a false-positive heading. **Iteration-3 additions**:
  - **Cross-reference sentences**: Lines containing phrases like "See Section …", "Refer to Appendix …", "as described in …", "in accordance with …", or "for more details/information" must **never** be promoted to headings regardless of font size or boldness. These are navigational prose, not structural headings.
  - **Legal / disclaimer prose**: Lines containing boilerplate legal language ("provided as-is", "without warranty", "all rights reserved", "disclaimer", "subject to the terms", "no liability", "governing law", "to the fullest extent", "warranty of merchantability") must **not** be promoted to headings. These blocks are often rendered in bold or larger font for emphasis but are body content.
- **Merged/spanning table normalization**: When `pdfplumber` reports cells that span multiple rows or columns, normalize them so every Markdown row has equal column count. Repeat the spanned value into each covered cell, or insert empty cells, and add a `<!-- WARNING: merged/spanning cells normalized; verify table accuracy -->` comment above the table.
- **Sparse spanning rows (iteration 2)**: Tables sometimes contain continuation rows where most cells are empty and a single cell spans the full width (e.g., a sub-header or note row). Preserve these rows in the Markdown table with the content in the correct column and empty cells for the rest — do not collapse or drop them. Mark such rows with an inline comment `<!-- spanning row -->` so downstream consumers can identify them.

Key behaviors:
- Text is segmented by vertical position; table regions are excluded to avoid duplication.
- Tables are extracted with `pdfplumber.find_tables()` and rendered as `| col |` Markdown, inserted at the correct vertical position.
- Raster images are saved to `images/` and referenced with `![](images/...)`.
- Vector graphics that cannot be rasterized produce a `<!-- WARNING: vector graphic ... -->` comment.
- Multi-column layouts are flagged with `<!-- NOTE: multi-column detected; verify reading order -->`.

---

## 4 · marker — Optional Advanced (High Accuracy)

**When to use**: books, academic papers, or documents where ML-based layout detection yields noticeably better results than docling. GPU strongly recommended (~4–5 GB VRAM); CPU mode works but is slow.

**Trade-offs**: GPL-3.0 license; model weights are cc-by-nc-sa-4.0 (non-commercial). Larger install footprint than docling.

```bash
uv pip install marker-pdf
marker_single document.pdf output_dir/
```

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from pathlib import Path
import re

def convert_with_marker(pdf_path: str, out_dir: str) -> Path:
    out = Path(out_dir)
    img_dir = out / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(pdf_path)
    text, _, images = text_from_rendered(rendered)

    for img_name, pil_img in (images or {}).items():
        dest = img_dir / Path(img_name).name
        pil_img.save(dest)
        text = text.replace(img_name, f"images/{dest.name}")

    # Normalise any remaining bare image references
    text = re.sub(
        r'!\[([^\]]*)\]\((?!images/)([^)]+\.(?:png|jpg|jpeg|webp))\)',
        r'![\1](images/\2)', text,
    )
    md_path = out / (Path(pdf_path).stem + ".md")
    md_path.write_text(text, encoding="utf-8")
    return md_path
```

Troubleshooting:
```bash
marker_single document.pdf out/ --force_ocr         # garbled text → force OCR
TORCH_DEVICE=cpu marker_single document.pdf out/     # no GPU
```

---

## 5 · MinerU — Optional Advanced (Scientific)

**When to use**: scientific papers with LaTeX formulas, complex multi-column layouts, or 109-language OCR needs. GPU recommended (≥ 8 GB VRAM); CPU via `--backend pipeline`.

**Trade-offs**: AGPL-3.0 license; ~5 GB model download on first run; heaviest install of all options.

**Images**: MinerU natively outputs to `images/` with correct Markdown references — no post-processing.

```bash
uv pip install 'mineru[all]'
mineru-models-download
mineru -p document.pdf -o output_dir/                     # GPU auto-detected
mineru -p document.pdf -o output_dir/ --backend pipeline  # CPU fallback
```

---

## Post-Conversion: Verification

Always verify that conversion produced faithful output. The lightweight script exposes `verify()` (aliased as `verify_tables()` for backward compatibility):

```python
from pdf_to_md import verify

stats = verify("output/document.md")
# Returns: {"tables": N, "images": N, "warnings": N,
#           "suspicious_plaintext_tables": N, "ok": bool}
```

If `tables` is 0 but the PDF visibly contains tables, fall back to pdfplumber extraction:

```python
import pdfplumber

def pdfplumber_tables_to_md(pdf_path: str) -> str:
    tables_md = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            for j, table in enumerate(page.extract_tables(), 1):
                if not table or not table[0]:
                    continue
                clean = [[cell or "" for cell in row] for row in table]
                header = "| " + " | ".join(clean[0]) + " |"
                sep = "| " + " | ".join(["---"] * len(clean[0])) + " |"
                rows = ["| " + " | ".join(r) + " |" for r in clean[1:]]
                tables_md.append(
                    f"<!-- Table: page {i}, table {j} -->\n"
                    + "\n".join([header, sep] + rows)
                )
    return "\n\n".join(tables_md)
```

---

## Iterative Testing Workflow

The skill ships with a batch eval harness (`scripts/run_evals.py`) that converts every PDF listed in `evals/evals.json` and prints a summary table.

```bash
# Install lightweight-script dependencies
pip install -r scripts/requirements.txt

# Run all evals (from .opencode/skills/pdf/)
python scripts/run_evals.py

# Explicit repo root (if not auto-detected)
python scripts/run_evals.py --repo-root /path/to/eval-skills

# Custom output directory
python scripts/run_evals.py -o tmp/eval_output
```

**Iteration loop** (repeat until all gates pass):
1. Run `python scripts/run_evals.py` — review summary table.
2. For each failing PDF, open the generated `.md` and check against the acceptance criteria above.
3. Adjust `scripts/pdf_to_md.py` thresholds or logic.
4. Re-run. Commit when the summary shows all green.

---

## Quick Reference

| Task | Command / Call |
|------|---------------|
| Text-only, fast | `markitdown doc.pdf -o doc.md` |
| General / tables / images | `docling doc.pdf --image-export-mode referenced` |
| Text-layer, no ML models | lightweight script (pdfplumber + PyMuPDF) |
| High-accuracy books/papers | `marker_single doc.pdf out/` |
| Scientific / formulas | `mineru -p doc.pdf -o out/` |
| Scanned, no GPU | `docling doc.pdf` (tesseract backend) |
| Batch convert | `docling ./folder/ --to md --image-export-mode referenced` |
| Verify output | `verify("output/doc.md")` or `verify_tables("output/doc.md")` |
| Fallback table extraction | `pdfplumber_tables_to_md("doc.pdf")` |
| Batch eval harness | `python scripts/run_evals.py` |