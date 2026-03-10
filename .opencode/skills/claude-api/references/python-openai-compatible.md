# Python patterns for OpenAI-compatible APIs

These examples assume the `openai` Python package and an OpenAI-compatible endpoint. Favor chat-completions-style code for maximum portability.

## Install

```bash
pip install openai
```

## Minimal client setup

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "opencode"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
)
model = os.getenv("OPENAI_MODEL", "gpt-oss-120b")
```

## Single request

```python
response = client.chat.completions.create(
    model=model,
    temperature=0,
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Summarize this file in three bullets."},
    ],
)

text = response.choices[0].message.content or ""
```

## Streaming

```python
stream = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Write a long answer."}],
    stream=True,
)

chunks = []
for event in stream:
    delta = event.choices[0].delta.content or ""
    if delta:
        print(delta, end="", flush=True)
        chunks.append(delta)

full_text = "".join(chunks)
```

## Structured JSON with validation

```python
import json

prompt = "Return JSON with keys: title, priority, tags"
response = client.chat.completions.create(
    model=model,
    temperature=0,
    messages=[{"role": "user", "content": prompt}],
)

raw = response.choices[0].message.content or "{}"
data = json.loads(raw)
assert isinstance(data.get("tags"), list)
```

If the provider supports JSON schema mode, you can layer it in later. Keep the plain JSON parser as the portability fallback.

## Tool calling

```python
import json

tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_ticket",
            "description": "Fetch a ticket by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"}
                },
                "required": ["ticket_id"],
            },
        },
    }
]

messages = [{"role": "user", "content": "Check ticket OPS-1042."}]
first = client.chat.completions.create(model=model, messages=messages, tools=tools)
message = first.choices[0].message
messages.append(message.model_dump(exclude_none=True))

for tool_call in message.tool_calls or []:
    args = json.loads(tool_call.function.arguments or "{}")
    result = {"id": args["ticket_id"], "status": "open"}
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        }
    )

final = client.chat.completions.create(model=model, messages=messages, tools=tools)
answer = final.choices[0].message.content or ""
```

## Raw HTTP fallback

If the SDK is missing or incompatible, use `requests.post()` against the configured `OPENAI_BASE_URL`. Keep the same environment contract and JSON payload shape.
