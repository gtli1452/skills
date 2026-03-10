---
name: doc-coauthoring
description: Draft, refine, and reader-test long-form documents with a file-first OpenCode workflow.
---

# Doc Co-Authoring

## Use when
- The user is writing a design doc, RFC, proposal, PRD, ADR, migration plan, or other substantial internal document.
- The work benefits from structured drafting, not just a single polished paragraph.
- The result should live in a real file that can be reviewed, edited, and tested.

## Do not use when
- The request is a short status update, memo, or announcement; use `internal-comms`.
- The user only wants ad hoc writing help and does not need a structured workflow.
- The task is implementation-only and no durable document is required.

## Capability checks and fallbacks
1. Check whether the document already exists.
   - If it does, edit the existing file in place.
   - If not, create the file early and keep the draft there instead of repeatedly reprinting it in chat.
2. Check the repo for templates or conventions.
   - If a docs format already exists, follow it.
   - If not, start from `templates\doc-outline.md` and tailor it quickly.
3. Check how much source context is available.
   - If the repo, notes, or pasted material are enough, draft normally.
   - If context is partial, capture assumptions and unresolved questions explicitly in the document.
4. Check whether fresh-context review is available.
   - If a sub-agent or fresh chat is available, use it for reader testing.
   - If not, use `templates\reader-test-prompt.md` and test the file content in a clean prompt.

## Default workflow
1. Frame the document before writing: audience, desired decision, scope, and deadline.
2. Gather raw material from files, notes, tickets, or pasted context without trying to perfect the prose yet.
3. Create the document scaffold early so edits happen in a stable file.
4. Draft the highest-risk section first: the proposal, technical approach, or key decision.
5. Fill supporting sections: context, goals, non-goals, alternatives, risks, rollout, open questions, and appendix links.
6. Refine with surgical edits to the file rather than rewriting the entire document each round.
7. Run a reader test from fresh context and fix any places where the document assumes too much.
8. Finish with a final pass for flow, redundancy, and factual completeness.

## Resource map
- `templates\doc-outline.md`: generic outline for a durable working draft.
- `templates\reader-test-prompt.md`: a fresh-context review prompt for checking reader comprehension.

## Output contract
Return or create:
- the drafted or updated document file,
- a short summary of unresolved questions or assumptions,
- reader-test findings when that step was run.

## Validation checklist
- The document clearly states what decision, proposal, or plan it is about.
- The intended audience can understand the summary without prior conversation context.
- Assumptions, trade-offs, and open questions are explicit.
- The document lives in a file that can be reviewed asynchronously.
- Reader testing or an equivalent fresh-context pass was performed, or the gap is called out.
