---
name: pdf
description: Use this skill whenever the user wants to convert PDFs to Markdown, extract content from PDFs, or process PDF documents for use with LLMs, agents, or text pipelines. This includes PDF-to-Markdown conversion (use the four-tool decision tree), extracting text, tables, or images from PDFs, batch processing PDF collections, and handling both text-layer and scanned PDFs. Always use this skill when the user mentions PDF, document conversion, extracting content from a document, or preparing documents for AI/RAG pipelines — even if they don't use the word "PDF" explicitly.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF → Markdown Guide

## Core Principle

PDF → Markdown is the primary goal. Once you have Markdown, downstream processing — agents, RAG pipelines, search indexing, summarization — becomes straightforward. Text extraction, table extraction, and OCR are all means to that end.

## Tool Selection

Pick the right tool before writing any code:

| Situation | Tool | Why |
|-----------|------|-----|
| Text-layer PDF, fast result needed, **no images** | **markitdown** | Zero models, instant — but image extraction not supported |
| General-purpose, enterprise, RAG pipeline | **docling** | MIT, LangChain/LlamaIndex-ready, CPU-capable, image export |
| Books, papers, high-accuracy needed | **marker** | ML layout detection, GPU preferred, image export |
| Scientific PDFs with formulas/tables, scanned | **MinerU** | Deepest model stack, 109-language OCR, outputs `images/` natively |
| Scanned PDF, no GPU available | **docling** + tesseract | OCR backend configurable without GPU |

**Image extraction support:**

| Tool | 擷取圖片 | 輸出位置 | Markdown 語法 |
|------|---------|---------|--------------|
| markitdown | ❌ 不支援 | — | — |
| docling | ✅ | 需手動指定 `images/` | `![](images/name.png)` |
| marker | ✅ | 預設散落在輸出目錄，需整理 | `![](images/name.png)` |
| MinerU | ✅ | 原生輸出 `images/` | `![](images/name.png)` |

**重要**：如果 PDF 包含需要保留的圖片，markitdown 無法使用，請選 docling / marker / MinerU。

**Table → Markdown 轉換可靠度：**

| Tool | 表格轉換 | 說明 |
|------|---------|------|
| markitdown | ⚠️ 不可靠 | 表格常輸出為縮排文字，不是 `\|col\|` 語法 |
| docling | ✅ 最穩定 | 內建 TableFormer 模型，專為結構化表格設計 |
| marker | ✅ 良好 | 版面偵測可識別表格，複雜合併儲存格偶有誤差 |
| MinerU | ✅ 良好 | 科學論文表格最佳，一般文件亦可 |

**重要**：如果 PDF 包含需要保留的表格，markitdown 不可靠，請選 docling（首選）/ marker / MinerU。

**Quick check — text-layer or scanned?**
```python
from markitdown import MarkItDown
result = MarkItDown().convert("file.pdf")
is_scanned = len(result.text_content.strip()) < 100
print("Scanned PDF" if is_scanned else "Text-layer PDF")
```

If scanned → use docling, marker, or MinerU (all have built-in OCR).

**Quick check — available VRAM:**
```python
import subprocess

def get_vram_gb() -> float:
    """Return available VRAM in GB. Returns 0 if no NVIDIA GPU found."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            text=True
        )
        mb = int(out.strip().splitlines()[0])
        return mb / 1024
    except Exception:
        return 0.0

vram = get_vram_gb()

if vram >= 8:
    print(f"✅ {vram:.1f} GB — marker GPU / MinerU GPU both available")
elif vram >= 4:
    print(f"⚠️  {vram:.1f} GB — marker GPU ok; MinerU use CPU mode")
elif vram > 0:
    print(f"❌ {vram:.1f} GB — insufficient VRAM; marker/MinerU use CPU mode")
else:
    print("❌ No NVIDIA GPU detected — use docling (preferred) or CPU mode for marker/MinerU")
```

VRAM 與建議模式對照：

| VRAM | marker | MinerU | 建議 |
|------|--------|--------|------|
| ≥ 8 GB | GPU ✅ | GPU ✅ | 全速，四工具任選 |
| 4-7 GB | GPU ✅ | CPU 模式 ⚠️ | marker GPU / MinerU `--backend pipeline` |
| 1-3 GB（如 MX330 2 GB） | CPU 模式 ⚠️ | CPU 模式 ⚠️ | 優先 docling；marker/MinerU 可跑但慢 |
| 無 GPU | CPU 模式 ⚠️ | CPU 模式 ⚠️ | 優先 docling |

---

## Environment Setup (Ubuntu / WSL)

```bash
# System dependencies
sudo apt install -y poppler-utils tesseract-ocr fonts-noto-cjk
sudo apt install -y tesseract-ocr-chi-tra tesseract-ocr-chi-sim  # CJK OCR

# Python packages — install only what you need
uv pip install 'markitdown[pdf]'   # lightweight
uv pip install docling              # enterprise-grade
uv pip install marker-pdf           # ML-based, high accuracy
uv pip install 'mineru[all]'        # heavy, scientific docs
```

---

## Tool 1: markitdown (Microsoft)

**Best for**: Text-layer PDFs where images are not needed.
**Requires**: No GPU, no model downloads.
**Limitation — images**: markitdown does **not** extract images. If the PDF contains figures, charts, or diagrams that must be preserved, use docling / marker / MinerU instead.
**Limitation — scanned**: Returns empty/garbled output on scanned PDFs — detect and fall back.

```bash
uv pip install 'markitdown[pdf]'
markitdown document.pdf -o document.md
```

```python
from markitdown import MarkItDown
from pathlib import Path

# Single file
result = MarkItDown().convert("document.pdf")
Path("document.md").write_text(result.text_content, encoding="utf-8")

# Batch with scanned-PDF guard
md = MarkItDown()
for pdf in Path(".").glob("*.pdf"):
    result = md.convert(str(pdf))
    if result.text_content.strip():
        pdf.with_suffix(".md").write_text(result.text_content, encoding="utf-8")
    else:
        print(f"WARNING: {pdf.name} appears scanned — use docling/marker/MinerU")
```

---

## Tool 2: docling (IBM / Linux Foundation)

**Best for**: General enterprise use, RAG pipelines, 表格轉換最可靠。
**Requires**: CPU-capable (GPU accelerates). MIT license.
**Handles**: Scanned PDFs via OCR, tables (TableFormer model), reading order, layout detection, image extraction.

```bash
uv pip install docling

# CLI — TableFormer 預設啟用，直接使用即可
docling document.pdf --image-export-mode referenced   # outputs document.md + images/
docling ./pdf_folder/ --to md --image-export-mode referenced  # batch
```

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem
from pathlib import Path
import json

# 明確啟用 TableFormer（預設已啟用，此處為顯式確認）
pipeline_options = PdfPipelineOptions(
    do_table_structure=True,        # 啟用表格結構辨識
    table_structure_options={"do_cell_matching": True},  # 確保儲存格對齊
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

# Export Markdown — 表格輸出為 | col | col | 語法，圖片指向 images/
md = result.document.export_to_markdown(image_mode=ImageRefMode.REFERENCED)

# Save each extracted image to images/
for item, _ in result.document.iterate_items():
    if isinstance(item, PictureItem) and item.image and item.image.pil_image:
        img_name = item.self_ref.replace("/", "_").strip("_") + ".png"
        item.image.pil_image.save(img_dir / img_name)

(out_dir / "document.md").write_text(md, encoding="utf-8")

# JSON (preserves structure metadata — useful for agents)
Path(out_dir / "document.json").write_text(
    json.dumps(result.document.export_to_dict(), ensure_ascii=False, indent=2),
    encoding="utf-8"
)
```

**LangChain / LlamaIndex integration:**
```python
# LangChain
from langchain_community.document_loaders import DoclingLoader
docs = DoclingLoader("document.pdf").load()

# LlamaIndex
from llama_index.readers.docling import DoclingReader
documents = DoclingReader().load_data("document.pdf")
```

---

## Tool 3: marker (datalab-to)

**Best for**: Books, academic papers, documents needing high layout accuracy.
**Requires**: PyTorch. GPU strongly recommended (~4-5 GB VRAM). CPU mode available but slow.
**License**: GPL-3.0. Model weights: cc-by-nc-sa-4.0 (check commercial use restrictions).
**Images**: marker extracts images and references them in Markdown. Use the normalizer below to ensure they land in `images/`.

```bash
uv pip install marker-pdf

# Single file — images output to output_dir/document/images/
marker_single document.pdf output_dir/

# Batch with GPU
NUM_DEVICES=1 NUM_WORKERS=2 marker_chunk_convert ./pdf_in/ ./md_out/
```

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from pathlib import Path
import re, shutil

def convert_with_marker(pdf_path: str, out_dir: str) -> Path:
    """Convert PDF with marker; normalise image paths to images/ subfolder."""
    out = Path(out_dir)
    img_dir = out / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(pdf_path)
    text, _, images = text_from_rendered(rendered)

    # Save images to images/ and rewrite references in Markdown
    for img_name, pil_img in (images or {}).items():
        dest = img_dir / Path(img_name).name
        pil_img.save(dest)
        # rewrite any path prefix → images/filename
        text = text.replace(img_name, f"images/{dest.name}")

    # Ensure any remaining bare filenames are prefixed with images/
    text = re.sub(r'!\[([^\]]*)\]\((?!images/)([^)]+\.(?:png|jpg|jpeg|webp))\)',
                  r'![\1](images/\2)', text)

    md_path = out / (Path(pdf_path).stem + ".md")
    md_path.write_text(text, encoding="utf-8")
    return md_path

md_path = convert_with_marker("document.pdf", "output/")
```

**Troubleshooting:**
```bash
# Garbled text → force OCR
marker_single document.pdf output_dir/ --force_ocr

# Use LLM for better quality (requires GOOGLE_API_KEY)
marker_single document.pdf output_dir/ --use_llm

# Force CPU (VRAM < 4 GB)
TORCH_DEVICE=cpu marker_single document.pdf output_dir/
```

---

## Tool 4: MinerU (opendatalab)

**Best for**: Scientific papers with formulas, complex multi-column layouts, 109-language OCR.
**Requires**: Python 3.10-3.13. GPU recommended (8 GB+ VRAM). CPU via `--backend pipeline`.
**License**: AGPL-3.0.
**Images**: MinerU natively outputs images to `images/` and references them with `![](images/filename.png)` in Markdown — no post-processing needed.

```bash
uv pip install 'mineru[all]'
mineru-models-download          # first run: downloads ~5 GB of models

# GPU (auto-detected) — produces output_dir/document.md + output_dir/images/
mineru -p document.pdf -o output_dir/

# CPU only (VRAM < 8 GB)
mineru -p document.pdf -o output_dir/ --backend pipeline

# Batch
mineru -p ./pdf_folder/ -o output_dir/
```

```python
from mineru.cli.common import do_parse
from pathlib import Path

do_parse(pdf_path="document.pdf", output_dir="output_dir/")
# CPU: add backend="pipeline"

# Images already in output_dir/images/, references already correct
md = Path("output_dir/document.md").read_text(encoding="utf-8")
```

---

## Lightweight Converter (No ML Models)

**適用**：有文字層的 PDF，需要圖片保留位置，不想安裝 ML 模型。
**不適用**：掃描版 PDF（入口處自動偵測並拒絕，提示改用 docling/marker/MinerU）。
**依賴**：`pdfplumber`, `pypdf`, `Pillow`（選用 `markitdown` 做掃描偵測）

```bash
uv pip install pdfplumber pypdf Pillow 'markitdown[pdf]'
```

核心腳本 `pdf_to_md.py`（下載後直接使用）：

```python
# 基本用法
from pdf_to_md import pdf_to_markdown, verify

md_path = pdf_to_markdown("document.pdf", "output/")
print(verify(str(md_path)))
# {"tables": 3, "images": 5, "warnings": 0}
```

```bash
# CLI 單檔
python pdf_to_md.py document.pdf -o output/

# CLI 批次
python pdf_to_md.py ./pdf_folder/ -o output/ --batch
```

**輸出結構：**
```
output/
├── document.md        ← 文字 + | 表格 | + ![](images/...)
└── images/
    ├── page1_img1.png
    └── page2_img1.png
```

**機制：**
- 文字：pdfplumber 按 y 座標分段，排除表格區域避免重複
- 表格：pdfplumber `find_tables()` → `| col |` 語法，按 y 座標插入正確位置
- 圖片：pypdf 擷取點陣圖 → `images/`，追加在所屬頁尾
- 向量圖：無法擷取時輸出 `<!-- WARNING -->` 而非靜默跳過
- 多欄版面：自動偵測並加 `<!-- NOTE -->` 提醒人工確認順序

---



```
PDF received
│
├─ 需要保留圖片？
│   ├─ YES → 跳過 markitdown，直接往下
│   └─ NO  → markitdown 可用（速度最快，無圖無表）
│
├─ 需要表格轉換為 Markdown？
│   └─ YES → docling（TableFormer，最可靠）
│             marker / MinerU 亦可，但複雜表格建議 docling
│
├─ Text-layer，需要圖片，不想裝 ML 模型？
│   └─ YES → pdf_to_md.py（Lightweight Converter）
│
├─ Text-layer? (quick check above)
│   ├─ YES, just need text fast       → markitdown（無圖無表需求時）
│   └─ YES, need structure/tables/RAG → docling
│
└─ Scanned / image-only?
    ├─ General doc                    → docling (tesseract backend, no GPU needed)
    ├─ Books / papers, high accuracy
    │   ├─ VRAM ≥ 4 GB               → marker GPU mode
    │   └─ VRAM < 4 GB               → marker CPU mode (TORCH_DEVICE=cpu), 慢
    └─ Scientific formulas / complex
        ├─ VRAM ≥ 8 GB               → MinerU GPU mode
        └─ VRAM < 8 GB               → MinerU CPU mode (--backend pipeline), 慢

轉換後 → 執行 verify_tables() 確認表格語法正確
         如失敗 → pdfplumber fallback
```

| Feature | markitdown | docling | marker | MinerU |
|---------|-----------|---------|--------|--------|
| Text-layer PDF | ✅ | ✅ | ✅ | ✅ |
| Scanned PDF (OCR) | ❌ | ✅ | ✅ | ✅ |
| Image extraction | ❌ | ✅ | ✅ | ✅ |
| Image → `images/` folder | ❌ | ✅ 需設定 | ✅ 需整理 | ✅ 原生 |
| Table → Markdown | ⚠️ basic | ✅ | ✅ | ✅ |
| Formula (LaTeX) | ❌ | ⚠️ partial | ✅ | ✅ |
| GPU required | ❌ | ❌ | Recommended | Recommended |
| Install size | Small | Medium | Large | Very large |
| License | MIT | MIT | GPL-3.0* | AGPL-3.0 |
| LangChain / LlamaIndex | ❌ | ✅ native | ❌ | ❌ |

*marker model weights are cc-by-nc-sa-4.0 — verify commercial use rights before deploying.

---

## Table Verification & Fallback

轉換後務必驗證表格是否正確輸出為 Markdown 語法。

```python
import re
from pathlib import Path

def verify_tables(md_path: str) -> dict:
    """Check converted Markdown for proper table syntax."""
    text = Path(md_path).read_text(encoding="utf-8")

    # Markdown table 特徵：含有 | 的行，且下一行是分隔線 |---|
    table_blocks = re.findall(
        r'(\|.+\|\n\|[-| :]+\|\n(?:\|.+\|\n?)*)',
        text
    )

    # 偵測可能未轉換的表格殘跡（連續多行都有空格對齊）
    suspicious = re.findall(r'(?m)^[ \t]+\S.*\n(?:[ \t]+\S.*\n){3,}', text)

    return {
        "markdown_tables_found": len(table_blocks),
        "suspicious_plaintext_tables": len(suspicious),
        "ok": len(table_blocks) > 0 or len(suspicious) == 0,
    }

result = verify_tables("output/document.md")
print(result)
# {"markdown_tables_found": 3, "suspicious_plaintext_tables": 0, "ok": True}
```

**如果 `markdown_tables_found` 為 0 但 PDF 明確有表格 → 使用 pdfplumber 補救：**

```python
import pdfplumber
import re
from pathlib import Path

def pdfplumber_tables_to_md(pdf_path: str) -> str:
    """Extract all tables from PDF as Markdown using pdfplumber."""
    tables_md = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            for j, table in enumerate(page.extract_tables(), 1):
                if not table or not table[0]:
                    continue
                # 清理 None 值
                clean = [
                    [cell or "" for cell in row]
                    for row in table
                ]
                # 第一列為 header
                header = "| " + " | ".join(clean[0]) + " |"
                separator = "| " + " | ".join(["---"] * len(clean[0])) + " |"
                rows = ["| " + " | ".join(row) + " |" for row in clean[1:]]
                tables_md.append(
                    f"<!-- Table: page {i}, table {j} -->\n"
                    + "\n".join([header, separator] + rows)
                )
    return "\n\n".join(tables_md)

# 直接輸出所有表格
print(pdfplumber_tables_to_md("document.pdf"))

# 或注入到已有的 Markdown 尾端
md = Path("output/document.md").read_text(encoding="utf-8")
tables = pdfplumber_tables_to_md("document.pdf")
if tables:
    Path("output/document.md").write_text(
        md + "\n\n---\n\n## Extracted Tables\n\n" + tables,
        encoding="utf-8"
    )
```

---

```python
from pathlib import Path

md_text = Path("document.md").read_text(encoding="utf-8")

# Chunk for RAG
from langchain.text_splitter import MarkdownTextSplitter
chunks = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100).split_text(md_text)

# Summarize via Claude
import anthropic
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Summarize:\n\n{md_text[:8000]}"}]
)
print(message.content[0].text)
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Text-layer PDF → MD (fast, no tables/images) | `MarkItDown().convert("f.pdf").text_content` |
| PDF with tables → MD (最可靠) | `docling f.pdf` |
| High-accuracy PDF → MD | `marker_single f.pdf out/` |
| Scientific PDF → MD | `mineru -p f.pdf -o out/` |
| Scanned, no GPU | `docling f.pdf` |
| Batch convert | `docling ./folder/ --to md` |
| Check if scanned | `len(MarkItDown().convert("f.pdf").text_content.strip()) < 100` |
| Verify tables converted | `verify_tables("output/document.md")` |
| Fallback table extraction | `pdfplumber_tables_to_md("document.pdf")` |