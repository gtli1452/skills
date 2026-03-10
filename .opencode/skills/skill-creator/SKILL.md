---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance in OpenCode. Use when users want to create a skill from scratch, edit or optimize an existing skill, run evals to test a skill, benchmark different versions, or improve a skill's description so the OpenCode skill tool loads it at the right time.
---

# Skill Creator

A skill for creating new skills and iteratively improving them in OpenCode.

At a high level, the process looks like this:

- Decide what you want the skill to do and when the `skill` tool should load it
- Draft or revise the skill
- Create a few realistic test prompts and run OpenCode with the skill available
- Help the user review results qualitatively and quantitatively
- Rewrite the skill based on those results
- Repeat until the skill is clearly helping
- Optionally optimize the frontmatter description for better triggering

Your job when using this skill is to figure out where the user is in that loop and help them make concrete progress. Sometimes that means drafting from scratch. Sometimes it means going straight to evals, review, and iteration.

If the user wants to work loosely and skip formal evals, that is allowed. Use judgment.

## Communicating with the user

People using this skill will vary widely in how technical they are. Use plain language by default.

- "Evaluation" and "benchmark" are usually fine, but explain them briefly if needed
- Words like "JSON", "assertion", and "baseline" should be introduced only when helpful
- If you are unsure whether the user knows a term, define it in one sentence and keep moving

## Creating a skill

### Capture Intent

Start by understanding the user's goal. The current conversation may already contain the workflow they want to capture. If so, extract as much as you can before asking new questions:
- the sequence of steps
- tool usage patterns
- input and output formats
- corrections the user made
- success criteria they care about

Then fill in the gaps.

1. What should this skill enable OpenCode to do?
2. When should the `skill` tool load it? What user phrases or contexts should trigger it?
3. What output format should the skill usually produce?
4. Should this skill include test cases and formal evals?
5. Does it depend on repo conventions, `AGENTS.md`, or existing examples?

### Interview and Research

Ask about edge cases, failure modes, example files, dependencies, and success criteria before writing test prompts.

Research in parallel where it helps:
- Use **Explore** child agents for fast read-only codebase or documentation discovery
- Use **General** child agents for multi-step research or more involved comparisons
- Read `AGENTS.md`, nearby docs, and example files when they are relevant
- Check available MCP servers if they can supply missing context

Come back with context so the user is not forced to rediscover facts you could have gathered yourself.

### Write the SKILL.md

Based on the interview, fill in these components:

- **name**: The skill identifier
- **description**: The primary trigger text. In OpenCode, this is what appears in the `skill` tool list and is the main thing the agent sees before deciding whether to load the skill
- **compatibility**: Optional. Use `opencode` when the skill assumes OpenCode-specific behavior
- **the rest of the skill**: The actual workflow and guidance

Descriptions should be explicit and a little pushy. OpenCode agents will often skip a helpful skill if the description is timid.

For example, instead of:

> How to build a simple fast dashboard to display internal company data.

Prefer something like:

> Build a simple, fast dashboard for internal company data and metrics. Use this skill whenever the user mentions dashboards, data visualization, internal metrics, reporting, or wants company data presented visually, even if they do not explicitly ask for a dashboard.

### Skill Writing Guide

#### Anatomy of a skill

```text
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled resources (optional)
    ├── scripts/    - Deterministic or repetitive helpers
    ├── references/ - Docs loaded on demand
    └── assets/     - Templates and other supporting files
```

#### Progressive disclosure in OpenCode

Skills load in layers:

1. **`name` + `description`** appear in the `skill` tool's available list
2. **SKILL.md body** is loaded when OpenCode chooses that skill
3. **Bundled resources** are read or executed only when needed

This means:
- Keep the description sharp and easy to recognize
- Keep `SKILL.md` readable and navigable
- Push bulky detail into references or scripts

#### `AGENTS.md` vs `SKILL.md`

Use `AGENTS.md` for repo-wide instructions, build/test commands, and team conventions.

Use `SKILL.md` for reusable workflows that should follow the user or task across sessions.

If a skill depends on local conventions, tell the skill to read `AGENTS.md` or specific files on demand instead of copying the entire ruleset into the skill itself.

#### Principle of lack of surprise

Skills must not contain malware, exploit code, or instructions that would violate the user's intent. Do not help create misleading or harmful skills.

#### Writing patterns

Prefer the imperative form.

**Defining output formats**

```markdown
## Report structure
Use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern**

```markdown
## Commit message format
**Example 1**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing Style

Explain *why* the steps matter instead of leaning entirely on rigid MUST/NEVER language. Skills work best when the agent understands the reasoning behind the instructions.

### Quick validation

After drafting or editing a skill, run the lightweight validator if it is available:

```bash
python -m scripts.quick_validate <path-to-skill>
```

This is a cheap frontmatter and structure sanity check before you spend time on deeper evals.

### Test Cases

After writing the draft, create 2-3 realistic prompts that resemble what a real user would actually say. Share them with the user and let them adjust the set.

Save prompts to `evals/evals.json`. Do not write assertions yet.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema.

## Running and evaluating test cases

Treat this as one connected workflow. Do not stop halfway through and call it done.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`, etc.) and within each iteration by eval (`eval-0/`, `eval-1/`, etc.). Create directories as you go.

### Step 1: Launch paired runs

If OpenCode child agents are available, start all with-skill and baseline runs in the same turn so they finish around the same time.

**Agent choice**
- Prefer **General** for execution-heavy or file-producing evals
- Use **Explore** only when the eval is mostly read-only analysis or discovery

**Make the skill discoverable**
- Run the eval in a workspace where the skill is available through `.opencode/skills/`, `.agents/skills/`, or the current project
- If you want to eliminate ambiguity, manually load the skill with the `skill` tool at the start of the with-skill run

**With-skill run**

```text
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user actually cares about>
```

**Baseline run**
- **Creating a new skill**: Same prompt, same files, no skill loaded. Save to `without_skill/outputs/`
- **Improving an existing skill**: Snapshot the original or prior version, use that as the baseline, and save to `old_skill/outputs/`

Write an `eval_metadata.json` for each eval directory and give the eval a descriptive name.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: Draft assertions while runs are active

Do not sit idle while the runs execute.

Draft quantitative assertions for each eval and explain them to the user. Assertions should be:
- objectively verifiable
- clearly named
- visible enough that a human skimming the viewer understands what they check

Subjective skills (tone, design taste, artistic output) often need human review more than formal assertions. Do not force brittle assertions onto subjective work.

Update both `eval_metadata.json` and `evals/evals.json` once the assertions are drafted.

### Step 3: Capture timing data

When each child session or task finishes, capture timing and token information if your OpenCode environment exposes it through session metadata, task completion details, or exported stats.

Save it immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

If exact token counts are not available, still record start/end times and whatever duration fields you can obtain.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run** — use a **General** child agent (or grade inline) that follows `agents/grader.md` and writes `grading.json` in each run directory. The viewer expects expectation entries to use the exact fields `text`, `passed`, and `evidence`

2. **Aggregate into benchmark** — run:

   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

   This produces `benchmark.json` and `benchmark.md`

3. **Do an analyst pass** — read the aggregate output and use `agents/analyzer.md` to surface patterns the summary can hide, such as weak assertions, flaky evals, or token/time trade-offs

4. **Launch the viewer** — use the bundled review tool instead of custom HTML:

   ```bash
   python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json
   ```

   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Headless or no-browser environments:** use `--static <output_path>` to write a standalone HTML file instead of starting a local server. When the user clicks **Submit All Reviews**, the static viewer downloads `feedback.json`; copy that file into the workspace before the next iteration

5. **Tell the user what to review** — explain that the Outputs tab is for qualitative review and the Benchmark tab is for the quantitative comparison

### What the user sees in the viewer

The **Outputs** tab shows one test case at a time:
- **Prompt**
- **Output**
- **Previous Output** (iteration 2+)
- **Formal Grades** (if grading was run)
- **Feedback** textbox
- **Previous Feedback** (iteration 2+)

The **Benchmark** tab shows pass rates, timing, token usage, and analyst observations.

Navigation is by prev/next buttons or arrow keys. When done, the user clicks **Submit All Reviews**, which saves `feedback.json`.

### Step 5: Read the feedback

When the user says they are done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback usually means the user thought that output was fine. Focus improvement effort on runs with explicit complaints.

If you started a local review server, stop it with the normal process controls for your shell or environment when you are done with it.

## Improving the skill

This is the heart of the loop. You have test outputs, human feedback, and formal grades. Now make the skill better.

### How to think about improvements

1. **Generalize from the feedback**

   Avoid overfitting to the three examples you happened to test. The point is to build a reusable workflow, not memorize test answers

2. **Keep the prompt lean**

   Remove parts of the skill that are not pulling their weight. If the transcripts show the agent doing busywork, rewrite the skill so it stops encouraging that behavior

3. **Explain the why**

   LLMs do better when they understand why a step matters. Replace rigid language with reasoning whenever possible

4. **Bundle repeated work**

   If multiple child runs independently write the same helper script or repeat the same multi-step pattern, that is strong evidence the skill should include a bundled script or tighter instructions

### The iteration loop

After improving the skill:

1. Apply the changes
2. Rerun all test cases into `iteration-<N+1>/`
3. Launch the viewer again, using `--previous-workspace` for comparison
4. Wait for the user to review
5. Read feedback, improve again, and repeat

Stop when:
- the user says they are happy
- feedback is empty across the board
- or you are no longer making meaningful progress

## Advanced: Blind comparison

If the user wants a stricter comparison between two versions of a skill, use the blind comparison workflow. Read:
- `agents/comparator.md`
- `agents/analyzer.md`

The idea is simple: compare outputs without revealing which version produced them, then analyze why the winner won.

This is optional and usually only worth doing when the user explicitly wants a tougher comparison.

## Description Optimization

The `description` field in `SKILL.md` frontmatter is how OpenCode exposes the skill in the `skill` tool list. After creating or improving a skill, offer to optimize that description.

### Step 1: Generate trigger eval queries

Create around 20 eval queries with a mix of should-trigger and should-not-trigger examples.

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

These should sound like real OpenCode users working in **Build** or **Plan** mode, not abstract textbook prompts.

Bad:
- `"Format this data"`
- `"Extract text from PDF"`
- `"Create a chart"`

Good:
- `"ok so my boss just sent me this xlsx file in downloads called Q4 sales final FINAL v2.xlsx and wants a profit margin column added. revenue is in col C and costs are in D i think"`

For **should-trigger** queries:
- cover the main workflow from different angles
- include formal and casual phrasings
- include near-misses where this skill should still win

For **should-not-trigger** queries:
- focus on tricky near-neighbors, not obviously irrelevant tasks
- try cases that share keywords but actually need another skill or a basic built-in tool

### Step 2: Review with the user

Use the HTML template in `assets/eval_review.html`:

1. Read the template
2. Replace:
   - `__EVAL_DATA_PLACEHOLDER__`
   - `__SKILL_NAME_PLACEHOLDER__`
   - `__SKILL_DESCRIPTION_PLACEHOLDER__`
3. Write the filled template to a temp file
4. Open it in a browser if possible, or save the path and ask the user to open it manually
5. If a browser is not practical, review the JSON inline with the user instead
6. Read the exported `eval_set.json` from the chosen download location

This matters. Bad queries lead to bad descriptions.

### Step 3: Run the optimization loop

Tell the user this takes a while, then save the eval set and run:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model openai/gpt-oss-120b \
  --max-iterations 5 \
  --verbose
```

`--model` accepts any OpenCode provider/model ID. `openai/gpt-oss-120b` is a good default example when you want a concrete choice.

How the scripts work:
- `run_eval.py` launches isolated `opencode run --format json` sessions with the candidate skill mounted under `.opencode/skills/`
- it watches raw JSON tool events and records whether the `skill` tool loaded the target skill
- `improve_description.py` uses the same OpenCode CLI path to ask for revised descriptions based on failures

While the loop runs, tail the output and keep the user updated on iteration count and scores.

### How skill triggering works

In OpenCode, skills appear in the `skill` tool description with their `name` and `description`. The agent decides whether to load a skill from that information.

Important implication: trivial one-step requests often will not load a skill even if the wording matches, because **Build** or **Plan** can handle the task directly with basic tools. Use substantive eval queries that reflect situations where loading the skill is actually helpful.

### Step 4: Apply the result

Take `best_description` from the loop output, update the skill frontmatter, and show the user:
- before vs after
- best score
- any important trade-offs you noticed

## Package and present

If the user wants a distributable bundle, run:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

Then tell them where the resulting `.skill` file was written.

## Environment-specific guidance

### OpenCode with child agents

- Use **Build** in the main session for edits and shell commands
- Use **Plan** when you want read-only review before changing the skill again
- Use **General** for execution-heavy eval runs and grading
- Use **Explore** for fast discovery and read-only research
- Generate the review viewer before doing another edit pass so the human sees concrete outputs first

### Single-session or headless environments

- If child agents are unavailable or unreliable, run eval prompts one at a time in fresh OpenCode sessions
- Use `--static` for the review viewer when there is no browser or no local server access
- If baselines are not meaningful or too expensive, lean more heavily on human qualitative review
- Description optimization requires the `opencode` CLI and access to the `skill` tool. If those are unavailable, skip that stage and explain why

### Updating an existing skill

The user may want to update an existing installed skill rather than create a new one.

- Preserve the original skill name
- If the installed location is read-only, copy the skill to a writable temp directory before editing
- Package from the writable copy if needed

## Reference files

The `agents/` directory contains instructions for specialized child-agent tasks:
- `agents/grader.md` — grade assertions against outputs
- `agents/comparator.md` — run blind A/B comparisons
- `agents/analyzer.md` — explain why one version beat another

The `references/` directory contains additional docs:
- `references/schemas.md` — JSON structures for evals, grading, timing, and benchmarks

## Core loop recap

- Figure out what the skill should do
- Draft or revise the skill
- Run OpenCode with the skill available on realistic prompts
- Let the user review outputs and benchmarks
- Improve the skill
- Repeat until it is genuinely helpful
- Package it if the user wants a distributable bundle

If you have a todo tool, use it so you do not forget steps in the loop.
