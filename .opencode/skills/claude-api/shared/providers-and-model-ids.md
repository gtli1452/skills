# Providers and model IDs

## Core rules

- OpenCode stores the selected model as `provider/model-id`.
- The **provider key** is the left side of that string.
- The **model key** is the right side. For custom providers, this is usually the key under `provider.<provider>.models`.
- A model's display `name` is for humans. The config key is what OpenCode uses.
- If your backend needs a different canonical identifier, add `id`; otherwise keep the config key equal to the backend model ID.

## Built-in provider flow

1. Run `/connect` and authenticate the provider.
2. Run `/models` and copy the exact full ID OpenCode shows.
3. Persist it in `opencode.json`.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "provider/model-id"
}
```

For one-off checks, you can also use the full ID directly from the CLI:

```bash
opencode run "summarize this repo" --model provider/model-id
```

## Custom OpenAI-compatible provider pattern

When the provider is not built in, define it explicitly and expose the models you want OpenCode to know about.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "local-openai": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Local OpenAI-compatible endpoint",
      "options": {
        "baseURL": "http://127.0.0.1:1234/v1",
        "apiKey": "{env:LOCAL_OPENAI_API_KEY}"
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

### Notes on that pattern

- `local-openai` is your provider key; pick a stable name and reuse it everywhere.
- `baseURL` must point at the endpoint's `/v1`-style root.
- The model key under `models` becomes the right side of `provider/model-id` unless you intentionally map it with `id`.
- Add `apiKey` only when the endpoint requires it.
- Add limits or model-specific options only if you know the backend supports them.

## Troubleshooting

- **`/models` does not show the model**: the provider is not connected, is disabled, or the model was never declared for a custom provider.
- **The wrong model keeps loading**: check CLI flags first, then project `opencode.json`, then global config, then the last-used model.
- **You only know the bare model name**: do not guess. Ask for the provider or have the user run `/models`.
- **A provider uses namespaced model IDs**: keep the exact key returned by the provider. Do not simplify it unless you are intentionally remapping it in `provider.<name>.models`.
