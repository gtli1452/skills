#!/usr/bin/env python3
from __future__ import annotations

"""Run the proxy eval + improve loop until max iterations or all pass."""

import argparse
import json
import random
import sys
import tempfile
import time
import webbrowser
from pathlib import Path

try:
    from scripts.generate_report import generate_html
    from scripts.improve_description import improve_description
    from scripts.run_eval import run_eval
    from scripts.utils import default_model_from_env, parse_skill_md
except ImportError:  # pragma: no cover - direct execution fallback
    from generate_report import generate_html
    from improve_description import improve_description
    from run_eval import run_eval
    from utils import default_model_from_env, parse_skill_md


def split_eval_set(eval_set: list[dict], holdout: float, seed: int = 42) -> tuple[list[dict], list[dict]]:
    random.seed(seed)
    trigger = [entry for entry in eval_set if entry["should_trigger"]]
    no_trigger = [entry for entry in eval_set if not entry["should_trigger"]]
    random.shuffle(trigger)
    random.shuffle(no_trigger)
    n_trigger_test = max(1, int(len(trigger) * holdout)) if trigger else 0
    n_no_trigger_test = max(1, int(len(no_trigger) * holdout)) if no_trigger else 0
    test_set = trigger[:n_trigger_test] + no_trigger[:n_no_trigger_test]
    train_set = trigger[n_trigger_test:] + no_trigger[n_no_trigger_test:]
    return train_set or test_set, test_set if train_set else []


def safe_open_report(path: Path) -> None:
    try:
        webbrowser.open(path.resolve().as_uri())
    except Exception:
        print(f"Report available at: {path}", file=sys.stderr)


def run_loop(
    eval_set: list[dict],
    skill_path: Path,
    description_override: str | None,
    num_workers: int,
    timeout: int,
    max_iterations: int,
    runs_per_query: int,
    trigger_threshold: float,
    holdout: float,
    model: str | None,
    verbose: bool,
    live_report_path: Path | None = None,
    log_dir: Path | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
) -> dict:
    name, original_description, content = parse_skill_md(skill_path)
    current_description = description_override or original_description
    resolved_model = default_model_from_env(model)

    if holdout > 0:
        train_set, test_set = split_eval_set(eval_set, holdout)
    else:
        train_set = eval_set
        test_set = []

    history = []
    exit_reason = "unknown"

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n{'=' * 60}", file=sys.stderr)
            print(f"Iteration {iteration}/{max_iterations}", file=sys.stderr)
            print(f"Description: {current_description}", file=sys.stderr)
            print(f"{'=' * 60}", file=sys.stderr)

        all_queries = train_set + test_set
        eval_start = time.time()
        all_results = run_eval(
            eval_set=all_queries,
            skill_name=name,
            description=current_description,
            num_workers=num_workers,
            timeout=timeout,
            runs_per_query=runs_per_query,
            trigger_threshold=trigger_threshold,
            model=resolved_model,
            base_url=base_url,
            api_key=api_key,
        )
        eval_elapsed = time.time() - eval_start

        train_queries = {item["query"] for item in train_set}
        train_result_list = [result for result in all_results["results"] if result["query"] in train_queries]
        test_result_list = [result for result in all_results["results"] if result["query"] not in train_queries]

        train_summary = {
            "passed": sum(1 for result in train_result_list if result["pass"]),
            "failed": sum(1 for result in train_result_list if not result["pass"]),
            "total": len(train_result_list),
        }
        test_summary = {
            "passed": sum(1 for result in test_result_list if result["pass"]),
            "failed": sum(1 for result in test_result_list if not result["pass"]),
            "total": len(test_result_list),
        } if test_set else None

        history.append(
            {
                "iteration": iteration,
                "description": current_description,
                "train_passed": train_summary["passed"],
                "train_failed": train_summary["failed"],
                "train_total": train_summary["total"],
                "train_results": train_result_list,
                "test_passed": test_summary["passed"] if test_summary else None,
                "test_failed": test_summary["failed"] if test_summary else None,
                "test_total": test_summary["total"] if test_summary else None,
                "test_results": test_result_list if test_summary else None,
                "passed": train_summary["passed"],
                "failed": train_summary["failed"],
                "total": train_summary["total"],
                "results": train_result_list,
            }
        )

        if live_report_path:
            partial_output = {
                "original_description": original_description,
                "best_description": current_description,
                "best_score": "in progress",
                "iterations_run": len(history),
                "holdout": holdout,
                "train_size": len(train_set),
                "test_size": len(test_set),
                "history": history,
            }
            live_report_path.write_text(
                generate_html(partial_output, auto_refresh=True, skill_name=name),
                encoding="utf-8",
            )

        if verbose:
            print(
                f"Train: {train_summary['passed']}/{train_summary['total']} | "
                f"Test: {test_summary['passed']}/{test_summary['total'] if test_summary else 0} | "
                f"Elapsed: {eval_elapsed:.1f}s",
                file=sys.stderr,
            )

        if train_summary["failed"] == 0:
            exit_reason = f"all_passed (iteration {iteration})"
            break
        if iteration == max_iterations:
            exit_reason = f"max_iterations ({max_iterations})"
            break

        blinded_history = [{k: v for k, v in item.items() if not k.startswith("test_")} for item in history]
        current_description = improve_description(
            skill_name=name,
            skill_content=content,
            current_description=current_description,
            eval_results={"results": train_result_list, "summary": train_summary},
            history=blinded_history,
            model=resolved_model,
            base_url=base_url,
            api_key=api_key,
            log_dir=log_dir,
            iteration=iteration,
        )

    if test_set:
        best = max(history, key=lambda item: item["test_passed"] or 0)
        best_score = f"{best['test_passed']}/{best['test_total']}"
    else:
        best = max(history, key=lambda item: item["train_passed"])
        best_score = f"{best['train_passed']}/{best['train_total']}"

    return {
        "exit_reason": exit_reason,
        "original_description": original_description,
        "best_description": best["description"],
        "best_score": best_score,
        "best_train_score": f"{best['train_passed']}/{best['train_total']}",
        "best_test_score": (f"{best['test_passed']}/{best['test_total']}" if test_set else None),
        "final_description": current_description,
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": len(train_set),
        "test_size": len(test_set),
        "model": resolved_model,
        "history": history,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run proxy eval + improvement loop for an OpenCode skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override starting description")
    parser.add_argument("--num-workers", type=int, default=8, help="Parallel requests to the evaluator model")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per model request in seconds")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max improvement iterations")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of repeated judgments per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--holdout", type=float, default=0.4, help="Fraction of eval set to hold out for testing (0 to disable)")
    parser.add_argument("--model", default=None, help="Model to use (default: OPENAI_MODEL or gpt-oss-120b)")
    parser.add_argument("--base-url", default=None, help="Override OPENAI_BASE_URL")
    parser.add_argument("--api-key", default=None, help="Override OPENAI_API_KEY")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    parser.add_argument("--report", default="auto", help="Generate HTML report at this path, or 'none' to disable")
    parser.add_argument("--results-dir", default=None, help="Save results.json, report.html, and logs into a timestamped subdirectory here")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, _, _ = parse_skill_md(skill_path)

    if args.report != "none":
        if args.report == "auto":
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            live_report_path = Path(tempfile.gettempdir()) / f"skill_description_report_{skill_path.name}_{timestamp}.html"
        else:
            live_report_path = Path(args.report)
        live_report_path.write_text(
            "<html><body><h1>Starting optimization loop...</h1><meta http-equiv='refresh' content='5'></body></html>",
            encoding="utf-8",
        )
        safe_open_report(live_report_path)
    else:
        live_report_path = None

    if args.results_dir:
        timestamp = time.strftime("%Y-%m-%d_%H%M%S")
        results_dir = Path(args.results_dir) / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)
    else:
        results_dir = None

    log_dir = results_dir / "logs" if results_dir else None
    output = run_loop(
        eval_set=eval_set,
        skill_path=skill_path,
        description_override=args.description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        max_iterations=args.max_iterations,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        holdout=args.holdout,
        model=args.model,
        verbose=args.verbose,
        live_report_path=live_report_path,
        log_dir=log_dir,
        base_url=args.base_url,
        api_key=args.api_key,
    )

    serialized = json.dumps(output, indent=2)
    print(serialized)
    if results_dir:
        (results_dir / "results.json").write_text(serialized, encoding="utf-8")

    if live_report_path:
        live_report_path.write_text(generate_html(output, auto_refresh=False, skill_name=name), encoding="utf-8")
        print(f"\nReport: {live_report_path}", file=sys.stderr)
        if results_dir:
            (results_dir / "report.html").write_text(live_report_path.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    main()
