"""
pdf_to_md.py -- Lightweight PDF to Markdown converter.

Dependencies: pdfplumber, pypdf, Pillow  (optional: markitdown)

Suitable for text-layer PDFs (not scanned).
Scanned PDFs are detected and rejected with a clear error suggesting
docling / marker / MinerU instead.

Usage:
    python pdf_to_md.py document.pdf -o output/
    python pdf_to_md.py ./folder/ -o output/ --batch
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
from pathlib import Path
from typing import Any

import pdfplumber
from PIL import Image
from pypdf import PdfReader

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_TABLE_COLS: int = 2
MIN_TABLE_ROWS: int = 2
PARAGRAPH_GAP_PT: float = 8.0

# ---------------------------------------------------------------------------
# Scanned-PDF detection
# ---------------------------------------------------------------------------


def is_scanned(pdf_path: str) -> bool:
    """Return True if the PDF has no meaningful text layer (likely scanned).

    Uses markitdown when available for better heuristics, otherwise falls
    back to pdfplumber character count on the first three pages.
    """
    try:
        from markitdown import MarkItDown  # type: ignore[import-untyped]

        result = MarkItDown().convert(pdf_path)
        return len(result.text_content.strip()) < 100
    except ImportError:
        pass

    # Fallback: sample first three pages with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        total = sum(len(p.extract_text() or "") for p in pdf.pages[:3])
    return total < 100


# ---------------------------------------------------------------------------
# Image extraction
# ---------------------------------------------------------------------------


def extract_page_images(
    reader: PdfReader, page_idx: int, img_dir: Path
) -> list[str]:
    """Extract raster images from *page_idx* and save as PNG into *img_dir*.

    Returns a list of Markdown image references or HTML warning comments for
    images that could not be decoded.
    """
    refs: list[str] = []
    for j, img_file in enumerate(reader.pages[page_idx].images):
        img_name = f"page{page_idx + 1}_img{j + 1}.png"
        try:
            pil = Image.open(io.BytesIO(img_file.data))
            pil.save(img_dir / img_name, "PNG")
            refs.append(f"![](images/{img_name})")
        except Exception as exc:  # noqa: BLE001
            refs.append(
                f"<!-- WARNING: image '{img_file.name}' on page "
                f"{page_idx + 1} skipped ({exc}) -->"
            )
    return refs


# ---------------------------------------------------------------------------
# Table extraction
# ---------------------------------------------------------------------------


def extract_page_tables(page: Any) -> list[dict[str, Any]]:
    """Find tables on *page* and return them as Markdown with y-position."""
    results: list[dict[str, Any]] = []
    for tbl_obj in page.find_tables():
        tbl = tbl_obj.extract()
        if (
            not tbl
            or len(tbl) < MIN_TABLE_ROWS
            or not tbl[0]
            or len(tbl[0]) < MIN_TABLE_COLS
        ):
            continue

        clean = [[(cell or "") for cell in row] for row in tbl]
        header = "| " + " | ".join(clean[0]) + " |"
        separator = "| " + " | ".join(["---"] * len(clean[0])) + " |"
        body_rows = ["| " + " | ".join(row) + " |" for row in clean[1:]]

        results.append(
            {
                "y_top": tbl_obj.bbox[1],
                "bbox": tbl_obj.bbox,
                "content": "\n".join([header, separator] + body_rows),
            }
        )
    return results


# ---------------------------------------------------------------------------
# Text extraction (excluding table regions)
# ---------------------------------------------------------------------------


def extract_page_text_blocks(
    page: Any, table_bboxes: list[tuple[float, ...]]
) -> list[dict[str, Any]]:
    """Extract text blocks from *page*, skipping areas covered by tables.

    Words are grouped into lines by y-coordinate and then merged into
    paragraphs separated by gaps larger than PARAGRAPH_GAP_PT.
    """
    words = page.extract_words(x_tolerance=2, y_tolerance=2)
    lines: dict[float, list[str]] = {}

    for w in words:
        # Skip words that fall inside any table bounding box
        if any(
            w["x0"] >= b[0]
            and w["x1"] <= b[2]
            and w["top"] >= b[1]
            and w["bottom"] <= b[3]
            for b in table_bboxes
        ):
            continue
        key = round(w["top"], 0)
        lines.setdefault(key, []).append(w["text"])

    sorted_ys = sorted(lines)
    paragraphs: list[dict[str, Any]] = []
    current: list[str] = []
    prev_y: float | None = None

    for y in sorted_ys:
        if prev_y is not None and (y - prev_y) > PARAGRAPH_GAP_PT:
            if current:
                paragraphs.append(
                    {"y_top": prev_y, "content": " ".join(current)}
                )
                current = []
        current.extend(lines[y])
        prev_y = y

    if current and prev_y is not None:
        paragraphs.append({"y_top": prev_y, "content": " ".join(current)})

    return paragraphs


# ---------------------------------------------------------------------------
# Multi-column heuristic
# ---------------------------------------------------------------------------


def is_multicolumn(page: Any) -> bool:
    """Rough heuristic: True when words split roughly evenly across the midline."""
    words = page.extract_words()
    if len(words) < 20:
        return False
    mid = page.width / 2
    left = sum(1 for w in words if w["x1"] < mid - 20)
    right = sum(1 for w in words if w["x0"] > mid + 20)
    return left > len(words) * 0.25 and right > len(words) * 0.25


# ---------------------------------------------------------------------------
# Per-page assembly (text + tables + images in y-order)
# ---------------------------------------------------------------------------


def process_page(
    reader: PdfReader, plumber_page: Any, page_idx: int, img_dir: Path
) -> str:
    """Build Markdown for a single page, interleaving text and tables by y."""
    tables = extract_page_tables(plumber_page)
    tbl_bboxes = [t["bbox"] for t in tables]
    texts = extract_page_text_blocks(plumber_page, tbl_bboxes)
    images = extract_page_images(reader, page_idx, img_dir)

    # Merge text paragraphs and tables, sort by vertical position
    all_blocks: list[tuple[float, str]] = [
        (t["y_top"], t["content"]) for t in texts
    ]
    all_blocks += [(t["y_top"], t["content"]) for t in tables]
    all_blocks.sort(key=lambda x: x[0])

    ordered = [block[1] for block in all_blocks if block[1].strip()]
    # Images appended at page end (pypdf has no reliable bbox for images)
    ordered += images

    if is_multicolumn(plumber_page):
        ordered.insert(
            0,
            f"<!-- NOTE: page {page_idx + 1} may have multi-column "
            "layout; reading order may need manual verification -->",
        )

    return "\n\n".join(ordered)


# ---------------------------------------------------------------------------
# Main conversion entry point
# ---------------------------------------------------------------------------


def pdf_to_markdown(pdf_path: str, out_dir: str) -> Path:
    """Convert a text-layer PDF to Markdown.

    - Images saved to ``output/images/`` as PNG, referenced with
      ``![](images/name.png)``
    - Tables converted to standard Markdown pipe-table syntax
    - Scanned PDFs rejected with a clear ValueError
    """
    if is_scanned(pdf_path):
        raise ValueError(
            f"{pdf_path} appears to be a scanned PDF (no text layer). "
            "Use docling / marker / MinerU instead."
        )

    out = Path(out_dir)
    img_dir = out / "images"
    # Clear previous images to avoid stale leftover files
    if img_dir.exists():
        shutil.rmtree(img_dir)
    img_dir.mkdir(parents=True)

    reader = PdfReader(pdf_path)
    pages_md: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            pages_md.append(process_page(reader, page, i, img_dir))

    md_text = "\n\n---\n\n".join(pages_md)
    out_md = out / (Path(pdf_path).stem + ".md")
    out_md.write_text(md_text, encoding="utf-8")
    return out_md


# ---------------------------------------------------------------------------
# Verification helper (returns counts for tables, images, warnings)
# ---------------------------------------------------------------------------


def verify(md_path: str) -> dict[str, int]:
    """Quick-check the generated Markdown for tables, images, and warnings."""
    text = Path(md_path).read_text(encoding="utf-8")

    # Match Markdown tables: header row, separator with dashes, body rows
    table_pattern = re.compile(
        r"^\|.+\|\n\|[\s\-:|]+\|\n(?:\|.+\|\n?)+", re.MULTILINE
    )
    tables = table_pattern.findall(text)

    # Match image references
    image_pattern = re.compile(r"!\[.*?\]\(images/[^)]+\)")
    images = image_pattern.findall(text)

    # Match warning / note comments
    warn_pattern = re.compile(r"<!--\s*(?:WARNING|NOTE):")
    warns = warn_pattern.findall(text)

    return {"tables": len(tables), "images": len(images), "warnings": len(warns)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Command-line interface for single-file and batch PDF conversion."""
    parser = argparse.ArgumentParser(
        description="PDF to Markdown converter (text-layer only)"
    )
    parser.add_argument("input", help="PDF file or directory (with --batch)")
    parser.add_argument("-o", "--output", default="output")
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()

    targets = (
        list(Path(args.input).glob("*.pdf"))
        if args.batch
        else [Path(args.input)]
    )

    for pdf in targets:
        print(f"Converting: {pdf.name}")
        # In batch mode each PDF gets its own subdirectory so images and
        # Markdown files from different PDFs never collide.
        pdf_out = (
            str(Path(args.output) / pdf.stem) if args.batch else args.output
        )
        try:
            md_path = pdf_to_markdown(str(pdf), pdf_out)
            stats = verify(str(md_path))
            print(
                f"  OK {md_path.name}  "
                f"tables={stats['tables']}  "
                f"images={stats['images']}  "
                f"warnings={stats['warnings']}"
            )
        except ValueError as exc:
            print(f"  FAIL {exc}")


if __name__ == "__main__":
    main()