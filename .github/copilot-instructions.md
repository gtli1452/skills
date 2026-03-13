# Copilot instructions for this repository

## Repository model

- Treat repo-root `skills/` as the Anthropic upstream tree. If the task is about OpenCode adaptations, do **not** rewrite `skills/`; put the adapted copy in `.opencode/skills/<skill>/`.
- Keep the mirror layout exact: `.opencode/skills/<skill>/...`. Never create nested paths like `.opencode/skills/skills/...`.
- If the user references upstream Anthropic skill URLs, commit ranges, or commits, treat them as source material only. In this fork, downstream edits still belong under `.opencode/skills/<skill>/` unless the user explicitly asks to change upstream `skills/`.
- `template/SKILL.md` is the minimal scaffold for new skills. The practical validation rules live in `skills/skill-creator/scripts/quick_validate.py`.

## Validation commands

- There is **no repo-wide build/test/lint pipeline** in this repository. Validate changes per skill.
- Preferred SKILL.md validation:
  - `python skills\skill-creator\scripts\quick_validate.py <skill_dir>`
- `quick_validate.py` depends on `PyYAML`. If that is unavailable, do not mutate the shared environment just to satisfy it. Use targeted checks instead:
  - `git --no-pager diff --check`
  - `python -m py_compile <modified_python_files>`
  - `bash -n <modified_shell_scripts>`
  - `node --check <modified_js_files>`
  - targeted `rg` searches for stale `Anthropic`, `Claude`, `claude.ai`, or other task-specific legacy wording
- If the user supplied a sample file or named output path, validation is not complete until you inspect the generated artifact and verify the specific quality criteria they named.

## Skill file conventions

- Every skill must have `SKILL.md` in the skill root.
- Follow the frontmatter rules enforced by `quick_validate.py`:
  - required: `name`, `description`
  - allowed optional keys: `license`, `allowed-tools`, `metadata`, `compatibility`
- `name` must stay kebab-case and within the validator limits; `description` must stay plain text without angle brackets.

## OpenCode adaptation workflow

- For OpenCode replay/split/migration tasks, start from a clean feature branch based on `main` / upstream baseline unless the user explicitly says to build on an existing branch.
- If the user asks for reviewable history, default to:
  - one setup/baseline commit for copying upstream content into `.opencode/skills/`
  - one commit per changed skill after that
- If you modify a skill and the user did not forbid commits, default to committing the skill update before wrapping up. When one skill goes through multiple reviewable quality iterations, preserve those as separate commits instead of leaving only an uncommitted final state.
- Keep new commits scoped to `.opencode/skills/` unless the user explicitly requests repo-level documentation changes.

## Output and artifact rules

- Default to chat output or session-state notes for analysis. Only create a repo-root markdown/txt report when the user explicitly asks for a file.
- If the user asks for a markdown deliverable, create **one agreed file** and avoid leaving extra draft reports in the repo root.
- If the user asks for a report, converted output, or comparison snapshot without specifying a tracked destination, place it under `tmp/` and keep related iteration artifacts together in a structured subdirectory there.

## Execution bias for this repo

- When the user has already specified the branching, commit, replay, or report format, move directly to implementation. Do not stay in research mode unless there is a concrete blocker.
- When the user gives explicit sample-driven quality goals (for example headings, spanning tables, preserved images, or specific output syntax), treat those as acceptance gates and check the generated files against them before declaring the work done.
- If the user says “ask first if unclear” and they are unavailable, proceed with the safest repo-specific default: preserve upstream `skills/`, work in `.opencode/skills/`, and prefer a fresh branch over mutating a messy one.
