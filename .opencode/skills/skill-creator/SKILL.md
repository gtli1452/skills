---
name: skill-creator
description: Create, rewrite, benchmark, and package OpenCode skills, including eval design, with-skill versus baseline comparisons, review UIs, and description tuning for better skill matching.
license: See LICENSE.txt
---

# Skill Creator

This OpenCode adaptation keeps the core loop from the source skill—draft, test, review, improve, repeat—but removes source-runtime-specific assumptions and product-specific branches.

## Use when
- Turning a repeatable workflow into a reusable OpenCode skill.
- Improving an existing skill that already has real user prompts or evals.
- Running with-skill versus baseline comparisons to prove a skill adds value.
- Packaging a finished skill or tightening its description for better matching.

## Do not use when
- The task is a one-off prompt, document, or script with no reuse value.
- The user only wants general advice about prompt writing, not a packaged skill.
- There is no meaningful way to evaluate success and the user does not want iteration.

## Capability checks and fallbacks
- If sub-agents are available, run with-skill and baseline evals in parallel; otherwise run them sequentially and note the confidence is lower.
- If a browser cannot be opened, use `eval-viewer\generate_review.py --static <output.html>` and hand the HTML file to the user.
- If no OpenAI-compatible model endpoint is configured (`OPENAI_API_KEY`, optional `OPENAI_BASE_URL`), skip automated description optimization and do manual candidate comparison with the eval review UI.
- If timing or token metadata is unavailable in the runtime, benchmark pass rate and qualitative findings only.
- If the original skill location is read-only, copy it into a writable workspace before editing.
- If packaging into a `.skill` file is not useful in the current environment, return the validated folder or a zip and explain how to install it manually.

## Default workflow
1. Capture the skill's purpose, trigger conditions, expected outputs, and important edge cases.
2. Draft or update `SKILL.md`, then move repeated heavy logic into `scripts\`, `references\`, or `assets\`.
3. Create 2-3 realistic evals in `evals\evals.json` and save per-run metadata in `<skill-name>-workspace\iteration-N\eval-*\eval_metadata.json`.
4. Execute each eval with the candidate skill and a baseline (`without_skill` for new skills, or the previous/original version for updates).
5. While runs execute, write objective expectations and attach them to the eval metadata.
6. Grade runs with `agents\grader.md`, then aggregate results with `scripts\aggregate_benchmark.py`.
7. Generate a review UI with `eval-viewer\generate_review.py`, collect feedback, inspect transcripts, and turn repeated work into reusable bundled scripts.
8. Iterate until the user is satisfied or improvements flatten out.
9. Optionally run `scripts\run_loop.py` to tune the description with an OpenAI-compatible model; treat its score as a proxy for matching quality, then sanity-check the winner manually.
10. Package the final skill with `scripts\package_skill.py` if the user wants a distributable artifact.

## Resource map
- `agents\grader.md` — grade expectations against transcripts and outputs.
- `agents\comparator.md` — blind A/B output comparison.
- `agents\analyzer.md` — post-hoc analysis of why one version won.
- `references\schemas.md` — JSON formats for eval metadata, grading, timing, and benchmarks.
- `assets\eval_review.html` — editable trigger-query review template.
- `eval-viewer\generate_review.py` and `eval-viewer\viewer.html` — human review UI for outputs and benchmarks.
- `scripts\quick_validate.py` — frontmatter validation.
- `scripts\aggregate_benchmark.py` — summarize per-run grading.
- `scripts\generate_report.py` — HTML report for description tuning.
- `scripts\run_eval.py`, `scripts\improve_description.py`, `scripts\run_loop.py` — OpenAI-compatible description-tuning workflow.
- `scripts\package_skill.py` — create a `.skill` archive.

## Output contract
- Deliver a valid skill folder with bundled resources that match the workflow.
- If evals ran, report the workspace path, benchmark summary, and review artifact path.
- If description tuning ran, show the original description, best candidate, and why it won.
- Surface missing eval coverage or tool limitations instead of hiding them.

## Validation checklist
- Frontmatter is valid and the description is short, discriminative, and specific.
- Evals are realistic and include at least one discriminating baseline comparison.
- Outputs, transcripts, and grading files are organized per iteration.
- Repeated helper logic has been extracted into scripts or references.
- Automated description tuning is clearly labeled as a proxy, not ground truth.
- Packaged artifacts exclude transient eval outputs unless the user explicitly wants them bundled.
