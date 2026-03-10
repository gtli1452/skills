---
name: doc-coauthoring
description: Guide users through a structured workflow for co-authoring documentation in OpenCode. Use when a user wants to write documentation, proposals, technical specs, decision docs, or similar structured content. This workflow helps gather context, draft section by section in local files, and test whether a fresh reader session can understand the document.
---

# Doc Co-Authoring Workflow

This skill gives a three-stage process for collaborative document creation in OpenCode. Act as an active guide through:

1. **Context Gathering**
2. **Refinement & Structure**
3. **Reader Testing**

## When to Offer This Workflow

**Trigger conditions:**
- User mentions writing documentation: "write a doc", "draft a proposal", "create a spec", "write up"
- User mentions specific doc types: "PRD", "design doc", "decision doc", "RFC"
- User seems to be starting a substantial writing task that will benefit from structure

**Initial offer:**
Offer the user a structured workflow for co-authoring the document. Explain the three stages:

1. **Context Gathering**: The user shares raw context while you close knowledge gaps
2. **Refinement & Structure**: Build a real draft file section by section
3. **Reader Testing**: Use a fresh reader session or OpenCode child agent to answer questions using only the document

Explain that this approach helps the document work for teammates, future readers, and AI tools that only see the written text. Ask whether they want to use this workflow or work freeform.

If the user declines, work freeform. If the user accepts, proceed to Stage 1.

## Stage 1: Context Gathering

**Goal:** Close the gap between what the user knows and what OpenCode knows so later guidance is genuinely informed.

### Initial Questions

Start by asking for meta-context about the document:

1. What type of document is this? (technical spec, proposal, decision doc, etc.)
2. Who is the primary audience?
3. What do they want the reader to think, decide, or do after reading it?
4. Is there a template or house format to follow?
5. Are there constraints, deadlines, or political considerations to know up front?

Tell the user they can answer in shorthand, paste rough notes, or dump context however is fastest.

### Pulling in Templates and Existing Material

**If the user provides a template or mentions a doc type:**
- Ask whether they have an existing template file, repo path, or exported document to share
- If they provide a local file or path, read it
- If they provide a shared resource that is accessible through connected tools or MCP servers, fetch it
- If it is not accessible, ask them to paste the relevant structure or export the document

**If the document already exists:**
- Read the current version before proposing a rewrite
- Check whether images, diagrams, or screenshots carry important meaning that is not described in text
- If visuals lack alt text or captions, explain that fresh reader sessions only understand what is written down. Offer to draft alt text from uploaded images or user descriptions

### Info Dumping

Once the initial questions are answered, encourage the user to dump all the context they have. Ask for things like:
- Background on the project or problem
- Related discussions, tickets, or earlier documents
- Why alternate solutions are not being used
- Timeline pressure and delivery constraints
- Technical architecture and dependencies
- Stakeholder concerns or objections
- Organizational context that affects the decision

Tell them not to organize it yet. The goal is coverage, not polish.

Offer multiple ways to provide context:
- Stream-of-consciousness notes
- Pointing to repo files, tickets, or docs
- Exported documents or pasted excerpts
- Connected tools or MCP servers, if available

**If this document must match local conventions:**
Once that becomes relevant, read `AGENTS.md` and any obvious style or template files in the repo so the draft matches the environment it will live in.

### During Context Gathering

- If the user points to team threads, shared docs, or related source material:
  - If connected tools are available, read them now
  - If not, ask for pasted excerpts, a local export, or a summary
- If the user references unfamiliar projects, teams, or acronyms:
  - Ask whether you should search the repo, `AGENTS.md`, or connected tools for background
  - Wait for confirmation before broad searches outside the immediately shared material
- As context arrives, keep track of what is now clear and what still needs follow-up

### Asking Clarifying Questions

Once the user has done an initial dump, ask targeted follow-up questions.

Generate 5-10 numbered questions based on the biggest remaining gaps. Focus on:
- Trade-offs
- Audience assumptions
- Risks and edge cases
- Scope boundaries
- Evidence needed to make the document credible

Tell the user they can answer in shorthand, point to more files, or keep info-dumping if that is faster.

### Exit Condition

You have enough context when you can ask about trade-offs, edge cases, and implications without needing basic background re-explained.

### Transition

Ask whether they want to add more context or move on to drafting.

If they want to add more, let them. When ready, proceed to Stage 2.

## Stage 2: Refinement & Structure

**Goal:** Build the document section by section through brainstorming, curation, drafting, and focused edits.

### Working Style

Explain that the document will be built section by section. For each section:

1. Ask clarifying questions
2. Brainstorm options or points worth covering
3. Have the user keep, remove, or combine items
4. Draft the section in the real document
5. Refine it through surgical edits

Use **Plan-style reasoning** to shape the outline and identify unknowns. Use **Build-style execution** to update the source file once there is a direction.

### Choosing a Structure

If the document structure is already clear:
- Ask which section they want to start with
- Suggest starting with the section that still has the most uncertainty

If the user does not yet know the structure:
- Suggest 3-5 sections based on the document type and any template you found
- Ask whether that structure works or should be adjusted

Leave summary and overview sections for later unless the user strongly prefers otherwise.

### Create the Working Draft

Once structure is agreed:

- Create a real markdown file in the working directory or repo
- Name it appropriately (`decision-doc.md`, `technical-spec.md`, `proposal.md`, etc.)
- Add all agreed section headers with brief placeholder text such as `[To be written]`
- Keep this file as the single source of truth for the draft

Announce that the scaffold has been created and that you will now fill it section by section.

### For Each Section

#### Step 1: Clarifying Questions

Announce that you are working on the specific section. Ask 5-10 targeted questions about what belongs there.

Tell the user they can answer in shorthand or just call out what matters most.

#### Step 2: Brainstorming

Brainstorm 5-20 things that might belong in the section, depending on complexity. Look for:
- Context that may have been mentioned once and then forgotten
- Trade-offs or objections worth making explicit
- Missing evidence or examples

Offer to brainstorm more if they want additional options.

#### Step 3: Curation

Ask which items should be kept, removed, or combined.

Examples:
- `Keep 1,4,7`
- `Remove 3 (duplicates 1)`
- `Combine 5 and 6`
- `Keep the idea from 8 but make it more cautious`

If the user responds freeform, extract the preference and proceed.

#### Step 4: Gap Check

Ask whether anything important is still missing from the section before drafting.

#### Step 5: Drafting

Replace the placeholder text for that section with a real draft in the document file.

After drafting:
- Confirm the file was updated
- Ask the user to read the new section and say what should change
- On the first section, explain that asking for changes is usually better than silently rewriting it themselves, because their edits teach you their preferences for later sections

#### Step 6: Iterative Refinement

As the user gives feedback:
- Make focused edits to the file instead of reprinting the whole document
- Confirm each edit is complete
- If the user edits the file directly and asks you to re-read it, read the file and learn from the changes

Continue until they are satisfied with that section.

### Quality Checking

After several rounds with no substantial changes, ask whether anything can be removed without losing meaning.

When a section is complete, confirm it and ask whether they want to move to the next section.

Repeat for all sections.

### Near Completion

Once most sections are done:
- Re-read the whole document
- Check for flow, consistency, contradictions, and repetition
- Look for filler or vague phrasing that should be tightened
- Make sure each section earns its place

When all sections are drafted and refined, ask whether they are ready for Reader Testing or want one more editing pass first.

## Stage 3: Reader Testing

**Goal:** Test the document with a fresh reader that sees only the document, not the history that produced it.

Explain that this catches blind spots: things that make perfect sense to the authors but are unclear to everyone else.

### Testing Approach

#### If OpenCode Child Agents Are Available

Use fresh child sessions directly.

**Preferred agent choice:**
- Use **@explore** for read-only comprehension checks
- Use **@general** for deeper ambiguity analysis, contradiction checks, or multi-file reasoning

##### Step 1: Predict Reader Questions

Generate 5-10 realistic reader questions someone might ask when trying to understand or find the document.

##### Step 2: Run Fresh-Reader Checks

For each question, create a fresh child session that gets only:
- The document file or pasted document content
- The single reader question

Do not pass along the drafting conversation.

For each result, summarize:
- What the reader answered correctly
- What it misunderstood
- What knowledge the document assumed without stating

##### Step 3: Run Additional Checks

Ask a fresh child session to inspect the document for:
- Ambiguity
- Hidden assumptions
- Contradictions
- Missing definitions or context

Summarize the issues it finds.

##### Step 4: Report and Fix

If the fresh reader struggles:
- List the specific issues
- Say which sections need revision
- Loop back to Stage 2 for those sections

#### If Child Agents Are Not Practical

Have the user do a manual fresh-reader pass.

##### Step 1: Predict Reader Questions

Generate 5-10 realistic reader questions.

##### Step 2: Set Up a Fresh Session

Ask the user to open a fresh OpenCode session, or any clean reader environment with no prior context, and give it only the document.

If they are in OpenCode, a new **Plan** session is often a good choice because it encourages read-only analysis.

##### Step 3: Ask the Reader

For each question, ask the fresh reader to provide:
- The answer
- Anything that was ambiguous or unclear
- What background knowledge the document seems to assume

Also ask:
- "What in this doc might confuse a new reader?"
- "What context does this doc assume but never states?"
- "Are there contradictions or inconsistencies?"

##### Step 4: Iterate

Collect what the fresh reader got wrong or struggled with, then loop back to Stage 2 to patch those gaps.

### Exit Condition

Reader Testing is done when a fresh reader can consistently answer the questions correctly and stops surfacing new gaps or ambiguities.

## Final Review

When Reader Testing passes:

1. Recommend that the user do one final read-through themselves
2. Suggest double-checking facts, links, dates, and technical details
3. Ask whether the document achieves the impact they originally wanted

If they want another pass, do it. Otherwise, announce completion and offer a few final tips:
- Keep appendices for detail that would otherwise bloat the main narrative
- Update the document as real readers give feedback
- If useful, keep links to tickets, source material, or prior decisions near the document for future readers

## Tips for Effective Guidance

**Tone:**
- Be direct and procedural
- Explain rationale briefly when it changes the user's behavior
- Do not oversell the workflow; just execute it

**Handling deviations:**
- If the user wants to skip a stage, let them
- If they are frustrated, acknowledge the trade-off and suggest a faster path
- Always preserve user agency over the process

**Context management:**
- Do not let unclear references pile up
- Ask about missing context as soon as it matters
- Read `AGENTS.md` or local style docs only when they become relevant to the document

**File management:**
- Create the real draft file early
- Keep one source-of-truth document
- Make focused edits instead of rewriting the whole thing in chat
- Do not create side files for brainstorming lists unless the user explicitly wants them

**Quality over speed:**
- Do not rush the stages
- Each iteration should improve understanding, structure, or clarity
- The goal is a document that actually works for readers
