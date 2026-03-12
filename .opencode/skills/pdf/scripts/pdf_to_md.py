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
from collections import Counter
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

# Heading detection thresholds (ratio relative to body font size).
# Raised in iteration 2 to reduce false-positive heading promotion.
H1_SIZE_RATIO: float = 1.50
H2_SIZE_RATIO: float = 1.30
H3_SIZE_RATIO: float = 1.15

# Maximum text length / word count that can ever qualify as a heading
HEADING_MAX_CHARS: int = 120
HEADING_MAX_WORDS: int = 20

# Minimum words per line for that line to count as "prose" when computing
# the body-font baseline.  Filters out short table cells and captions.
PROSE_MIN_WORDS_PER_LINE: int = 4

# Column count above which a table gets a readability warning
WIDE_TABLE_COLS: int = 8

# Ghost-table filtering thresholds
MIN_TABLE_TEXT_DENSITY: float = 0.3
MIN_TABLE_AVG_CELL_LEN: float = 1.5

# Header/footer detection
HEADER_FOOTER_MIN_PAGES: int = 3
HEADER_FOOTER_ZONE_PT: float = 60.0

# ---------------------------------------------------------------------------
# Font statistics collection (first pass over all pages)
# ---------------------------------------------------------------------------


def collect_font_stats(pdf: pdfplumber.PDF) -> dict[str, Any]:
    """Scan all pages to determine the body-font baseline and repeated headers/footers.

    Body font size is derived from *prose-like* lines (those with at least
    ``PROSE_MIN_WORDS_PER_LINE`` words).  This avoids small table text or
    footnote text from dominating the baseline – a major source of heading
    false-positives in iteration 1.

    Returns:
        body_size      – most common font size in prose lines (float)
        body_fontname  – most common font name in prose lines (str)
        header_footer_texts – set of normalised strings that recur in the
                              header / footer zone across many pages
    """
    all_size_counter: Counter[float] = Counter()
    all_font_counter: Counter[str] = Counter()
    prose_size_counter: Counter[float] = Counter()
    prose_font_counter: Counter[str] = Counter()
    top_texts: Counter[str] = Counter()
    bottom_texts: Counter[str] = Counter()
    num_pages = len(pdf.pages)

    for page in pdf.pages:
        words = page.extract_words(
            x_tolerance=2, y_tolerance=2,
            extra_attrs=["fontname", "size"],
        )
        page_height = page.height

        # Group words into lines by rounded y-position for prose detection
        page_lines: dict[float, list[dict[str, Any]]] = {}
        for w in words:
            y_key = round(w.get("top", 0), 0)
            page_lines.setdefault(y_key, []).append(w)

        for w in words:
            sz = w.get("size")
            fn = w.get("fontname", "")
            if sz and sz > 0:
                chars = max(len(w.get("text", "")), 1)
                all_size_counter[round(sz, 1)] += chars
                all_font_counter[fn] += chars
            text = w.get("text", "").strip()
            if not text:
                continue
            top_val = w.get("top", 0)
            if top_val < HEADER_FOOTER_ZONE_PT:
                top_texts[text.lower()] += 1
            elif top_val > page_height - HEADER_FOOTER_ZONE_PT:
                bottom_texts[text.lower()] += 1

        # Prose-line identification: lines with enough words to likely be
        # real paragraph text rather than table cells or captions.
        for _y_key, line_words in page_lines.items():
            if len(line_words) >= PROSE_MIN_WORDS_PER_LINE:
                for w in line_words:
                    sz = w.get("size")
                    fn = w.get("fontname", "")
                    if sz and sz > 0:
                        chars = max(len(w.get("text", "")), 1)
                        prose_size_counter[round(sz, 1)] += chars
                        prose_font_counter[fn] += chars

    # Prefer prose-derived body size; fall back to overall stats
    if prose_size_counter:
        body_size = prose_size_counter.most_common(1)[0][0]
        body_fontname = (
            prose_font_counter.most_common(1)[0][0] if prose_font_counter else ""
        )
    else:
        body_size = (
            all_size_counter.most_common(1)[0][0] if all_size_counter else 11.0
        )
        body_fontname = (
            all_font_counter.most_common(1)[0][0] if all_font_counter else ""
        )

    threshold = min(HEADER_FOOTER_MIN_PAGES, max(2, num_pages // 2))
    hf_texts: set[str] = set()
    for txt, count in top_texts.items():
        if count >= threshold:
            hf_texts.add(txt)
    for txt, count in bottom_texts.items():
        if count >= threshold:
            hf_texts.add(txt)

    return {
        "body_size": body_size,
        "body_fontname": body_fontname,
        "header_footer_texts": hf_texts,
    }


# ---------------------------------------------------------------------------
# Heading classification
# ---------------------------------------------------------------------------


def _is_bold(fontname: str) -> bool:
    """Heuristic: does the font name indicate bold weight?"""
    fn = fontname.lower()
    return "bold" in fn or "black" in fn or "heavy" in fn


def _is_title_case_or_upper(text: str) -> bool:
    """Check if *text* follows title-case or ALL-CAPS heading conventions."""
    stripped = text.strip()
    if not stripped:
        return False
    # ALL-CAPS (ignore very short tokens like "I" or abbreviations)
    alpha = [c for c in stripped if c.isalpha()]
    if len(alpha) > 3 and all(c.isupper() for c in alpha):
        return True
    # Title case: majority of significant words start with uppercase
    words = stripped.split()
    if len(words) < 2:
        return True  # single word – neutral, don't block
    _MINOR = {
        "a", "an", "the", "and", "or", "of", "in", "on", "to",
        "for", "with", "at", "by", "from", "is", "are", "was", "were",
        "not", "but", "nor", "so", "yet", "as", "its", "it",
    }
    significant = [w for w in words if w.lower() not in _MINOR]
    if not significant:
        return False
    caps = sum(1 for w in significant if w[:1].isupper())
    return caps / len(significant) >= 0.7


def classify_heading(
    size: float, fontname: str, body_size: float, text: str
) -> int:
    """Return heading level 1-3, or 0 for body text.

    Iteration 2 strengthens evidence requirements beyond pure size ratio
    to sharply reduce false positives: text length / word count limits,
    boldness, and title-case / all-caps patterns are all considered.

    Iteration 3 tightens per-level length caps (H2 ≤ 80 chars, H3 ≤ 60
    chars) and rejects long ALL-CAPS prose which is typically legal /
    disclaimer boilerplate rather than a structural heading.
    """
    if body_size <= 0 or size <= 0:
        return 0

    stripped = text.strip()

    # Hard length gate – nothing this long is a heading
    if (
        len(stripped) > HEADING_MAX_CHARS
        or len(stripped.split()) > HEADING_MAX_WORDS
    ):
        return 0

    # Iteration 3: long all-caps prose is legal/disclaimer boilerplate, not a
    # heading.  True all-caps headings are short (e.g. "INTRODUCTION"); long
    # all-caps text is typically trademark notices or warranty disclaimers.
    _alpha = [c for c in stripped if c.isalpha()]
    if len(_alpha) > 3 and all(c.isupper() for c in _alpha) and len(stripped) > 60:
        return 0

    ratio = size / body_size
    bold = _is_bold(fontname)
    title_like = _is_title_case_or_upper(stripped)

    # H1: clearly oversized text
    if ratio >= H1_SIZE_RATIO:
        return 1

    # H2: moderately larger – require bold *or* title-case for confirmation
    if ratio >= H2_SIZE_RATIO:
        # Iteration 3: tighter per-level length cap for H2
        if len(stripped) > 80 or len(stripped.split()) > 14:
            return 0
        if bold or title_like:
            return 2
        # Well above threshold → allow without additional traits
        if ratio >= H2_SIZE_RATIO + 0.15:
            return 2
        return 0

    # H3: slightly larger and bold
    if ratio >= H3_SIZE_RATIO and bold:
        # Iteration 3: tighter per-level length cap for H3
        if len(stripped) > 60 or len(stripped.split()) > 10:
            return 0
        return 3

    # Same size as body, bold, short, title-like → weak H3 candidate
    if bold and ratio >= 1.0 and len(stripped) <= 60 and title_like:
        return 3

    return 0


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


def _sanitize_cell(cell: str | None) -> str:
    """Clean a table cell for Markdown: collapse newlines, strip, escape pipes."""
    if not cell:
        return ""
    text = cell.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s{2,}", " ", text).strip()
    text = text.replace("|", "\\|")
    return text


def _is_ghost_table(rows: list[list[str]], bbox: tuple[float, ...]) -> bool:
    """Detect 'ghost tables' created by diagrams or decorative rules."""
    total_cells = sum(len(row) for row in rows)
    if total_cells == 0:
        return True
    non_empty = sum(1 for row in rows for cell in row if cell.strip())
    if non_empty / total_cells < MIN_TABLE_TEXT_DENSITY:
        return True
    lengths = [len(cell.strip()) for row in rows for cell in row if cell.strip()]
    if lengths and (sum(lengths) / len(lengths)) < MIN_TABLE_AVG_CELL_LEN:
        return True
    return False


def _detect_title_row(
    rows: list[list[str]],
) -> tuple[str | None, list[list[str]]]:
    """Detect and extract a merged title row from the top of a table.

    A title row is one where most cells are empty except one, or where all
    non-empty cells share the same text (a merged-cell artefact).
    """
    if len(rows) < 3:
        return None, rows
    first = rows[0]
    non_empty = [c for c in first if c.strip()]
    if len(non_empty) == 0:
        return None, rows[1:]
    if len(non_empty) == 1:
        return non_empty[0].strip(), rows[1:]
    unique = set(c.strip() for c in non_empty)
    if len(unique) == 1:
        return unique.pop(), rows[1:]
    return None, rows


def _normalize_span_cells(rows: list[list[str]], ncols: int) -> list[list[str]]:
    """Pad / truncate every row to exactly *ncols* columns."""
    result: list[list[str]] = []
    for row in rows:
        if len(row) < ncols:
            row = list(row) + [""] * (ncols - len(row))
        elif len(row) > ncols:
            row = row[:ncols]
        result.append(row)
    return result


def _forward_fill_groups(
    rows: list[list[str]], ncols: int,
) -> tuple[list[list[str]], bool]:
    """Vertically forward-fill sparse leftmost columns in group-structured tables.

    PDF tables often use merged cells for group headers (e.g. a bank name in
    column 1 spanning several data rows).  pdfplumber renders these as one
    filled cell followed by empty cells below.  This copies values downward in
    such columns so the resulting Markdown is self-contained row-by-row.

    Only fills columns from the left that show a clear group pattern
    (significantly fewer non-empty data cells than the remaining columns).
    Stops at the first column that is mostly populated.

    Returns ``(rows, did_fill)`` — *did_fill* is True if any cells were filled.
    """
    if len(rows) < 3 or ncols < 3:
        return rows, False

    result = [list(row) for row in rows]
    data_rows = result[1:]  # skip header row
    total = len(data_rows)
    if total < 2:
        return rows, False

    filled = False
    for col in range(ncols):
        non_empty = sum(1 for r in data_rows if r[col].strip())
        # Column is mostly populated → not a group column; stop scanning
        if non_empty >= total * 0.6:
            break
        # Column is entirely empty → nothing to propagate
        if non_empty == 0:
            continue
        last_val = ""
        for row_idx in range(1, len(result)):
            cell = result[row_idx][col].strip()
            if cell:
                last_val = cell
            elif last_val:
                result[row_idx][col] = last_val
                filled = True

    return result, filled


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

        clean = [[_sanitize_cell(cell) for cell in row] for row in tbl]

        if _is_ghost_table(clean, tbl_obj.bbox):
            continue

        title, clean = _detect_title_row(clean)
        if len(clean) < MIN_TABLE_ROWS:
            continue

        ncols = max(len(row) for row in clean)
        if ncols < MIN_TABLE_COLS:
            continue
        clean = _normalize_span_cells(clean, ncols)
        clean, did_fill = _forward_fill_groups(clean, ncols)

        header = "| " + " | ".join(clean[0]) + " |"
        separator = "| " + " | ".join(["---"] * ncols) + " |"
        body_rows = ["| " + " | ".join(row) + " |" for row in clean[1:]]

        parts: list[str] = []
        if title:
            parts.append(f"**{title}**\n")
        if ncols >= WIDE_TABLE_COLS:
            parts.append(
                f"<!-- NOTE: wide table ({ncols} cols); "
                "formatting may be approximate -->"
            )
        if did_fill:
            parts.append(
                "<!-- NOTE: sparse group columns were forward-filled "
                "for readability -->"
            )
        parts.append("\n".join([header, separator] + body_rows))

        results.append(
            {
                "y_top": tbl_obj.bbox[1],
                "bbox": tbl_obj.bbox,
                "content": "\n".join(parts),
            }
        )
    return results


# ---------------------------------------------------------------------------
# Text extraction (excluding table regions)
# ---------------------------------------------------------------------------


def extract_page_text_blocks(
    page: Any,
    table_bboxes: list[tuple[float, ...]],
    font_stats: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract text blocks with heading detection, skipping table regions.

    Uses font size / name from each word to classify headings.
    Filters repeated header / footer text.
    """
    body_size: float = font_stats["body_size"]
    hf_texts: set[str] = font_stats["header_footer_texts"]

    words = page.extract_words(
        x_tolerance=2, y_tolerance=2,
        extra_attrs=["fontname", "size"],
    )

    # Group words into lines keyed by rounded y, tracking font info
    lines: dict[float, dict[str, Any]] = {}
    for w in words:
        if any(
            w["x0"] >= b[0]
            and w["x1"] <= b[2]
            and w["top"] >= b[1]
            and w["bottom"] <= b[3]
            for b in table_bboxes
        ):
            continue
        key = round(w["top"], 0)
        if key not in lines:
            lines[key] = {"words": [], "sizes": [], "fontnames": []}
        lines[key]["words"].append(w["text"])
        sz = w.get("size", 0)
        fn = w.get("fontname", "")
        chars = max(len(w.get("text", "")), 1)
        lines[key]["sizes"].extend([sz] * chars)
        lines[key]["fontnames"].extend([fn] * chars)

    sorted_ys = sorted(lines)
    paragraphs: list[dict[str, Any]] = []
    current_words: list[str] = []
    current_sizes: list[float] = []
    current_fonts: list[str] = []
    prev_y: float | None = None
    block_start_y: float | None = None

    def _dominant_size(sizes: list[float]) -> float:
        if not sizes:
            return body_size
        c: Counter[float] = Counter(round(s, 1) for s in sizes)
        return c.most_common(1)[0][0]

    def _dominant_font(fonts: list[str]) -> str:
        if not fonts:
            return ""
        return Counter(fonts).most_common(1)[0][0]

    def _flush() -> None:
        nonlocal current_words, current_sizes, current_fonts, block_start_y
        if not current_words or block_start_y is None:
            current_words, current_sizes, current_fonts = [], [], []
            return

        text = " ".join(current_words)

        # Filter header/footer text
        if text.lower().strip() in hf_texts:
            current_words, current_sizes, current_fonts = [], [], []
            return

        dom_size = _dominant_size(current_sizes)
        dom_font = _dominant_font(current_fonts)

        heading_level = classify_heading(dom_size, dom_font, body_size, text)

        # classify_heading already enforces length limits; extra safety net
        if heading_level > 0 and len(text) > HEADING_MAX_CHARS:
            heading_level = 0

        # Don't promote list items, captions, reference labels, or sentences
        stripped = text.strip()
        if heading_level > 0 and (
            stripped.startswith(("•", "-", "\u2013", "\u2014", "*"))
            or re.match(r"^\d+\.\s", stripped)
            or re.match(
                r"^(Figure|Table|Source|Note)\s", stripped, re.IGNORECASE
            )
            # Sentence-like text ending with a period is unlikely a heading
            or (stripped.endswith(".") and len(stripped) > 40)
            # Iteration 3: cross-reference sentences (often long, bold, and
            # mistaken for headings).  Patterns like "See Section 4.2",
            # "Refer to Appendix B", "as described in …".
            or re.search(
                r"\b(?:see\s+(?:the|section|table|figure|appendix|clause|page|also)"
                r"|refer(?:ence)?\s+to"
                r"|as\s+described\s+in"
                r"|in\s+accordance\s+with"
                r"|for\s+(?:more\s+|further\s+|additional\s+)?(?:details|information)\b"
                r"|^the\s+following\b"
                r"|^please\s+(?:note|refer|see|contact)\b)",
                stripped,
                re.IGNORECASE,
            )
            # Iteration 3: legal / disclaimer boilerplate.  Bold or large
            # font disclaimers are a common source of false-positive headings.
            or re.search(
                r"\b(?:provided\s+.{0,15}as[\s-]is"
                r"|without\s+warranty"
                r"|all\s+rights\s+reserved"
                r"|disclaimer"
                r"|subject\s+to\s+(?:the\s+)?(?:terms|conditions|limitations)"
                r"|governing\s+law"
                r"|(?:no|limit(?:ed|ation\s+of))\s+liability"
                r"|shall\s+not\s+be\s+(?:liable|responsible)"
                r"|to\s+the\s+(?:fullest|maximum)\s+extent"
                r"|warranty\s+of\s+(?:merchantability|fitness))\b",
                stripped,
                re.IGNORECASE,
            )
            # Iteration 3: lines ending with continuation punctuation are
            # mid-sentence fragments, not headings.
            or stripped[-1:] in (",", ";", ":")
        ):
            heading_level = 0

        if heading_level > 0:
            text = "#" * heading_level + " " + text

        paragraphs.append({"y_top": block_start_y, "content": text})
        current_words, current_sizes, current_fonts = [], [], []

    for y in sorted_ys:
        line = lines[y]

        # Paragraph gap → flush
        if prev_y is not None and (y - prev_y) > PARAGRAPH_GAP_PT:
            _flush()
            block_start_y = y

        if block_start_y is None:
            block_start_y = y

        # Font-size change within a visual paragraph → also flush
        if current_sizes and line["sizes"]:
            cur_dom = _dominant_size(current_sizes)
            line_dom = _dominant_size(line["sizes"])
            if abs(cur_dom - line_dom) > 1.5:
                _flush()
                block_start_y = y

        current_words.extend(line["words"])
        current_sizes.extend(line["sizes"])
        current_fonts.extend(line["fontnames"])
        prev_y = y

    _flush()
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
    reader: PdfReader, plumber_page: Any, page_idx: int, img_dir: Path,
    font_stats: dict[str, Any],
) -> str:
    """Build Markdown for a single page, interleaving text and tables by y."""
    tables = extract_page_tables(plumber_page)
    tbl_bboxes = [t["bbox"] for t in tables]
    texts = extract_page_text_blocks(plumber_page, tbl_bboxes, font_stats)
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
        font_stats = collect_font_stats(pdf)
        for i, page in enumerate(pdf.pages):
            pages_md.append(process_page(reader, page, i, img_dir, font_stats))

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