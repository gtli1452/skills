---
name: pdf
description: Use when a local PDF is the main input or output: extracting text or tables, filling forms, annotating non-fillable forms, splitting or merging pages, OCR, or creating and validating PDFs from local data.
---

# PDF workflows

Assume local files under the user's control. Prefer deterministic scripts, JSON intermediates, and image-based validation when layout matters.

## Use when
- A `.pdf` file is the primary source or deliverable.
- The task involves text extraction, table extraction, page manipulation, OCR, form filling, or creating a PDF from structured content.
- You need a validation-friendly workflow for fillable or non-fillable forms.

## Do not use when
- The primary artifact is a Word document, spreadsheet, or slide deck.
- The task is only to summarize content and no PDF file needs to be created, modified, or inspected directly.
- The workflow depends on online signing or hosted document services.

## Capability checks and fallbacks
1. Confirm the input file, requested outputs, and whether you are extracting data, filling a form, changing pages, or creating a new PDF.
2. Check available tools:
   - `python`
   - `python scripts\check_fillable_fields.py --help`
   - `python scripts\convert_pdf_to_images.py --help`
   - optional CLI tools such as `pdftotext` or `qpdf`
3. Fallbacks:
   - If text extraction is weak because the PDF is scanned, render images and use OCR
   - If a form is not fillable, switch to the annotation workflow in `forms.md`
   - If visual placement matters, convert pages to images before finalizing

## Default workflow
1. Identify whether the task is extraction, form filling, page manipulation, or PDF creation.
2. For text and tables, use `pypdf`, `pdfplumber`, `pdftotext`, or the techniques in `reference.md`.
3. For forms, start with `python scripts\check_fillable_fields.py input.pdf` and follow `forms.md` exactly.
4. For non-fillable forms, keep coordinates in JSON, validate them with `python scripts\check_bounding_boxes.py fields.json`, then fill.
5. For layout-sensitive work, render pages with `python scripts\convert_pdf_to_images.py input.pdf images` and review them.
6. Return the final PDF path or extracted artifacts and the validation notes.

## Resource map
- `forms.md` — step-by-step workflows for fillable and non-fillable PDFs
- `reference.md` — advanced libraries and examples for creation, rendering, extraction, and manipulation
- `scripts\check_fillable_fields.py`, `extract_form_field_info.py`, `fill_fillable_fields.py` — fillable-form detection and completion
- `scripts\extract_form_structure.py`, `fill_pdf_form_with_annotations.py` — non-fillable form structure extraction and annotation-based filling
- `scripts\check_bounding_boxes.py`, `create_validation_image.py`, `convert_pdf_to_images.py` — coordinate validation and visual QA helpers

## Output contract
Always report:
- the final PDF path or extracted artifact path
- the source PDF used
- the workflow chosen (extraction, fillable form, non-fillable form, page editing, or creation)
- the validation commands you ran and their results
- any extraction ambiguity, OCR limitations, or placement caveats

## Validation checklist
- [ ] Text or table extraction was sampled for correctness when extraction was requested
- [ ] Fillable forms were validated against extracted field metadata before writing values
- [ ] Non-fillable forms used checked bounding boxes before filling
- [ ] Rendered page images were reviewed when placement or appearance mattered
- [ ] OCR or extraction limitations were reported instead of guessed around
