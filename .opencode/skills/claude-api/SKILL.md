---
name: claude-api
description: Build or debug provider-neutral LLM API integrations for OpenCode projects, especially OpenAI-compatible or local endpoints, streaming, tool calling, structured JSON, files, and batch workflows.
license: See LICENSE.txt
---

# OpenCode LLM API Builder

This is the OpenCode adaptation of the original `claude-api` skill. Preserve the original intent—help with application code that talks to language models—but default to provider-neutral, OpenAI-compatible, and local-runtime-friendly patterns instead of Anthropic-only assumptions.

## Use when
- The task is to add, refactor, or debug LLM API calls in app code.
- The repo already uses `openai`, `litellm`, raw HTTP, or another OpenAI-compatible client.
- The user asks for streaming, tool/function calling, JSON output, embeddings, files, or batches.
- The user mentions base URLs, model IDs, API keys, provider switching, or local model runtimes.

## Do not use when
- The task is pure prompt writing, model training, or unrelated ML/data-science work.
- The request is about a provider-specific SDK surface that must remain vendor-locked with no portability work.
- The repo already has a stable abstraction and only needs unrelated business logic.

## Capability checks and fallbacks
- Detect the project language first and prefer the SDK already present in the repo.
- If the endpoint is OpenAI-compatible, prefer `chat.completions`-style code for maximum portability; if not, map the same workflow onto the provider's native SDK.
- If native tool calling is unavailable, fall back to app-managed JSON actions and explicit execution loops.
- If schema-constrained output is unavailable, validate plain JSON text and retry on parse errors.
- If provider file or batch APIs are unavailable, chunk work client-side and orchestrate multiple requests.
- If live docs are unavailable, use the bundled reference files in `references\`.
- Default model choice: use the repo or environment's configured model (`OPENAI_MODEL` or equivalent). Do not hard-code a vendor model unless the user explicitly asks for one.

## Default workflow
1. Detect the language, dependency set, and existing client abstraction.
2. Choose the smallest integration surface that fits the task: single call, streaming UI, tool loop, structured JSON, embeddings, files, or batch processing.
3. Normalize config around environment variables such as `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`.
4. Implement the minimal working call first, then layer on retries, timeouts, and error handling.
5. Validate every boundary: request schema, tool arguments, and final parsed output.
6. For agentic flows, prefer explicit tools and an app-controlled loop over hidden magic.
7. Add a smoke test or runnable example that proves auth, model selection, and parsing all work.
8. Leave a short note documenting any provider-specific assumptions that remain.

## Resource map
- `references\provider-checklist.md` — portability checklist and feature-selection matrix.
- `references\python-openai-compatible.md` — Python examples for chat, streaming, structured output, and tools.
- `references\typescript-openai-compatible.md` — TypeScript/Node equivalents.
- `references\migration-notes.md` — traces the original folder intent and maps Claude-era concepts to OpenCode-friendly ones.

## Output contract
- Deliver working code, not just pseudo-code.
- Keep secrets in config or environment variables, never inline.
- Include one concrete invocation example or smoke-test command.
- Clearly state which endpoint shape the patch expects.

## Validation checklist
- The chosen client matches the repo language and dependency set.
- Base URL, API key, and model name are configurable.
- Tool/function inputs are validated and parseable.
- Streaming paths handle partial output cleanly.
- Structured output is parsed and validated instead of trusted blindly.
- Retries, timeouts, and rate-limit handling are sensible.
- Existing tests or build steps still pass, or any gap is explicitly called out.
