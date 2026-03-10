---
name: pptx
description: Use when a local PowerPoint file (.pptx) is the main input or output, including reading slide content, updating an existing deck, building a new presentation, reusing a template, or validating slide layout after edits.
---

# PPTX workflows

Assume local files under the user's control. Prefer deterministic unpack/edit/pack steps and explicit visual QA.

## Use when
- A `.pptx` is the source, template, or deliverable.
- The task requires creating slides, updating deck content, reusing template layouts, extracting slide text, or visually QAing a presentation.
- You need to duplicate, delete, reorder, or repair slides without relying on manual GUI-only work.

## Do not use when
- The primary deliverable is a PDF, Word document, spreadsheet, or HTML report.
- The job is only to summarize content and there is no need to touch the presentation file itself.
- The workflow depends on online presentation services.

## Capability checks and fallbacks
1. Check the input deck or template and confirm the desired output path.
2. Check available tooling:
   - `python -m markitdown --help` for text extraction
   - `python scripts\thumbnail.py --help` for visual template mapping
   - `python scripts\office\soffice.py --help` and `pdftoppm -h` for slide renders
   - `node -e "require('pptxgenjs'); console.log('pptxgenjs ok')"` when creating from scratch
3. Fallbacks:
   - If `markitdown` is unavailable, unpack the deck and read slide XML directly
   - If `pptxgenjs` is unavailable, prefer adapting a template or editing XML instead of inventing a binary format
   - If image rendering is unavailable, do content QA with extracted text and note that visual validation was limited

## Default workflow
1. Decide between a template-based edit and a from-scratch build.
2. For template-based work, read `editing.md`, then analyze with `thumbnail.py` and `markitdown`, unpack, make structural changes, edit slide XML, clean, and pack.
3. For new decks, read `pptxgenjs.md`, generate the presentation, then run QA.
4. Perform two QA passes:
   - content QA with `python -m markitdown output.pptx`
   - visual QA by rendering slides to PDF or images and reviewing them for overflow, collisions, alignment, and leftover placeholders
5. Repeat the fix-and-verify loop until the deck passes a clean review.
6. Return the final deck path and the QA results.

## Resource map
- `editing.md` — template-based unpack/edit/clean/pack workflow
- `pptxgenjs.md` — from-scratch slide creation patterns
- `scripts\thumbnail.py` — template layout overview
- `scripts\add_slide.py` — duplicate slides or add from a layout
- `scripts\clean.py` — remove orphaned slides, rels, and media after structural edits
- `scripts\office\unpack.py`, `pack.py`, `soffice.py` — deterministic extraction, packing, and rendering

## Output contract
Always report:
- the final `.pptx` path
- the template or source deck used, if any
- whether the work was template-based or from scratch
- the QA commands you ran
- any remaining visual caveats or areas that need manual review

## Validation checklist
- [ ] `python -m markitdown output.pptx` returns the expected slide text and order
- [ ] Placeholder text such as `xxxx`, `lorem ipsum`, or template boilerplate was searched for and removed
- [ ] Slide order and duplicated or deleted slides were cleaned correctly
- [ ] Rendered slide images were checked for overflow, overlap, clipping, weak contrast, and spacing issues
- [ ] A fix-and-verify cycle was completed after the first render
