"""
pdf_to_md.py — Lightweight PDF → Markdown converter
依賴：pdfplumber, pypdf, Pillow, markitdown

適用：有文字層的 PDF（非掃描版）。
不適用：整張 PDF 為掃描圖片 → 請改用 docling / marker / MinerU。

用法：
python pdf_to_md.py document.pdf -o output/
python pdf_to_md.py ./folder/ -o output/ -batch
"""

import io, re, argparse, shutil
from pathlib import Path

import pdfplumber
from pypdf import PdfReader
from PIL import Image

# ── 常數 ─────────────────────────────────────────────────────────────────────

MIN_TABLE_COLS   = 2
MIN_TABLE_ROWS   = 2
PARAGRAPH_GAP_PT = 8

# ── Scanned PDF 偵測（P3 修正）────────────────────────────────────────────────

def is_scanned(pdf_path: str) -> bool:
"""Return True if PDF has no meaningful text layer (likely scanned)."""
try:
from markitdown import MarkItDown
result = MarkItDown().convert(pdf_path)
return len(result.text_content.strip()) < 100
except ImportError:
# fallback: use pdfplumber
with pdfplumber.open(pdf_path) as pdf:
total = sum(len(p.extract_text() or "") for p in pdf.pages[:3])
return total < 100

# ── 圖片（P1 修正：使用 img_file.name / img_file.data）─────────────────────

def extract_page_images(reader: PdfReader, page_idx: int, img_dir: Path) -> list[str]:
refs = []
for j, img_file in enumerate(reader.pages[page_idx].images):
img_name = f"page{page_idx+1}_img{j+1}.png"
try:
pil = Image.open(io.BytesIO(img_file.data))
pil.save(img_dir / img_name, "PNG")
refs.append(f"![](images/{img_name})")
except Exception as e:
refs.append(f"<!-- WARNING: image '{img_file.name}' p{page_idx+1} skipped ({e}) -->")
return refs

# ── 表格 ──────────────────────────────────────────────────────────────────────

def extract_page_tables(page) -> list[dict]:
results = []
for tbl_obj in page.find_tables():
tbl = tbl_obj.extract()
if not tbl or len(tbl) < MIN_TABLE_ROWS or not tbl[0] or len(tbl[0]) < MIN_TABLE_COLS:
continue
clean     = [[c or "" for c in row] for row in tbl]
header    = "| " + " | ".join(clean[0]) + " |"
separator = "| " + " | ".join(["—"] * len(clean[0])) + " |"
rows      = ["| " + " | ".join(r) + " |" for r in clean[1:]]
results.append({
"y_top":   tbl_obj.bbox[1],
"bbox":    tbl_obj.bbox,
"content": "\n".join([header, separator] + rows),
})
return results

# ── 文字（排除表格區域）──────────────────────────────────────────────────────

def extract_page_text_blocks(page, table_bboxes: list) -> list[dict]:
words = page.extract_words(x_tolerance=2, y_tolerance=2)
lines: dict[float, list[str]] = {}
for w in words:
if any(w["x0"] >= b[0] and w["x1"] <= b[2] and
w["top"] >= b[1] and w["bottom"] <= b[3]
for b in table_bboxes):
continue
key = round(w["top"], 0)
lines.setdefault(key, []).append(w["text"])

```
sorted_ys = sorted(lines)
paragraphs, current, prev_y = [], [], None
for y in sorted_ys:
    if prev_y is not None and (y - prev_y) > PARAGRAPH_GAP_PT:
        if current:
            paragraphs.append({"y_top": prev_y, "content": " ".join(current)})
            current = []
    current.extend(lines[y])
    prev_y = y
if current and prev_y is not None:
    paragraphs.append({"y_top": prev_y, "content": " ".join(current)})
return paragraphs
```

# ── 多欄偵測 ──────────────────────────────────────────────────────────────────

def is_multicolumn(page) -> bool:
words = page.extract_words()
if len(words) < 20:
return False
mid   = page.width / 2
left  = sum(1 for w in words if w["x1"] < mid - 20)
right = sum(1 for w in words if w["x0"] > mid + 20)
return left > len(words) * 0.25 and right > len(words) * 0.25

# ── 頁面處理 ──────────────────────────────────────────────────────────────────

def process_page(reader: PdfReader, plumber_page, page_idx: int, img_dir: Path) -> str:
tables      = extract_page_tables(plumber_page)
tbl_bboxes  = [t["bbox"] for t in tables]
texts       = extract_page_text_blocks(plumber_page, tbl_bboxes)
images      = extract_page_images(reader, page_idx, img_dir)

```
all_blocks  = [(t["y_top"], t["content"]) for t in texts]
all_blocks += [(t["y_top"], t["content"]) for t in tables]
all_blocks.sort(key=lambda x: x[0])

ordered = [b[1] for b in all_blocks if b[1].strip()]
ordered += images  # 圖片追加在頁尾（pypdf 無可靠 bbox）

if is_multicolumn(plumber_page):
    ordered.insert(0, f"<!-- NOTE: page {page_idx+1} may have multi-column layout; verify order -->")

return "\n\n".join(ordered)
```

# ── 主函式 ───────────────────────────────────────────────────────────────────

def pdf_to_markdown(pdf_path: str, out_dir: str) -> Path:
"""
Convert a text-layer PDF to Markdown.
- Images saved to images/ as PNG, referenced with ![](images/name.png)
- Tables converted to | col | Markdown syntax
- Scanned PDFs rejected with clear error
"""
if is_scanned(pdf_path):
raise ValueError(
f"{pdf_path} appears to be a scanned PDF (no text layer). "
"Use docling / marker / MinerU instead."
)

```
out     = Path(out_dir)
img_dir = out / "images"
# P4 修正：每次轉換清空 img_dir，避免累積舊圖
if img_dir.exists():
    shutil.rmtree(img_dir)
img_dir.mkdir(parents=True)

reader   = PdfReader(pdf_path)
pages_md = []
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        pages_md.append(process_page(reader, page, i, img_dir))

md     = "\n\n---\n\n".join(pages_md)
out_md = out / (Path(pdf_path).stem + ".md")
out_md.write_text(md, encoding="utf-8")
return out_md
```

# ── 驗證 ──────────────────────────────────────────────────────────────────────

def verify(md_path: str) -> dict:
text   = Path(md_path).read_text(encoding="utf-8")
tables = re.findall(r"(|.+|\n|[-| :]+|\n(?:|.+|\n?)*)", text)
images = re.findall(r"![.*?](images/[^)]+)", text)
warns  = re.findall(r"<!- WARNING", text)
return {"tables": len(tables), "images": len(images), "warnings": len(warns)}

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
parser = argparse.ArgumentParser(description="PDF → Markdown (text-layer only)")
parser.add_argument("input",  help="PDF file or directory (with -batch)")
parser.add_argument("-o", "-output", default="output")
parser.add_argument("-batch", action="store_true")
args = parser.parse_args()

```
targets = list(Path(args.input).glob("*.pdf")) if args.batch else [Path(args.input)]
for pdf in targets:
    print(f"Converting: {pdf.name}")
    try:
        md_path = pdf_to_markdown(str(pdf), args.output)
        stats   = verify(str(md_path))
        print(f"  ✅ {md_path.name}  tables={stats['tables']}  images={stats['images']}  warnings={stats['warnings']}")
    except ValueError as e:
        print(f"  ❌ {e}")
```

if **name** == "**main**":
main()