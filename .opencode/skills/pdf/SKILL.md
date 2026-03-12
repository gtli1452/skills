---
name: pdf
description: Use this skill whenever the user wants to convert a PDF to Markdown, extract text, tables, or images from a PDF, or prepare PDF content for LLM, RAG, or text pipelines. Trigger on any mention of PDF conversion, document extraction, or PDF processing — even if the user does not say "PDF" explicitly. This skill covers text-layer and scanned PDFs, single files and batch runs.
---

# PDF to Markdown

Convert PDF documents into clean Markdown that preserves structure, tables, and image references. Every other downstream use — RAG chunking, summarization, search indexing — starts from good Markdown.

## Fidelity Warning

Markdown cannot represent every PDF layout. When you encounter any of the following, insert an HTML comment warning and tell the user:

- **Multi-column layouts** — reading order may be wrong. Add `<!-- WARNING: multi-column layout detected; verify reading order -->`.
- **Nested or merged table cells** — Markdown tables are flat grids. Add `<!-- WARNING: merged cells simplified; verify table accuracy -->`.
- **Overlapping text/image regions** — positional fidelity is lost. Add `<!-- WARNING: overlapping elements; layout approximated -->`.
- **Vector diagrams / annotations** — not extractable as raster images. Add `<!-- WARNING: vector graphic on page N could not be extracted -->`.

Never silently drop content. If extraction is partial, warn explicitly.

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
│   │       │           │   └─ YES → lightweight script (pdfplumber + pypdf)
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
└─ Post-conversion → run verify_tables(); warn user on failure
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

**When to use**: text-layer PDFs where you need tables and images but want to avoid installing ML model weights. Uses `pdfplumber` for text and tables, `pypdf` + `Pillow` for raster image extraction.

**Not suitable for**: scanned PDFs (no OCR). Detect and refuse early.

```bash
uv pip install pdfplumber pypdf Pillow
```

Output structure:
```
output/
├── document.md        # text + | table | + ![](images/...)
└── images/
    ├── page1_img1.png
    └── page2_img1.png
```

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

## Post-Conversion: Table Verification

Always verify that tables converted correctly. If `markdown_tables_found` is 0 but the PDF visibly contains tables, fall back to pdfplumber extraction.

```python
import re
from pathlib import Path

def verify_tables(md_path: str) -> dict:
    text = Path(md_path).read_text(encoding="utf-8")
    table_blocks = re.findall(
        r'(\|.+\|\n\|[-| :]+\|\n(?:\|.+\|\n?)*)', text
    )
    suspicious = re.findall(r'(?m)^[ \t]+\S.*\n(?:[ \t]+\S.*\n){3,}', text)
    return {
        "markdown_tables_found": len(table_blocks),
        "suspicious_plaintext_tables": len(suspicious),
        "ok": len(table_blocks) > 0 or len(suspicious) == 0,
    }
```

If verification fails, extract tables with pdfplumber and append them:

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

## Quick Reference

| Task | Command / Call |
|------|---------------|
| Text-only, fast | `markitdown doc.pdf -o doc.md` |
| General / tables / images | `docling doc.pdf --image-export-mode referenced` |
| Text-layer, no ML models | lightweight script (pdfplumber + pypdf) |
| High-accuracy books/papers | `marker_single doc.pdf out/` |
| Scientific / formulas | `mineru -p doc.pdf -o out/` |
| Scanned, no GPU | `docling doc.pdf` (tesseract backend) |
| Batch convert | `docling ./folder/ --to md --image-export-mode referenced` |
| Verify tables | `verify_tables("output/doc.md")` |
| Fallback table extraction | `pdfplumber_tables_to_md("doc.pdf")` |