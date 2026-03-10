# Provider-neutral LLM API checklist

Use this when adapting app code to any OpenAI-compatible or local model endpoint.

## Configuration contract

Prefer environment-driven configuration:

- `OPENAI_API_KEY` — auth token; for local runtimes without auth, use a harmless placeholder if the client requires one.
- `OPENAI_BASE_URL` — custom gateway, local runtime, or proxy.
- `OPENAI_MODEL` — default model selection.
- Provider-specific extras only when unavoidable.

Keep these values out of source code.

## Choose the smallest surface

| Need | Preferred surface | Portable fallback |
| --- | --- | --- |
| Single response | Chat/completions request | Raw HTTP POST |
| Streaming UI | SSE or SDK streaming helpers | Polling or chunked output |
| Tool calling | Native function/tool calling | JSON action loop in app code |
| Structured output | JSON schema / JSON mode | Plain text JSON + validation + retry |
| Files or batches | Provider file/batch APIs | Client-side chunking / job queue |
| Embeddings | Native embedding endpoint | Local embedding service |

## Portability rules

1. Do not hard-code vendor model IDs in library code.
2. Keep `base_url` configurable so hosted and local providers are both possible.
3. Do not assume provider-specific thinking, compaction, or server-hosted tools exist.
4. Parse tool arguments as JSON objects, never with brittle string matching.
5. Validate the final shape before downstream code consumes it.
6. Prefer explicit response parsing over hidden SDK magic when portability matters.

## Error-handling baseline

- `401/403`: bad auth, expired token, or wrong project.
- `404`: wrong base URL or unsupported endpoint shape.
- `429`: retry with backoff and jitter.
- `5xx`: bounded retries with logging.
- Context/window failures: chunk input or summarize upstream.
- Invalid JSON: re-ask with the parse error and expected schema.

## Smoke-test recipe

1. Verify environment variables load correctly.
2. Send one tiny text prompt.
3. If the feature matters, run one streaming request.
4. If tools matter, run a single deterministic tool call.
5. If structured output matters, prove the parser rejects invalid output.
