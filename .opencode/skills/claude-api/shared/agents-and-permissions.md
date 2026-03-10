# Agents, modes, and permissions

## Built-in OpenCode vocabulary

- **Build**: the default primary agent or mode with full tool access.
- **Plan**: the restricted primary agent or mode for analysis and planning.
- **General**: a built-in subagent for multi-step work.
- **Explore**: a built-in read-only subagent for fast codebase exploration.

Use these names directly instead of inventing vendor-specific terminology.

## Where different instructions belong

- **`AGENTS.md`**: standing project rules and repo conventions.
- **`opencode.json`**: models, providers, permissions, tools, and agent or mode overrides.
- **Skill folders**: reusable, discoverable workflows loaded by the skill tool.

## Minimal mode override pattern

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "local-openai/gpt-oss-120b",
  "mode": {
    "build": {
      "model": "local-openai/gpt-oss-120b"
    },
    "plan": {
      "model": "local-openai/gpt-oss-120b",
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    }
  }
}
```

Use a different Plan model only when you actually want a smaller, cheaper, or more restrictive planning setup.

## Skill permissions

The skill tool can be allowed, denied, or set to ask through `permission.skill`.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "skill": {
      "*": "allow",
      "experimental-*": "ask"
    }
  }
}
```

## Practical guidance

- Put repo-wide coding rules in `AGENTS.md`, not inside every skill.
- Use skills for reusable workflows like release prep, provider setup, or code review checklists.
- Use General when you want a broad subagent to execute or research multi-step work.
- Use Explore when you want read-only code search and fast answers.
- Keep provider or model changes in config, not buried in prose documents.
