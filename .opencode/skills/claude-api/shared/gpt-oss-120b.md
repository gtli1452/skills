# gpt-oss-120b in OpenCode

`gpt-oss-120b` is a **target model**, not a built-in OpenCode capability.

## What that means in practice

- If a hosted provider already exposes it, use the exact `provider/model-id` shown by `/models`.
- If you run it behind a local or custom OpenAI-compatible endpoint, define a provider block and expose a model key yourself.
- If the provider uses a different key such as `openai/gpt-oss-120b` or another namespace, use that exact key. OpenCode cares about the configured ID, not the marketing name.

## Fast path

1. `/connect` to the provider if needed.
2. `/models` to see whether `gpt-oss-120b` is already available.
3. Set the default model in `opencode.json`.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "myprovider/gpt-oss-120b"
}
```

## Local or proxy example

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "local-openai": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Local OpenAI-compatible endpoint",
      "options": {
        "baseURL": "http://127.0.0.1:1234/v1"
      },
      "models": {
        "gpt-oss-120b": {
          "name": "GPT-OSS 120B"
        }
      }
    }
  },
  "model": "local-openai/gpt-oss-120b"
}
```

## Good defaults

- Use the full `provider/model-id` everywhere: config, CLI flags, and agent overrides.
- Let Build use `gpt-oss-120b` only when its latency and cost fit the workflow.
- Pair it with `small_model` or a cheaper Plan default only if the same provider offers an appropriate secondary model.
- Treat reasoning, verbosity, or other advanced options as **provider-specific**. Only set them when the provider docs or `/models` output supports them.

## Avoid these mistakes

- Saying "OpenCode has gpt-oss-120b built in."
- Writing `"model": "gpt-oss-120b"` without a provider.
- Assuming every provider exposes the same key or the same options.
