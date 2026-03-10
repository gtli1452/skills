"""MCP Server Evaluation Harness

This script evaluates MCP servers by running test questions against them using
any tool-calling model exposed through an OpenAI-compatible chat completions API.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
import traceback
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from connections import create_connection

EVALUATION_PROMPT = """You are an AI assistant with access to tools.

When given a task, you MUST:
1. Use the available tools to complete the task
2. Provide summary of each step in your approach, wrapped in <summary> tags
3. Provide feedback on the tools provided, wrapped in <feedback> tags
4. Provide your final response, wrapped in <response> tags

Summary Requirements:
- In your <summary> tags, you must explain:
  - The steps you took to complete the task
  - Which tools you used, in what order, and why
  - The inputs you provided to each tool
  - The outputs you received from each tool
  - A summary for how you arrived at the response

Feedback Requirements:
- In your <feedback> tags, provide constructive feedback on the tools:
  - Comment on tool names: Are they clear and descriptive?
  - Comment on input parameters: Are they well-documented? Are required vs optional parameters clear?
  - Comment on descriptions: Do they accurately describe what the tool does?
  - Comment on any errors encountered during tool usage: Did the tool fail to execute? Did the tool return too many tokens?
  - Identify specific areas for improvement and explain WHY they would help
  - Be specific and actionable in your suggestions

Response Requirements:
- Your response should be concise and directly address what was asked
- Always wrap your final response in <response> tags
- If you cannot solve the task return <response>NOT_FOUND</response>
- For numeric responses, provide just the number
- For IDs, provide just the ID
- For names or text, provide the exact text requested
- Your response should go last"""

DEFAULT_MAX_TOKENS = 4096
DEFAULT_REQUEST_TIMEOUT_S = 300


def parse_evaluation_file(file_path: Path) -> list[dict[str, Any]]:
    """Parse XML evaluation file with qa_pair elements."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        evaluations = []

        for qa_pair in root.findall(".//qa_pair"):
            question_elem = qa_pair.find("question")
            answer_elem = qa_pair.find("answer")

            if question_elem is not None and answer_elem is not None:
                evaluations.append({
                    "question": (question_elem.text or "").strip(),
                    "answer": (answer_elem.text or "").strip(),
                })

        return evaluations
    except Exception as e:
        print(f"Error parsing evaluation file {file_path}: {e}")
        return []


def extract_xml_content(text: str, tag: str) -> str | None:
    """Extract content from XML tags."""
    pattern = rf"<{tag}>(.*?)</{tag}>"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[-1].strip() if matches else None


def serialize_tool_result(tool_result: Any) -> str:
    """Serialize MCP tool results into a string for the model."""
    if isinstance(tool_result, str):
        return tool_result

    try:
        return json.dumps(tool_result, ensure_ascii=False, default=str)
    except TypeError:
        return str(tool_result)


def normalize_completion_url(base_url: str) -> str:
    """Normalize a base URL into an OpenAI-compatible chat completions endpoint."""
    base_url = base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def convert_tools_for_model(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert MCP tool metadata into OpenAI-compatible function tool specs."""
    converted = []
    for tool in tools:
        parameters = tool.get("input_schema") or {"type": "object", "properties": {}}
        converted.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description") or "",
                "parameters": parameters,
            },
        })
    return converted


def extract_message_text(message: dict[str, Any]) -> str:
    """Extract text content from a chat completion message."""
    content = message.get("content")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                if block.get("type") in {"text", "output_text"} and block.get("text"):
                    parts.append(str(block["text"]))
                elif isinstance(block.get("content"), str):
                    parts.append(block["content"])
        return "".join(parts).strip()

    return ""


def parse_tool_arguments(raw_arguments: Any) -> dict[str, Any]:
    """Parse tool arguments returned by the model."""
    if raw_arguments is None or raw_arguments == "":
        return {}

    if isinstance(raw_arguments, dict):
        return raw_arguments

    if isinstance(raw_arguments, str):
        parsed = json.loads(raw_arguments)
        if isinstance(parsed, dict):
            return parsed

    raise ValueError(f"Tool arguments must be a JSON object, got: {raw_arguments!r}")


def parse_headers(header_list: list[str]) -> dict[str, str]:
    """Parse header strings in format 'Key: Value' into a dictionary."""
    headers = {}
    if not header_list:
        return headers

    for header in header_list:
        if ":" in header:
            key, value = header.split(":", 1)
            headers[key.strip()] = value.strip()
        else:
            print(f"Warning: Ignoring malformed header: {header}")
    return headers


def parse_env_vars(env_list: list[str]) -> dict[str, str]:
    """Parse environment variable strings in format 'KEY=VALUE' into a dictionary."""
    env = {}
    if not env_list:
        return env

    for env_var in env_list:
        if "=" in env_var:
            key, value = env_var.split("=", 1)
            env[key.strip()] = value.strip()
        else:
            print(f"Warning: Ignoring malformed environment variable: {env_var}")
    return env


def get_env_default(*names: str) -> str | None:
    """Return the first non-empty environment variable from the provided names."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


@dataclass
class ChatCompletionClient:
    """Minimal client for OpenAI-compatible chat completions APIs."""

    model: str
    base_url: str
    api_key: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    timeout_s: int = DEFAULT_REQUEST_TIMEOUT_S
    max_tokens: int = DEFAULT_MAX_TOKENS

    def __post_init__(self):
        self.endpoint = normalize_completion_url(self.base_url)
        merged_headers = {"Content-Type": "application/json"}
        merged_headers.update(self.headers or {})
        if self.api_key and "authorization" not in {header.lower() for header in merged_headers}:
            merged_headers["Authorization"] = f"Bearer {self.api_key}"
        self.headers = merged_headers

    def create_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create a chat completion request."""
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0,
            "max_tokens": self.max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=data,
            headers=self.headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Model API request failed with HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Model API request failed: {exc.reason}") from exc


async def agent_loop(
    client: ChatCompletionClient,
    question: str,
    tools: list[dict[str, Any]],
    connection: Any,
) -> tuple[str, dict[str, Any]]:
    """Run the agent loop with MCP tools."""
    messages = [
        {"role": "system", "content": EVALUATION_PROMPT},
        {"role": "user", "content": question},
    ]
    tool_specs = convert_tools_for_model(tools)
    tool_metrics: dict[str, dict[str, Any]] = {}

    while True:
        response = await asyncio.to_thread(client.create_completion, messages, tool_specs)
        choices = response.get("choices") or []
        if not choices:
            raise RuntimeError(
                f"Model API returned no choices: {json.dumps(response, ensure_ascii=False)}"
            )

        message = choices[0].get("message") or {}
        response_text = extract_message_text(message)
        tool_calls = message.get("tool_calls") or []

        if not tool_calls:
            return response_text, tool_metrics

        messages.append({
            "role": "assistant",
            "content": response_text or "",
            "tool_calls": tool_calls,
        })

        for tool_call in tool_calls:
            function = tool_call.get("function") or {}
            tool_name = function.get("name")
            tool_start_ts = time.time()

            try:
                if not tool_name:
                    raise ValueError(f"Missing tool name in tool call: {tool_call}")
                tool_input = parse_tool_arguments(function.get("arguments"))
                tool_result = await connection.call_tool(tool_name, tool_input)
                tool_response = serialize_tool_result(tool_result)
            except Exception as e:
                tool_response = f"Error executing tool {tool_name}: {str(e)}\n"
                tool_response += traceback.format_exc()
            tool_duration = time.time() - tool_start_ts

            if tool_name not in tool_metrics:
                tool_metrics[tool_name] = {"count": 0, "durations": []}
            tool_metrics[tool_name]["count"] += 1
            tool_metrics[tool_name]["durations"].append(tool_duration)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", tool_name or "tool"),
                "content": tool_response,
            })


async def evaluate_single_task(
    client: ChatCompletionClient,
    qa_pair: dict[str, Any],
    tools: list[dict[str, Any]],
    connection: Any,
    task_index: int,
) -> dict[str, Any]:
    """Evaluate a single QA pair with the given tools."""
    start_time = time.time()

    print(f"Task {task_index + 1}: Running task with question: {qa_pair['question']}")
    response, tool_metrics = await agent_loop(client, qa_pair["question"], tools, connection)

    response_value = extract_xml_content(response or "", "response")
    summary = extract_xml_content(response or "", "summary")
    feedback = extract_xml_content(response or "", "feedback")

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
    client: ChatCompletionClient,
) -> str:
    """Run evaluation with MCP server tools."""
    print("🚀 Starting Evaluation")

    tools = await connection.list_tools()
    print(f"📋 Loaded {len(tools)} tools from MCP server")

    qa_pairs = parse_evaluation_file(eval_path)
    print(f"📋 Loaded {len(qa_pairs)} evaluation tasks")

    results = []
    for i, qa_pair in enumerate(qa_pairs):
        print(f"Processing task {i + 1}/{len(qa_pairs)}")
        result = await evaluate_single_task(client, qa_pair, tools, connection, i)
        results.append(result)

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

    report += "".join([
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
    ])

    return report


async def main():
    parser = argparse.ArgumentParser(
        description="Evaluate MCP servers using test questions and a tool-calling model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate a local stdio MCP server with a local or proxied model endpoint
  python evaluation.py --llm-base-url http://localhost:11434/v1 --model your-tool-calling-model -t stdio -c python -a my_server.py eval.xml

  # Evaluate an HTTP MCP server with a hosted model gateway
  python evaluation.py --llm-base-url https://api.example.com/v1 --llm-api-key sk-example --model provider/model-name -t http -u https://example.com/mcp eval.xml
        """,
    )

    parser.add_argument("eval_file", type=Path, help="Path to evaluation XML file")
    parser.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=get_env_default("LLM_MODEL", "OPENAI_MODEL"),
        help="Tool-calling model to use (default: LLM_MODEL/OPENAI_MODEL env var)",
    )
    parser.add_argument(
        "--llm-base-url",
        default=get_env_default("LLM_BASE_URL", "OPENAI_BASE_URL"),
        help="Base URL for an OpenAI-compatible chat completions API (default: LLM_BASE_URL/OPENAI_BASE_URL env var)",
    )
    parser.add_argument(
        "--llm-api-key",
        default=get_env_default("LLM_API_KEY", "OPENAI_API_KEY"),
        help="API key for the model endpoint (default: LLM_API_KEY/OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--llm-header",
        nargs="+",
        dest="llm_headers",
        help="Additional model API headers in 'Key: Value' format",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=DEFAULT_REQUEST_TIMEOUT_S,
        help=f"Model API request timeout in seconds (default: {DEFAULT_REQUEST_TIMEOUT_S})",
    )

    stdio_group = parser.add_argument_group("stdio options")
    stdio_group.add_argument("-c", "--command", help="Command to run MCP server (stdio only)")
    stdio_group.add_argument("-a", "--args", nargs="+", help="Arguments for the command (stdio only)")
    stdio_group.add_argument("-e", "--env", nargs="+", help="Environment variables in KEY=VALUE format (stdio only)")

    remote_group = parser.add_argument_group("sse/http options")
    remote_group.add_argument("-u", "--url", help="MCP server URL (sse/http only)")
    remote_group.add_argument("-H", "--header", nargs="+", dest="headers", help="HTTP headers in 'Key: Value' format (sse/http only)")

    parser.add_argument("-o", "--output", type=Path, help="Output file for evaluation report (default: stdout)")

    args = parser.parse_args()

    if not args.eval_file.exists():
        print(f"Error: Evaluation file not found: {args.eval_file}")
        sys.exit(1)

    if not args.model:
        parser.error("--model is required unless LLM_MODEL or OPENAI_MODEL is set")
    if not args.llm_base_url:
        parser.error("--llm-base-url is required unless LLM_BASE_URL or OPENAI_BASE_URL is set")

    mcp_headers = parse_headers(args.headers) if args.headers else None
    llm_headers = parse_headers(args.llm_headers) if args.llm_headers else {}
    env_vars = parse_env_vars(args.env) if args.env else None

    client = ChatCompletionClient(
        model=args.model,
        base_url=args.llm_base_url,
        api_key=args.llm_api_key,
        headers=llm_headers,
        timeout_s=args.request_timeout,
    )

    try:
        connection = create_connection(
            transport=args.transport,
            command=args.command,
            args=args.args,
            env=env_vars,
            url=args.url,
            headers=mcp_headers,
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Using model {args.model} via {client.endpoint}")
    print(f"Connecting to MCP server via {args.transport}...")

    async with connection:
        print("✅ Connected successfully")
        report = await run_evaluation(args.eval_file, connection, client)

        if args.output:
            args.output.write_text(report)
            print(f"\n✅ Report saved to {args.output}")
        else:
            print("\n" + report)


if __name__ == "__main__":
    asyncio.run(main())
