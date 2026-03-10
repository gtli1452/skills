# Migration from Claude-centric workflows

This file is the only place where Anthropic and Claude terminology should appear by default. Everywhere else in this skill should stay OpenCode-first.

## Concept mapping

| Older wording | OpenCode-native replacement |
| --- | --- |
| "Pick Claude Opus/Sonnet first" | Pick a provider, run `/models`, and use the exact `provider/model-id`. |
| `CLAUDE.md` for repo rules | `AGENTS.md` for repo rules. OpenCode can still read `CLAUDE.md` as a fallback if compatibility is enabled. |
| `.claude/skills/` as the default path | `.opencode/skills/` as the default path. |
| Anthropic SDK examples as the primary path | Provider config in `opencode.json`, plus custom OpenAI-compatible providers when needed. |
| Claude-specific built-in artifacts or runtime assumptions | Standard file editing, OpenCode agents, `AGENTS.md`, skills, commands, and config. |

## If the user is still using Anthropic in OpenCode

That is fine, but frame it as **one provider among many**.

- Connect Anthropic with `/connect` if that is still their provider.
- Select the model with `/models`.
- Persist it as `anthropic/model-id` in `opencode.json`.
- Do not make Anthropic the default explanation when the question is really about OpenCode behavior.

## Migration checklist

1. Replace hardcoded Claude model strings with exact `provider/model-id` values.
2. Move standing repo guidance into `AGENTS.md`.
3. Move repeatable task playbooks into skills.
4. Replace Anthropic-only config advice with provider-specific or OpenAI-compatible provider guidance.
5. Re-run `/models` and update configs from the exact output instead of guessing model names.
