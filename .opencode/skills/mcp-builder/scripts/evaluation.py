"""MCP Server Evaluation Harness

Evaluate MCP servers against an XML question set using any OpenAI-compatible,
tool-calling chat-completions endpoint.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from openai import OpenAI

from connections import create_connection

EVALUATION_PROMPT = """You are an AI assistant with access to MCP-backed tools.

When given a task, you MUST:
1. Use the available tools to complete the task when needed.
2. Provide a summary of each step in your approach, wrapped in <summary> tags.
3. Provide feedback on the tools provided, wrapped in <feedback> tags.
4. Provide your final response, wrapped in <response> tags.

Summary requirements:
- Explain the steps you took.
- Mention which tools you used, in what order, and why.
- Summarize the important inputs and outputs.

Feedback requirements:
- Comment on tool names, descriptions, and schemas.
- Note confusing parameters, oversized responses, or weak pagination.
- Suggest specific improvements that would help future agents.

Response requirements:
- Keep the final answer concise.
- If you cannot solve the task, return <response>NOT_FOUND</response>.
- For numeric answers, output only the number.
- For identifiers or names, output the exact requested value.
"""


def default_model(explicit: str | None = None) -> str:
    return explicit or os.getenv("OPENAI_MODEL") or "gpt-oss-120b"


def create_client(base_url: str | None = None, api_key: str | None = None, timeout: int = 120) -> OpenAI:
    kwargs: dict[str, Any] = {
        "api_key": api_key or os.getenv("OPENAI_API_KEY") or "opencode",
        "timeout": timeout,
    }
    resolved_base_url = base_url or os.getenv("OPENAI_BASE_URL")
    if resolved_base_url:
        kwargs["base_url"] = resolved_base_url
    return OpenAI(**kwargs)


def jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    if hasattr(value, "model_dump"):
        return jsonable(value.model_dump())
    if hasattr(value, "__dict__"):
        return jsonable({k: v for k, v in vars(value).items() if not k.startswith("_")})
    return str(value)


def parse_evaluation_file(file_path: Path) -> list[dict[str, Any]]:
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error parsing evaluation file {file_path}: {exc}")
        return []

    evaluations: list[dict[str, Any]] = []
    for qa_pair in root.findall(".//qa_pair"):
        question_elem = qa_pair.find("question")
        answer_elem = qa_pair.find("answer")
        if question_elem is None or answer_elem is None:
            continue
        evaluations.append(
            {
                "question": (question_elem.text or "").strip(),
                "answer": (answer_elem.text or "").strip(),
            }
        )
    return evaluations


def extract_xml_content(text: str | None, tag: str) -> str | None:
    if not text:
        return None
    matches = re.findall(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return matches[-1].strip() if matches else None


def build_openai_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    openai_tools: list[dict[str, Any]] = []
    for tool in tools:
        parameters = tool.get("input_schema") or {"type": "object", "properties": {}}
        if parameters.get("type") != "object":
            parameters = {"type": "object", "properties": {"value": parameters}}
        openai_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description") or "",
                    "parameters": parameters,
                },
            }
        )
    return openai_tools


async def agent_loop(
    client: OpenAI,
    model: str,
    question: str,
    tools: list[dict[str, Any]],
    connection: Any,
) -> tuple[str, dict[str, Any]]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": EVALUATION_PROMPT},
        {"role": "user", "content": question},
    ]
    openai_tools = build_openai_tools(tools)
    tool_metrics: dict[str, dict[str, Any]] = {}

    while True:
        request_kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 4096,
        }
        if openai_tools:
            request_kwargs["tools"] = openai_tools
            request_kwargs["tool_choice"] = "auto"

        response = await asyncio.to_thread(client.chat.completions.create, **request_kwargs)
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        tool_calls = message.tool_calls or []
        if not tool_calls:
            return message.content or "", tool_metrics

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_input = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                tool_input = {}

            start = time.time()
            try:
                tool_result = await connection.call_tool(tool_name, tool_input)
                normalized_result = jsonable(tool_result)
                tool_response = json.dumps(normalized_result, ensure_ascii=False)
            except Exception as exc:  # pragma: no cover - defensive
                tool_response = f"Error executing tool {tool_name}: {exc}\n{traceback.format_exc()}"
            duration = time.time() - start

            metrics = tool_metrics.setdefault(tool_name, {"count": 0, "durations": []})
            metrics["count"] += 1
            metrics["durations"].append(duration)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_response,
                }
            )


async def evaluate_single_task(
    client: OpenAI,
    model: str,
    qa_pair: dict[str, Any],
    tools: list[dict[str, Any]],
    connection: Any,
    task_index: int,
) -> dict[str, Any]:
    start_time = time.time()
    print(f"Task {task_index + 1}: {qa_pair['question']}")
    response_text, tool_metrics = await agent_loop(client, model, qa_pair["question"], tools, connection)
    response_value = extract_xml_content(response_text, "response")
    summary = extract_xml_content(response_text, "summary")
    feedback = extract_xml_content(response_text, "feedback")
    duration_seconds = time.time() - start_time
    return {
        "question": qa_pair["question"],
        "expected": qa_pair["answer"],
        "actual": response_value,
        "score": int(response_value == qa_pair["answer"]) if response_value else 0,
        "total_duration": duration_seconds,
        "tool_calls": tool_metrics,
        "num_tool_calls": sum(len(metrics["durations"]) for metrics in tool_metrics.values()),
        "summary": summary,
        "feedback": feedback,
    }


REPORT_HEADER = """
# Evaluation Report

## Summary

- **Accuracy**: {correct}/{total} ({accuracy:.1f}%)
- **Average Task Duration**: {average_duration_s:.2f}s
- **Average Tool Calls per Task**: {average_tool_calls:.2f}
- **Total Tool Calls**: {total_tool_calls}

---
"""

TASK_TEMPLATE = """
### Task {task_num}

**Question**: {question}
**Ground Truth Answer**: `{expected_answer}`
**Actual Answer**: `{actual_answer}`
**Correct**: {correct_indicator}
**Duration**: {total_duration:.2f}s
**Tool Calls**: {tool_calls}

**Summary**
{summary}

**Feedback**
{feedback}

---
"""


async def run_evaluation(
    eval_path: Path,
    connection: Any,
    model: str,
    base_url: str | None = None,
    api_key: str | None = None,
) -> str:
    print("🚀 Starting evaluation")
    client = create_client(base_url=base_url, api_key=api_key)
    tools = await connection.list_tools()
    print(f"📋 Loaded {len(tools)} tools from MCP server")
    qa_pairs = parse_evaluation_file(eval_path)
    print(f"📋 Loaded {len(qa_pairs)} evaluation tasks")

    results = []
    for i, qa_pair in enumerate(qa_pairs):
        print(f"Processing task {i + 1}/{len(qa_pairs)}")
        results.append(await evaluate_single_task(client, model, qa_pair, tools, connection, i))

    correct = sum(r["score"] for r in results)
    accuracy = (correct / len(results)) * 100 if results else 0
    average_duration_s = sum(r["total_duration"] for r in results) / len(results) if results else 0
    average_tool_calls = sum(r["num_tool_calls"] for r in results) / len(results) if results else 0
    total_tool_calls = sum(r["num_tool_calls"] for r in results)

    report = REPORT_HEADER.format(
        correct=correct,
        total=len(results),
        accuracy=accuracy,
        average_duration_s=average_duration_s,
        average_tool_calls=average_tool_calls,
        total_tool_calls=total_tool_calls,
    )
    report += "".join(
        TASK_TEMPLATE.format(
            task_num=i + 1,
            question=qa_pair["question"],
            expected_answer=qa_pair["answer"],
            actual_answer=result["actual"] or "N/A",
            correct_indicator="✅" if result["score"] else "❌",
            total_duration=result["total_duration"],
            tool_calls=json.dumps(result["tool_calls"], indent=2),
            summary=result["summary"] or "N/A",
            feedback=result["feedback"] or "N/A",
        )
        for i, (qa_pair, result) in enumerate(zip(qa_pairs, results))
    )
    return report


def parse_headers(header_list: list[str] | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for header in header_list or []:
        if ":" not in header:
            print(f"Warning: ignoring malformed header: {header}")
            continue
        key, value = header.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def parse_env_vars(env_list: list[str] | None) -> dict[str, str]:
    env: dict[str, str] = {}
    for entry in env_list or []:
        if "=" not in entry:
            print(f"Warning: ignoring malformed environment variable: {entry}")
            continue
        key, value = entry.split("=", 1)
        env[key.strip()] = value.strip()
    return env


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate MCP servers using an OpenAI-compatible tool-calling model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate a local stdio MCP server
  python evaluation.py -t stdio -c python -a my_server.py eval.xml

  # Evaluate an SSE MCP server
  python evaluation.py -t sse -u https://example.com/mcp -H \"Authorization: Bearer token\" eval.xml

  # Evaluate an HTTP MCP server with a local model gateway
  python evaluation.py -t http -u https://example.com/mcp -m gpt-oss-120b --base-url http://localhost:11434/v1 eval.xml
        """,
    )
    parser.add_argument("eval_file", type=Path, help="Path to evaluation XML file")
    parser.add_argument("-t", "--transport", choices=["stdio", "sse", "http"], default="stdio", help="Transport type (default: stdio)")
    parser.add_argument("-m", "--model", default=default_model(), help="Model to use (default: OPENAI_MODEL or gpt-oss-120b)")
    parser.add_argument("--base-url", default=None, help="Override OPENAI_BASE_URL for the evaluation model")
    parser.add_argument("--api-key", default=None, help="Override OPENAI_API_KEY for the evaluation model")

    stdio_group = parser.add_argument_group("stdio options")
    stdio_group.add_argument("-c", "--command", help="Command to run MCP server (stdio only)")
    stdio_group.add_argument("-a", "--args", nargs="+", help="Arguments for the command (stdio only)")
    stdio_group.add_argument("-e", "--env", nargs="+", help="Environment variables in KEY=VALUE format (stdio only)")

    remote_group = parser.add_argument_group("sse/http options")
    remote_group.add_argument("-u", "--url", help="MCP server URL (sse/http only)")
    remote_group.add_argument("-H", "--header", nargs="+", dest="headers", help="HTTP headers in 'Key: Value' format (sse/http only)")

    parser.add_argument("-o", "--output", type=Path, help="Output file for the evaluation report (default: stdout)")
    args = parser.parse_args()

    if not args.eval_file.exists():
        print(f"Error: evaluation file not found: {args.eval_file}")
        sys.exit(1)

    headers = parse_headers(args.headers)
    env_vars = parse_env_vars(args.env)

    try:
        connection = create_connection(
            transport=args.transport,
            command=args.command,
            args=args.args,
            env=env_vars or None,
            url=args.url,
            headers=headers or None,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"🔗 Connecting to MCP server via {args.transport}...")
    async with connection:
        print("✅ Connected successfully")
        report = await run_evaluation(
            args.eval_file,
            connection,
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
        )
        if args.output:
            args.output.write_text(report, encoding="utf-8")
            print(f"\n✅ Report saved to {args.output}")
        else:
            print("\n" + report)


if __name__ == "__main__":
    asyncio.run(main())
