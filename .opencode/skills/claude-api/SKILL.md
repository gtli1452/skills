---
name: claude-api
description: Help with OpenCode provider/model setup. TRIGGER when the user asks about `/connect`, `/models`, `opencode.json`, `provider/model-id`, custom OpenAI-compatible providers, `gpt-oss-120b`, Build/Plan or General/Explore model selection, AGENTS.md vs skills, or migrating legacy provider-centric workflows into OpenCode. DO NOT TRIGGER for general SDK coding that is not about OpenCode configuration or workflows.
license: Complete terms in LICENSE.txt
compatibility: opencode
metadata:
  audience: opencode-users
  workflow: provider-model
  target-model: gpt-oss-120b
---

# OpenCode provider/model workflows

This skill keeps the historical `claude-api` name for compatibility, but its job is now OpenCode-native provider, model, and workflow guidance.

## Default stance

- Start with the **provider**, not the model. OpenCode persists selections as `provider/model-id`.
- Treat `gpt-oss-120b` as a **target model exposed by some provider or endpoint**, not as a built-in OpenCode feature.
- Use `/connect` to authenticate, `/models` to discover the exact IDs OpenCode sees, and `opencode.json` to persist defaults and overrides.
- Use OpenCode terms precisely: **Build** and **Plan** are the built-in primary agents/modes; **General** and **Explore** are built-in subagents; `AGENTS.md` stores standing repo instructions; the **skill tool** loads reusable `SKILL.md` workflows on demand.
- Prefer provider-first, OpenAI-compatible patterns. Do not assume vendor-specific SDKs, proprietary artifacts, or single-provider runtime behavior unless the user is explicitly migrating legacy docs.

## Fast routing

Start with `shared/overview.md` for nearly every request, then read only what matches the task:

- **Provider setup, `/connect`, `/models`, `opencode.json`, `provider/model-id`, custom endpoints**
  -> `shared/providers-and-model-ids.md`
- **`gpt-oss-120b` selection, examples, or troubleshooting**
  -> `shared/gpt-oss-120b.md`
- **Build/Plan defaults, General/Explore usage, AGENTS.md, permissions**
  -> `shared/agents-and-permissions.md`
- **Where skills live, what frontmatter to use, AGENTS.md vs SKILL.md**
  -> `shared/skills-layout.md`
- **Migrating legacy prompts, configs, or habits into OpenCode**
  -> `shared/migration-from-claude.md`

If the request spans multiple topics, read `shared/overview.md` first and then the relevant focused docs.

## Response pattern

1. Identify the path:
   - built-in provider
   - OpenCode Zen/Go
   - custom OpenAI-compatible endpoint
   - migration from legacy wording
2. Give the exact `provider/model-id` if it is already known.
3. If the exact ID is unknown, tell the user to run `/models` and use the returned key literally.
4. Provide the smallest `opencode.json` snippet that solves the problem.
5. Only add mode or agent overrides when the user actually needs different Build/Plan or General/Explore behavior.

## Minimal baseline snippet

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "provider/model-id"
}
```

Use `small_model`, `agent`, or `mode` overrides only when the workflow needs them.

## Guardrails

- Never present a bare model name like `gpt-oss-120b` as sufficient by itself when OpenCode needs `provider/model-id`.
- Never guess namespaced or dated IDs when `/models` or provider config can provide the exact answer.
- Keep vendor-specific migration notes in `shared/migration-from-claude.md`. The default path for this skill is OpenCode-first and provider-first.
