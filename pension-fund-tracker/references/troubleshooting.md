# Troubleshooting

## Fast diagnosis

| Problem | Likely cause | Fix |
|---|---|---|
| Hebrew appears garbled | Encoding mismatch | Try UTF-8-SIG, UTF-8, then Windows-1255 |
| CSV loads as one column | Wrong delimiter | Re-export as comma CSV or preprocess delimiter |
| Percentages are 100x too high | Fraction/percentage confusion | Confirm source convention |
| Dates fail | Unexpected format | Inspect source column and add alias or converter |
| Fund not found | ID parsed as number or lost leading zero | Keep IDs as text |
| Ranking differs from spreadsheet | Latest-only logic differs from spreadsheet | Align method and period |
| Missing 36M return | New fund or omitted field | Use available periods and caveat |
| CKAN 404 | Resource ID changed | Run package search |
| CKAN `success: false` | API rejected request | Inspect `error` and simplify query |
| CLI import error | Missing dependencies | Install `requirements-dev.txt` |

## Encoding

Try:
1. UTF-8-SIG
2. UTF-8
3. Windows-1255 (`cp1255`)

```python
from pathlib import Path
for enc in ["utf-8-sig", "utf-8", "cp1255"]:
    try:
        print(enc, Path("pensia-net.csv").read_text(encoding=enc)[:100])
        break
    except UnicodeDecodeError:
        pass
```

## Number parsing

| Source value | Normalized value |
|---|---:|
| `0.2` | `0.2` |
| `0.20%` | `0.2` |
| `1,23` | `1.23` |
| `1,234.56` | `1234.56` |
| `₪2,000` | `2000` |

Do not convert `0.2` to `20%` unless the official schema explicitly says values are fractions.

## Date parsing

Supported:
- `31/12/2025`
- `31/12/2025`
- `2025-12-31`
- `12-2025`
- `12/2025`
- `202512`

Month-only values become the first day of that month in machine output.

## Validation levels

Critical:
- Missing fund ID.
- Missing fund name.
- Missing report date.

Warning:
- Duplicate fund/name/date row.
- Implausible return.
- Implausible fee.
- Negative assets.
- Missing long-term return.

## API recovery

For stale discovered resource ID:
1. Search packages.
2. Inspect resources.
3. Choose the current official Pensia Net resource from Data.gov.il.
4. Update configuration.
5. Save new source metadata.

For timeouts:
1. Reduce page size.
2. Add retry/backoff outside the bundled client.
3. Cache raw pages.
4. Resume from last offset.

## Reproducibility

Save:
- Raw source file.
- Normalized JSON.
- Validation output.
- Command line.
- Package version.
- Assumptions.
- Final report.
