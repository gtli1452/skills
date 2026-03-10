# Overview

Use this skill for OpenCode questions that are really about **provider setup, model selection, config placement, or workflow wiring** rather than raw SDK code.

## Quick playbook

1. **Choose the provider path**: built-in provider, OpenCode Zen/Go, or a custom OpenAI-compatible endpoint.
2. **Connect credentials** with `/connect` when the provider is not already authenticated.
3. **Discover exact model IDs** with `/models` before hardcoding anything.
4. **Persist defaults** in `opencode.json` with `model`, optional `small_model`, and provider-specific settings.
5. **Only then** add agent or mode overrides for Build/Plan or other custom workflows.

## Where config lives

- **Project config**: `opencode.json` in the repo root. Use this for team-shared defaults.
- **Global config**: `~/.config/opencode/opencode.json`. Use this for personal defaults.
- Project config overrides global config for conflicting keys.

## Minimal examples

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "provider/model-id"
}
```

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "provider/model-id",
  "small_model": "provider/smaller-model-id"
}
```

## OpenCode-native reminders

- `AGENTS.md` is for standing project instructions.
- Skills are reusable task playbooks loaded through the **skill tool**.
- Build/Plan are the built-in primary agents or modes.
- General/Explore are the built-in subagents.
- `gpt-oss-120b` is only usable when a provider exposes it under some exact model key.

## Read next

- Provider wiring and `provider/model-id`: `providers-and-model-ids.md`
- `gpt-oss-120b` specifics: `gpt-oss-120b.md`
- Agents, permissions, and AGENTS.md: `agents-and-permissions.md`
- Skill placement and frontmatter: `skills-layout.md`
- Migration notes: `migration-from-claude.md`
