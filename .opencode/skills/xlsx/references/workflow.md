# Spreadsheet workflow reference

Read this file when a workbook or delimited table is the main artifact.

## Choose the right tool

| Need | Recommended tool |
|------|------------------|
| Inspect, filter, clean, or reshape tabular data | `pandas` |
| Preserve workbook structure, formulas, or formatting | `openpyxl` |
| Recalculate formulas and detect Excel errors | `scripts\recalc.py` |

Use `pandas` for data operations and `openpyxl` for workbook-aware edits. It is normal to use both in the same workflow.

## Reading data with pandas
```python
import pandas as pd

df = pd.read_excel("input.xlsx")
all_sheets = pd.read_excel("input.xlsx", sheet_name=None)

df = pd.read_csv("input.csv")
```

Useful analysis steps:
- `df.head()` for a quick preview
- `df.info()` for column types and null counts
- `df.describe()` for numeric summaries

## Writing data with pandas
```python
import pandas as pd

df.to_excel("output.xlsx", index=False)
df.to_csv("output.csv", index=False)
```
Use this path when you do not need workbook formulas or rich formatting.

## Editing workbooks with openpyxl
```python
from openpyxl import Workbook, load_workbook

wb = load_workbook("existing.xlsx")
ws = wb[wb.sheetnames[0]]

ws["A1"] = "Updated value"
ws["B2"] = "=SUM(B3:B10)"

wb.save("output.xlsx")
```

Use `openpyxl` when you need to preserve formulas, sheet layout, styles, or named worksheets.

## Formula rule: write formulas into Excel
Prefer formulas in the workbook over Python-calculated hardcodes.

**Wrong:**
```python
total = df["Sales"].sum()
ws["B10"] = total
```

**Right:**
```python
ws["B10"] = "=SUM(B2:B9)"
```

The workbook should still recalculate correctly if the source values change later.

## Recalculation and error detection
After creating or editing a formula-bearing workbook:
```bash
python scripts\recalc.py output.xlsx
```

Example JSON response:
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42
}
```

If errors exist, the script reports them by type and cell location.

```json
{
  "status": "errors_found",
  "total_errors": 2,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

Fix the formulas and rerun until the workbook is clean or the remaining limitation is clearly reported.

## Common pitfalls
- Excel rows and columns are 1-based; DataFrame positions are not
- `load_workbook(..., data_only=True)` is for reading calculated values, not for saving formula workbooks
- Nulls and blank strings can break formula assumptions if you do not handle them explicitly
- Large workbooks often hide important references far to the right; verify the actual cell addresses
- Cross-sheet formulas must use the correct `SheetName!A1` syntax

## Quick validation strategy
- Test 2 or 3 representative formulas before filling an entire sheet
- Check zero, negative, and empty-value cases
- Recalculate before you declare the workbook done
