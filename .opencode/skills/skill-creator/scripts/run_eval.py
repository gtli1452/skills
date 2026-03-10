#!/usr/bin/env python3
"""Run trigger evaluation for an OpenCode skill description.

Tests whether a skill's description causes OpenCode to load the skill via the
native ``skill`` tool for a set of queries. Outputs results as JSON.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import parse_skill_md


def _create_temp_skill_workspace(skill_name: str, skill_description: str) -> Path:
    """Create a temporary OpenCode-native workspace containing only the eval skill."""
    root = Path(tempfile.mkdtemp(prefix="opencode-skill-eval-"))
    skill_dir = root / ".opencode" / "skills" / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    description_lines = (skill_description or "").splitlines() or [""]
    indented_description = "\n  ".join(description_lines)

    skill_md = (
        "---\n"
        f"name: {skill_name}\n"
        "description: |\n"
        f"  {indented_description}\n"
        "compatibility: opencode\n"
        "---\n\n"
        f"# {skill_name}\n\n"
        "Temporary evaluation fixture used by skill-creator's description optimizer.\n"
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    return root


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    model: str | None = None,
    agent: str = "build",
) -> bool:
    """Run a single query and return whether OpenCode loaded the target skill."""
    workspace_root = _create_temp_skill_workspace(skill_name, skill_description)

    try:
        cmd = ["opencode", "run", "--agent", agent, "--format", "json", "--dir", str(workspace_root)]
        if model:
            cmd.extend(["--model", model])
        cmd.append(query)

        env = os.environ.copy()
        env["OPENCODE_DISABLE_CLAUDE_CODE"] = "1"

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=timeout,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "`opencode` CLI not found on PATH. Install OpenCode to run description evals."
            ) from exc
        except subprocess.TimeoutExpired:
            return False

        if result.returncode != 0 and not result.stdout.strip():
            raise RuntimeError(
                f"`opencode run` exited {result.returncode}\nstderr: {result.stderr}"
            )

        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("type") != "tool_use":
                continue

            part = event.get("part", {})
            if part.get("tool") != "skill":
                continue

            state = part.get("state", {})
            if not isinstance(state, dict):
                continue
            input_data = state.get("input", {})
            if isinstance(input_data, dict) and input_data.get("name") == skill_name:
                return True

        return False
    finally:
        shutil.rmtree(workspace_root, ignore_errors=True)


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    agent: str = "build",
) -> dict:
    """Run the full eval set and return results."""
    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    model,
                    agent,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="OpenCode model to use (default: current OpenCode model)")
    parser.add_argument("--agent", default="build", help="Primary OpenCode agent to use for each eval run")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, _ = parse_skill_md(skill_path)
    description = args.description or original_description

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        agent=args.agent,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
