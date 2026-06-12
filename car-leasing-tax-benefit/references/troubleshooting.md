# Troubleshooting Guide

## Fast triage

| Problem | First check | Likely fix |
|---|---|---|
| Calculation fails immediately | JSON/table path | Use `--table` or restore `data/tax_authority_tables.json`. |
| Year rejected | `tax_year` exists in table | Add current year rules. |
| Category rejected | Category key spelling | Run `categories`. |
| Result differs from payroll | Rate/reduction/source price | Compare trace with payroll system setup. |
| Hebrew CSV is unreadable | Encoding | Open with UTF-8 or use Excel import wizard. |

## Error: `Rule table not found`

Cause: the client cannot locate `data/tax_authority_tables.json`.

Fix:

```bash
python scripts/car_leasing_tax_benefit_client.py calculate \
  --table /full/path/to/tax_authority_tables.json \
  --price 180000
```

Also check that the command is run from the project folder or that the script has not been moved without the data folder.

## Error: `Rule table is not valid JSON`

Cause: a manual edit introduced a missing comma, unescaped quote, or invalid character.

Fix:

```bash
python -m json.tool data/tax_authority_tables.json
```

Correct the highlighted line, then run tests.

## Error: `No rules for tax_year=YYYY`

Cause: the requested year is absent from `annual_rules`.

Fix:

1. Copy the prior year block.
2. Rename the key to the new year.
3. Update effective dates in `DD/MM/YYYY`.
4. Update the linear rate and category reductions from official sources.
5. Run `pytest scripts`.

## Error: `Unknown category`

Cause: unsupported key or typo.

Supported keys for the included private-car formula:

```text
private_combustion
hybrid
plugin_hybrid
electric
```

Command:

```bash
python scripts/car_leasing_tax_benefit_client.py categories
```

## Error: `requires a dedicated rule`

Cause: the selected category is intentionally blocked from the private-car linear formula. Example: `motorcycle_l3`.

Fix: use a separate rule source for that category. Do not force the private-car formula.

## Result is unexpectedly high

Possible causes:

- Used list price including additions instead of official coordinated original price.
- Used `employee_marginal_tax_rate` only to estimate tax cost, not to reduce Shovi Rechev.
- Entered agorot as shekels, for example `18000000` instead of `180000`.
- Missed green-vehicle category.

Checks:

```bash
python scripts/car_leasing_tax_benefit_client.py calculate --price 180000 --category private_combustion --json
```

Read `trace.gross_monthly_value_ils`.

## Result is unexpectedly low

Possible causes:

- Used stale or excessive green-vehicle reduction.
- Entered `private_use_ratio` below 1.
- Used `months_available` below 12.
- Used price after discount rather than official price.
- Electric/hybrid table copied from the wrong year.

Checks:

- Inspect `trace.category_reduction_ils`.
- Inspect `trace.private_use_ratio`.
- Inspect `trace.months_available`.
- Confirm `rule_effective_from` and `rule_effective_to`.

## Payroll system produces a different value

Perform reconciliation:

| Reconciliation item | Calculator location | Payroll location |
|---|---|---|
| Tax year | `tax_year` | Payroll period setup |
| Price | `original_price_ils` | Vehicle master data |
| Category | `category` | Vehicle tax-benefit code |
| Monthly reduction | `trace.category_reduction_ils` | Tax table |
| Formula rate | `trace.base_linear_rate` | Tax table |
| Period | `trace.months_available` | Assignment dates |

Document any payroll rounding or day-proration differences.

## CSV opens with broken Hebrew

The client writes UTF-8 with BOM (`utf-8-sig`) for CSV export. If text still appears garbled:

1. Open Excel.
2. Choose Data → From Text/CSV.
3. Select UTF-8.
4. Confirm delimiter is comma.
5. Import.

## Typer CLI does not run

The CLI wrapper uses Typer when installed and falls back to the argparse client otherwise.

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Fallback command:

```bash
python scripts/car_leasing_tax_benefit_client.py calculate --price 180000
```

## Test suite fails after table update

Common reasons:

- Expected amounts in tests still reflect previous category reductions.
- JSON table uses strings where numbers were expected, or vice versa.
- A required category was removed.
- Effective dates were changed to a non-`DD/MM/YYYY` format.

Fix sequence:

```bash
python -m json.tool data/tax_authority_tables.json
pytest scripts -q
```

Update tests only after verifying the official table and recalculating expected values.

## Accountant requests legal support

Provide:

- Official Israel Tax Authority page/table used.
- Rule-table JSON snapshot.
- Vehicle price source.
- Trace output.
- Availability period.
- Explanation that estimated tax cost is a planning figure, not final payroll withholding.
