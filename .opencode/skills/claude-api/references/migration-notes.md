# Migration notes from the original Claude-focused skill

This folder keeps the original `claude-api` name for traceability, but the OpenCode version is intentionally provider-neutral.

## What stayed the same

- The skill still targets application code that integrates LLM APIs.
- Language detection, SDK-vs-raw-HTTP choice, streaming, tool loops, and structured output still matter.
- The core advice remains: start simple, validate aggressively, and keep provider assumptions explicit.

## What changed

| Original concept | OpenCode adaptation |
| --- | --- |
| Anthropic Messages API | OpenAI-compatible chat/completions or provider-native equivalent |
| Anthropic SDK helpers | Reuse the SDK already present in the repo, or raw HTTP |
| Claude model defaults | Use the user's configured/default model, often via `OPENAI_MODEL` |
| Claude-only thinking / compaction features | Treat as optional provider extras; never assume portability |
| Anthropic server-side tools | Prefer app-owned tool calling, MCP, or explicit runtime integrations |
| Agent SDK assumptions | Keep file/web/shell tooling outside this skill unless the repo already provides it |

## Practical rule of thumb

- If the repo already imports `openai`, stay in that ecosystem.
- If the repo talks to a gateway or local runtime, keep `base_url` configurable and do not tie the code to a hosted provider.
- If a feature only exists on one provider, document the gap and add a fallback path.
