#!/usr/bin/env python3
from __future__ import annotations

"""Improve an OpenCode skill description using an OpenAI-compatible model."""

import argparse
import json
from pathlib import Path

try:
    from scripts.utils import create_openai_client, default_model_from_env, extract_json_object, parse_skill_md
except ImportError:  # pragma: no cover - direct execution fallback
    from utils import create_openai_client, default_model_from_env, extract_json_object, parse_skill_md


OPTIMIZER_SYSTEM_PROMPT = """You are optimizing the frontmatter description of an OpenCode skill.

Goals:
- Improve when the skill should match.
- Keep the description concise, discriminative, and useful.
- Generalize from failures instead of keyword stuffing.
- Prefer imperative phrasing about user intent.

Constraints:
- Keep the description comfortably under 1024 characters.
- Mention the user situations where the skill should be used.
- Mention near-miss cases or boundaries only when they improve precision.
- Do not mention hidden implementation details unless they help the matcher understand the domain.

Respond with JSON only:
{"description": "new description text"}
"""


def _call_optimizer(
    prompt: str,
    model: str | None,
    base_url: str | None,
    api_key: str | None,
    timeout: int = 300,
) -> str:
    resolved_model = default_model_from_env(model)
    client = create_openai_client(base_url=base_url, api_key=api_key, timeout=timeout)
    response = client.chat.completions.create(
        model=resolved_model,
        temperature=0.2,
        max_tokens=500,
        messages=[
            {"role": "system", "content": OPTIMIZER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def improve_description(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list[dict],
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    test_results: dict | None = None,
    log_dir: Path | None = None,
    iteration: int | None = None,
) -> str:
    failed_triggers = [r for r in eval_results["results"] if r["should_trigger"] and not r["pass"]]
    false_triggers = [r for r in eval_results["results"] if not r["should_trigger"] and not r["pass"]]

    scores_summary = {
        "train": f"{eval_results['summary']['passed']}/{eval_results['summary']['total']}"
    }
    if test_results:
        scores_summary["test"] = f"{test_results['summary']['passed']}/{test_results['summary']['total']}"

    prompt_payload = {
        "skill_name": skill_name,
        "current_description": current_description,
        "scores": scores_summary,
        "failed_to_trigger": [
            {
                "query": r["query"],
                "trigger_rate": f"{r['triggers']}/{r['runs']}",
                "reasons": r.get("sample_reasons", []),
            }
            for r in failed_triggers
        ],
        "false_triggers": [
            {
                "query": r["query"],
                "trigger_rate": f"{r['triggers']}/{r['runs']}",
                "reasons": r.get("sample_reasons", []),
            }
            for r in false_triggers
        ],
        "history": [
            {
                "description": item.get("description"),
                "train_score": f"{item.get('train_passed', item.get('passed', 0))}/{item.get('train_total', item.get('total', 0))}",
                "test_score": (f"{item.get('test_passed')}/{item.get('test_total')}" if item.get('test_passed') is not None else None),
            }
            for item in history
        ],
        "skill_content": skill_content,
    }

    raw = _call_optimizer(
        json.dumps(prompt_payload, ensure_ascii=False, indent=2),
        model=model,
        base_url=base_url,
        api_key=api_key,
    )
    try:
        parsed = extract_json_object(raw)
        description = str(parsed.get("description", "")).strip().strip('"')
    except ValueError:
        description = raw.strip().strip('"')

    transcript = {
        "iteration": iteration,
        "prompt": prompt_payload,
        "response": raw,
        "parsed_description": description,
        "char_count": len(description),
        "over_limit": len(description) > 1024,
    }

    if len(description) > 1024:
        shorten_payload = {
            "instruction": "Rewrite the following skill description to stay under 1024 characters while keeping the most important trigger cues.",
            "description": description,
        }
        shorten_raw = _call_optimizer(
            json.dumps(shorten_payload, ensure_ascii=False, indent=2),
            model=model,
            base_url=base_url,
            api_key=api_key,
        )
        try:
            parsed = extract_json_object(shorten_raw)
            description = str(parsed.get("description", "")).strip().strip('"')
        except ValueError:
            description = shorten_raw.strip().strip('"')
        transcript["rewrite_response"] = shorten_raw
        transcript["rewrite_description"] = description
        transcript["rewrite_char_count"] = len(description)

    transcript["final_description"] = description
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"improve_iter_{iteration or 'unknown'}.json").write_text(
            json.dumps(transcript, indent=2),
            encoding="utf-8",
        )

    return description


def main() -> None:
    parser = argparse.ArgumentParser(description="Improve a skill description using an OpenAI-compatible model")
    parser.add_argument("--eval-results", required=True, help="Path to eval results JSON")
    parser.add_argument("--skill-path", required=True, help="Path to the skill directory")
    parser.add_argument("--history", default=None, help="Path to prior history JSON")
    parser.add_argument("--model", default=None, help="Model to use (default: OPENAI_MODEL or gpt-oss-120b)")
    parser.add_argument("--base-url", default=None, help="Override OPENAI_BASE_URL")
    parser.add_argument("--api-key", default=None, help="Override OPENAI_API_KEY")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        raise SystemExit(f"Error: No SKILL.md found at {skill_path}")

    eval_results = json.loads(Path(args.eval_results).read_text(encoding="utf-8"))
    history = json.loads(Path(args.history).read_text(encoding="utf-8")) if args.history else []
    name, _, content = parse_skill_md(skill_path)
    new_description = improve_description(
        skill_name=name,
        skill_content=content,
        current_description=eval_results["description"],
        eval_results=eval_results,
        history=history,
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
    )
    print(
        json.dumps(
            {
                "description": new_description,
                "history": history + [
                    {
                        "description": eval_results["description"],
                        "passed": eval_results["summary"]["passed"],
                        "failed": eval_results["summary"]["failed"],
                        "total": eval_results["summary"]["total"],
                        "results": eval_results["results"],
                    }
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
