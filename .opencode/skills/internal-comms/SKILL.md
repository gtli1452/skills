---
name: internal-comms
description: Write internal communications in the formats an organization already uses. Use this skill for status reports, leadership updates, 3P updates, newsletters, FAQs, incident reports, project updates, and similar internal comms. Adapt to any examples, templates, or AGENTS.md guidance the user provides.
license: Complete terms in LICENSE.txt
---

## When to use this skill

Use this skill whenever the user wants help drafting or revising an internal communication, including:
- 3P updates (Progress, Plans, Problems)
- Company or org newsletters
- FAQ responses
- Status reports
- Leadership updates
- Project updates
- Incident reports

## How to use this skill

1. **Identify the communication type and audience** from the request
2. **Load the closest guideline file** from the `examples/` directory:
   - `examples/3p-updates.md` - Progress/Plans/Problems team updates
   - `examples/company-newsletter.md` - Org-wide newsletters
   - `examples/faq-answers.md` - FAQ and common-question responses
   - `examples/general-comms.md` - Any internal communication that does not cleanly match the others
3. **Check for local conventions** in `AGENTS.md`, nearby docs, or user-provided examples if the output needs to match a specific house style
4. **Gather missing facts** before drafting so the communication is accurate and appropriately scoped
5. **Follow the selected guideline file** for formatting, tone, and structure

If the communication type does not match an existing guideline, use `examples/general-comms.md` as the default and adapt it to the user's organization and audience.

## Keywords

3P updates, company newsletter, internal newsletter, weekly update, FAQ, common questions, status update, leadership update, project update, incident report, internal comms
