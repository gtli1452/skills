---
name: docx
description: Use when a local Word document (.docx or .doc) is the main input or output: extracting content, converting legacy files, creating new documents, editing existing documents, managing tracked changes or comments, or validating layout after document changes.
---

# DOCX workflows

Assume local files under the user's control. Prefer deterministic scripts and explicit validation over manual GUI-only editing.

## Use when
- A `.docx` or `.doc` file is the primary source or deliverable.
- The task needs template-preserving edits, tracked changes, comments, page numbers, tables of contents, headers or footers, images, or precise layout control.
- You need to extract or inspect document content before editing.

## Do not use when
- The final artifact is primarily a PDF and no Word edit is required; use the PDF skill instead.
- The main deliverable is a spreadsheet, slide deck, HTML page, or cloud-doc workflow.
- The task is mainly free-form writing with no file to create or update.

## Capability checks and fallbacks
1. Confirm the input file, requested output path, and whether an existing template must be preserved exactly.
2. Check available tools before choosing a path:
   - `python`
   - `pandoc --version` for text extraction
   - `python scripts\office\soffice.py --help` for LibreOffice-backed conversion and rendering
   - `node -e "require('docx'); console.log('docx ok')"` when creating a new document with the `docx` package
3. Fallbacks:
   - If the input is `.doc`, convert it first with `python scripts\office\soffice.py --headless --convert-to docx input.doc`
   - If `pandoc` is unavailable, inspect the XML with `python scripts\office\unpack.py input.docx unpacked`
   - If the `docx` package is unavailable, prefer editing a template `.docx` or a simpler conversion path instead of inventing fragile XML from scratch
   - If tracked changes must be flattened, run `python scripts\accept_changes.py input.docx output.docx`

## Default workflow
1. Inspect the file and decide which path applies:
   - read or analyze only
   - update an existing document
   - create a new document
2. For read or analysis tasks, extract text with `pandoc` or unpack the file for raw XML inspection.
3. For existing-document edits, read `references\editing-documents.md`, then unpack, edit only the necessary XML, and repack.
4. For new documents, read `references\creating-documents.md`, generate the file, then validate it.
5. When tracked changes or comments are required, set the author explicitly if the user cares; otherwise use the default `Editor`.
6. When layout matters, render the result to PDF or images and do a visual QA pass.
7. Return the final file path, what changed, and the validation results.

## Resource map
- `references\creating-documents.md` — creation patterns, page setup, lists, tables, images, TOC, headers, and footers
- `references\editing-documents.md` — unpack/edit/pack flow, tracked changes, comments, XML pitfalls, and render QA
- `scripts\office\unpack.py`, `pack.py`, `validate.py`, `soffice.py` — deterministic extraction, packing, validation, and LibreOffice-backed conversion
- `scripts\comment.py` — add comment boilerplate across DOCX XML files
- `scripts\accept_changes.py` — accept tracked changes into a clean output
- `scripts\templates\` — comment-related XML templates used by `comment.py`

## Output contract
Always report:
- the final `.docx` path
- the source file or files used
- whether you created a new document or edited an existing one
- the validation commands you ran and their results
- any remaining caveats, especially around layout, tracked changes, or unsupported Word features

## Validation checklist
- [ ] The file opens and passes `python scripts\office\validate.py output.docx`
- [ ] If the document was created from scratch, page size and orientation were set explicitly
- [ ] Lists use real numbering or bullet structures, not literal bullet characters
- [ ] Tables use explicit widths that add up correctly
- [ ] Tracked changes and comments have the intended author and valid XML placement
- [ ] Smart quotes and whitespace-sensitive text were preserved correctly
- [ ] A visual QA pass was completed when layout, images, headers or footers, or page breaks matter
