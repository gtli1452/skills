---
name: xlsx
description: Use when a local workbook or tabular file (.xlsx, .xlsm, .csv, or .tsv) is the main input or output, especially for analysis, cleanup, formula-driven edits, template-preserving updates, or creating a spreadsheet deliverable.
---

# XLSX workflows

Assume local files under the user's control. Favor deterministic workbook edits over manual spreadsheet GUIs.

## Use when
- A workbook or delimited table is the primary source or deliverable.
- The task requires spreadsheet analysis, cleanup, formulas, formatting, charts, or template-preserving edits.
- The user wants a file they can keep using in Excel or LibreOffice after the task is complete.

## Do not use when
- The deliverable is primarily a Word document, slide deck, PDF, or database workflow.
- The request is only for a one-off calculation and no workbook needs to be created or updated.
- The workflow depends on cloud-only spreadsheet services or APIs.

## Capability checks and fallbacks
1. Confirm the source files, target workbook path, and whether an existing template must be preserved exactly.
2. Check available tooling:
   - `python`
   - `python -c "import pandas, openpyxl; print('ok')"`
   - `python scripts\recalc.py --help`
3. Fallbacks:
   - If formulas are required, prefer `openpyxl`; if formulas are not required, `pandas` may be enough
   - If `recalc.py` cannot run, save the workbook but clearly report formulas as unverified
   - For fragile templates, make minimal structural changes and preserve workbook layout and formulas wherever possible

## Default workflow
1. Pick the tool path from `references\workflow.md`.
2. Use `pandas` for analysis or cleanup and `openpyxl` for formulas, formatting, and template-safe edits.
3. Keep assumptions in cells and write formulas in Excel, not Python-calculated hardcodes.
4. Save to the requested output path.
5. Run `python scripts\recalc.py output.xlsx` whenever formulas are present.
6. Fix errors and rerun until `status` is `success` or document the limitation explicitly.
7. Return the workbook path, touched sheets, and validation output.

## Resource map
- `references\workflow.md` — tool selection, read or write examples, formula rules, recalculation flow, and common pitfalls
- `references\modeling-standards.md` — output quality standards, formatting defaults, and financial-model conventions
- `scripts\recalc.py` — recalculate formulas with LibreOffice and report Excel errors as JSON
- `scripts\office\soffice.py` — LibreOffice wrapper used by the recalculation flow

## Output contract
Always report:
- the final workbook path
- the source file or files used
- the sheets you created or changed
- whether formulas were added or preserved
- the recalculation or validation result
- any unresolved workbook limitations

## Validation checklist
- [ ] Existing template structure and conventions were preserved when required
- [ ] Formulas were written into cells instead of hardcoded Python results
- [ ] `python scripts\recalc.py output.xlsx` was run for formula-bearing files
- [ ] The recalculation output shows zero formula errors, or every remaining error was explicitly reported
- [ ] Number formats, assumptions, and key hardcodes follow `references\modeling-standards.md`
