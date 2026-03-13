"""
run_evals.py -- Batch harness for the PDF-to-Markdown skill evaluation corpus.

Reads evals/evals.json, locates the PDF files listed there, runs
pdf_to_md.py on each, collects verify() stats, and prints a summary table.

Usage:
    python run_evals.py                    # from .opencode/skills/pdf/scripts/
    python run_evals.py --repo-root /path  # explicit repo root
    python run_evals.py --evals ../evals/evals.json  # custom evals path

Exit code:
    0 if all PDFs converted successfully
    1 if any PDF failed or produced suspicious output
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
import traceback
from pathlib import Path

# Allow importing pdf_to_md from the same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_to_md import pdf_to_markdown, verify  # noqa: E402


def _resolve_repo_root(explicit: str | None) -> Path:
    """Walk up from this script to find the repository root (contains .git/)."""
    if explicit:
        return Path(explicit).resolve()
    d = Path(__file__).resolve().parent
    for _ in range(10):
        if (d / ".git").exists():
            return d
        d = d.parent
    # Fallback: assume four levels up from scripts/
    return Path(__file__).resolve().parents[4]


def run(
    evals_path: Path,
    repo_root: Path,
    out_base: Path,
) -> list[dict]:
    """Run every eval entry and return results."""
    evals = json.loads(evals_path.read_text(encoding="utf-8"))
    entries = evals.get("evals", [])
    files_base = evals.get("files_base", "repo_root")

    results: list[dict] = []
    for entry in entries:
        eid = entry.get("id", "?")
        pdf_files = entry.get("files", [])
        prompt = entry.get("prompt", "")
        expectations = entry.get("expectations", [])

        for pdf_rel in pdf_files:
            if files_base == "repo_root":
                pdf_path = repo_root / pdf_rel
            else:
                pdf_path = Path(pdf_rel)

            out_dir = out_base / f"eval_{eid}" / pdf_path.stem
            result: dict = {
                "eval_id": eid,
                "pdf": str(pdf_rel),
                "out_dir": str(out_dir),
                "prompt_snippet": textwrap.shorten(prompt, 80),
                "expectation_count": len(expectations),
                "status": "pending",
                "stats": {},
                "error": None,
            }

            if not pdf_path.exists():
                result["status"] = "missing_pdf"
                result["error"] = f"PDF not found: {pdf_path}"
                results.append(result)
                continue

            try:
                out_dir.mkdir(parents=True, exist_ok=True)
                md_path = pdf_to_markdown(str(pdf_path), str(out_dir))
                stats = verify(str(md_path))
                result["stats"] = stats
                result["status"] = "ok" if stats.get("ok", True) else "warning"
            except Exception:
                result["status"] = "error"
                result["error"] = traceback.format_exc().splitlines()[-1]

            results.append(result)

    return results


def print_summary(results: list[dict]) -> bool:
    """Print a summary table and return True if all passed."""
    col_w = {"eval": 6, "pdf": 32, "status": 10, "tables": 7, "images": 7, "warns": 7, "suspect": 8}
    hdr = (
        f"{'Eval':<{col_w['eval']}} "
        f"{'PDF':<{col_w['pdf']}} "
        f"{'Status':<{col_w['status']}} "
        f"{'Tables':>{col_w['tables']}} "
        f"{'Images':>{col_w['images']}} "
        f"{'Warns':>{col_w['warns']}} "
        f"{'Suspect':>{col_w['suspect']}}"
    )
    sep = "-" * len(hdr)
    print(f"\n{sep}\n{hdr}\n{sep}")

    all_ok = True
    for r in results:
        s = r.get("stats", {})
        status = r["status"]
        if status not in ("ok",):
            all_ok = False
        pdf_name = Path(r["pdf"]).name
        if len(pdf_name) > col_w["pdf"]:
            pdf_name = pdf_name[: col_w["pdf"] - 3] + "..."
        print(
            f"{r['eval_id']:<{col_w['eval']}} "
            f"{pdf_name:<{col_w['pdf']}} "
            f"{status:<{col_w['status']}} "
            f"{s.get('tables', '-'):>{col_w['tables']}} "
            f"{s.get('images', '-'):>{col_w['images']}} "
            f"{s.get('warnings', '-'):>{col_w['warns']}} "
            f"{s.get('suspicious_plaintext_tables', '-'):>{col_w['suspect']}}"
        )
        if r.get("error"):
            print(f"       Error: {r['error']}")

    print(sep)
    passed = sum(1 for r in results if r["status"] == "ok")
    total = len(results)
    print(f"\n  {passed}/{total} passed")
    if not all_ok:
        print("  Some evaluations need attention — review output above.\n")
    else:
        print("  All evaluations passed.\n")
    return all_ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch PDF eval harness")
    parser.add_argument(
        "--evals",
        default=str(Path(__file__).resolve().parent.parent / "evals" / "evals.json"),
        help="Path to evals.json",
    )
    parser.add_argument("--repo-root", default=None, help="Repository root")
    parser.add_argument(
        "-o", "--output",
        default=str(Path(__file__).resolve().parent.parent / "evals" / "output"),
        help="Base output directory for eval results",
    )
    args = parser.parse_args()

    evals_path = Path(args.evals).resolve()
    if not evals_path.exists():
        print(f"ERROR: evals file not found: {evals_path}", file=sys.stderr)
        sys.exit(1)

    repo_root = _resolve_repo_root(args.repo_root)
    out_base = Path(args.output).resolve()

    print(f"Evals:     {evals_path}")
    print(f"Repo root: {repo_root}")
    print(f"Output:    {out_base}")

    results = run(evals_path, repo_root, out_base)
    ok = print_summary(results)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
