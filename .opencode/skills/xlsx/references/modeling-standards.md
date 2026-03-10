# Workbook and modeling standards

Use these defaults unless the user's existing template or instructions clearly override them.

## All workbook outputs
- Use a consistent, professional font for new workbook content
- Deliver formula-bearing files with zero Excel errors whenever possible
- Preserve established template styling and conventions when modifying an existing workbook
- Document meaningful hardcodes or assumptions near the cells that depend on them

## Financial model color conventions
Unless the workbook already uses a different house style:
- **Blue text**: hardcoded inputs and scenario cells
- **Black text**: formulas and calculations
- **Green text**: links to other worksheets in the same workbook
- **Red text**: external links to other files
- **Yellow fill**: assumptions or cells needing attention

## Number formatting defaults
- Years as text strings such as `2024`
- Currency with explicit units in headers, for example `Revenue ($mm)`
- Zeros displayed as `-` when that fits the workbook's convention
- Percentages as `0.0%` unless the workbook already uses something else
- Negative numbers in parentheses instead of a leading minus when the workbook uses financial formatting

## Formula construction rules
- Put assumptions in dedicated cells and reference them from formulas
- Avoid hardcoded multipliers inside formulas when a named or visible assumption cell would be clearer
- Verify references before copying formulas across long ranges
- Test edge cases such as zero denominators and empty source cells

## Hardcode documentation pattern
When a workbook relies on a manually entered figure, note the source in an adjacent cell, comment, or notes area.

Suggested format:
`Source: [System or document], [Date], [Specific reference], [URL if applicable]`

Examples:
- `Source: Company 10-K, FY2024, Page 45, Revenue Note`
- `Source: Internal forecast, 2026-03-01, Budget tab assumptions`

## Final QA
- Check that key headers, units, and totals make sense
- Confirm formulas were recalculated successfully
- Confirm the workbook still resembles the original template when template preservation mattered
