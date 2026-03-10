# Skills layout

## Where OpenCode looks for skills

Use one folder per skill and place a `SKILL.md` inside it.

- Project skills: `.opencode/skills/<name>/SKILL.md`
- Global skills: `~/.config/opencode/skills/<name>/SKILL.md`
- Compatibility paths also exist for `.claude/skills/` and `.agents/skills/`, but `.opencode/skills/` is the default OpenCode-native location.

## Frontmatter rules

Recognized fields:

- `name` (required)
- `description` (required)
- `license` (optional)
- `compatibility` (optional)
- `metadata` (optional string-to-string map)

The `name` should match the folder name and stay kebab-case.

## AGENTS.md vs SKILL.md vs opencode.json

- Use **`AGENTS.md`** for standing rules that should always be in context for this repo.
- Use **`SKILL.md`** for a reusable workflow that should load on demand through the skill tool.
- Use **`opencode.json`** for runtime behavior such as providers, models, permissions, modes, and agents.

## Minimal skill example

```markdown
---
name: provider-help
description: Help configure providers and model IDs in OpenCode.
compatibility: opencode
metadata:
  audience: maintainers
  workflow: config
---

# What I do

- Explain `/connect` and `/models`
- Draft `opencode.json` snippets
- Clarify `provider/model-id`
```

## Authoring guidance

- Put the trigger logic in the description so the skill tool can pick it correctly.
- Keep the top-level `SKILL.md` concise and push deeper details into support docs.
- Use support docs for progressive disclosure rather than stuffing every example into the front file.
- When a skill is specifically about OpenCode, prefer OpenCode-native names and paths even if legacy compatibility fallbacks still work.
