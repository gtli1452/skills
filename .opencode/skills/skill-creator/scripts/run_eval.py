#!/usr/bin/env python3
from __future__ import annotations

"""Run trigger evaluation for an OpenCode skill description.

This does not call the live OpenCode matcher directly. Instead it uses an
OpenAI-compatible model as a proxy classifier for whether the skill should
load for each query.
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from scripts.utils import create_openai_client, default_model_from_env, extract_json_object, parse_skill_md
except ImportError:  # pragma: no cover - direct execution fallback
    from utils import create_openai_client, default_model_from_env, extract_json_object, parse_skill_md


MATCH_PROMPT = """You are simulating skill matching for an OpenCode-style assistant.

You will receive:
- a skill name
- a skill description
- a user query

Decide whether the assistant should load the skill before answering.

Trigger rules:
- Trigger when the skill would materially improve the answer by adding a specialized workflow, bundled scripts, domain-specific constraints, or unique references.
- Do not trigger for generic tasks the base assistant can already handle without loading the skill.
- Do not rely on body content that the matcher would not normally read; focus on the skill name and description.
- Be careful with near misses and keyword overlap.

Respond with JSON only:
{"trigger": true, "reason": "short explanation"}
"""


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    model: str,
    timeout: int,
    base_url: str | None = None,
    api_key: str | None = None,
) -> dict[str, object]:
    client = create_openai_client(base_url=base_url, api_key=api_key, timeout=timeout)
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=200,
        messages=[
            {"role": "system", "content": MATCH_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "skill_name": skill_name,
                        "skill_description": skill_description,
                        "query": query,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            },
        ],
    )
    text = response.choices[0].message.content or ""
    try:
        parsed = extract_json_object(text)
    except ValueError:
        return {"trigger": False, "reason": f"Unparseable response: {text[:120]}"}
    return {
        "trigger": bool(parsed.get("trigger")),
        "reason": str(parsed.get("reason", "")).strip(),
    }


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
) -> dict:
    resolved_model = default_model_from_env(model)
    outcomes: dict[int, list[dict[str, object]]] = {idx: [] for idx, _ in enumerate(eval_set)}

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_index: dict = {}
        for idx, item in enumerate(eval_set):
            for _ in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    resolved_model,
                    timeout,
                    base_url,
                    api_key,
                )
                future_to_index[future] = idx

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                outcomes[idx].append(future.result())
            except Exception as exc:  # pragma: no cover - defensive
                print(f"Warning: query failed: {exc}", file=sys.stderr)
                outcomes[idx].append({"trigger": False, "reason": str(exc)})

    results = []
    for idx, item in enumerate(eval_set):
        runs = outcomes[idx]
        triggers = sum(1 for run in runs if run.get("trigger"))
        trigger_rate = triggers / len(runs) if runs else 0.0
        should_trigger = bool(item["should_trigger"])
        did_pass = trigger_rate >= trigger_threshold if should_trigger else trigger_rate < trigger_threshold
        results.append(
            {
                "query": item["query"],
                "should_trigger": should_trigger,
                "trigger_rate": trigger_rate,
                "triggers": triggers,
                "runs": len(runs),
                "pass": did_pass,
                "sample_reasons": [run.get("reason", "") for run in runs[:3]],
            }
        )

    passed = sum(1 for result in results if result["pass"])
    total = len(results)
    return {
        "skill_name": skill_name,
        "description": description,
        "model": resolved_model,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run proxy trigger evaluation for an OpenCode skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to the skill directory")
    parser.add_argument("--description", default=None, help="Override the description from SKILL.md")
    parser.add_argument("--num-workers", type=int, default=8, help="Parallel requests to the evaluator model")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per model request in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of repeated judgments per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate needed to count as a trigger")
    parser.add_argument("--model", default=None, help="Model to use (default: OPENAI_MODEL or gpt-oss-120b)")
    parser.add_argument("--base-url", default=None, help="Override OPENAI_BASE_URL")
    parser.add_argument("--api-key", default=None, help="Override OPENAI_API_KEY")
    parser.add_argument("--output", default=None, help="Optional output file path")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    skill_name, current_description, _ = parse_skill_md(skill_path)
    result = run_eval(
        eval_set=eval_set,
        skill_name=skill_name,
        description=args.description or current_description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
    )

    serialized = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
