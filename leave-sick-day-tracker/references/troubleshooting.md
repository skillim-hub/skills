# Troubleshooting

Use this guide to diagnose incorrect balances, rejected files, payroll mismatches, and localization issues.

## Balance issues

### Annual balance is unexpectedly high

Likely causes:

- Approved vacation events were not imported.
- `approved=false` remains on real events.
- Employee ID mismatch creates orphan events.
- As-of date is before the absence date.
- Opening balance was imported twice.

Fix:

1. Search `events.csv` for the employee ID.
2. Confirm `absence_type=annual`.
3. Confirm `approved=true`.
4. Run summary with the correct month-end date.
5. Compare `opening_annual_balance` with the prior system.

### Annual balance is unexpectedly low

Likely causes:

- Weekends or holidays counted as vacation.
- Workweek set to `6` instead of `5`.
- Half-day entered as `1`.
- Duplicate event imported.
- Manual `days` value overrides auto-counting.

Fix:

1. Check `work_week_days`.
2. Check duplicate rows.
3. Inspect `days`; blank it to use auto-counting or enter the correct value.
4. Adjust holiday days manually until a holiday calendar is added.
5. Keep an audit note for every manual override.

### Sick balance is negative

Likely causes:

- Employee has not accrued enough sick days.
- Opening sick balance missing.
- One long illness exceeds accrued balance.
- Sick accrual cap or rate was configured incorrectly.

Fix:

1. Confirm `hire_date`.
2. Confirm `opening_sick_balance`.
3. Confirm `sick_monthly_accrual=1.5` unless a different rule applies.
4. Confirm `sick_cap_days=90` unless a different rule applies.
5. Mark unpaid excess or special arrangement in payroll notes.

### Sick paid-day equivalent is wrong

Likely causes:

- Separate illnesses were merged.
- A continuous illness was split.
- Non-workdays were included.
- Contract/collective agreement has more generous pay.

Fix:

1. Match event dates to medical certificates.
2. Split unrelated events.
3. Merge continuous events only when supported.
4. Override payroll treatment if a more generous arrangement applies.
5. Document the basis.

## Data import issues

### Unknown employee ID

Cause: `events.csv` contains an `employee_id` not present in `employees.csv`.

Fix:

```bash
python scripts/leave_sick_day_tracker_cli.py validate-data ./data/employees.csv ./data/events.csv
```

Then correct the ID or add the employee.

### Invalid date

Accepted formats:

- `31/12/2024`
- `31/12/2024`
- `2024-12-31`

Rejected examples:

- `31.12.2024`
- `12-31-2024`
- `2024/31/12`

### Hebrew appears corrupted in Excel

Cause: CSV encoding without BOM.

Fix:

- Use files produced by the command-line tool export.
- Save manual CSV as UTF-8 with BOM.
- In Excel, import through Data → From Text/CSV and select UTF-8.

### Decimal values fail in imported files

Cause: comma decimal separators such as `0,5` inside CSV.

Fix:

- Use `0.5`.
- Avoid thousands separators.
- Wrap notes containing commas in quotes.

## Legal/payroll review warnings

### Negative annual leave

Actions:

1. Check whether advance vacation was approved.
2. Confirm deduction from final pay is lawful and documented before termination.
3. Consider shortening future approved vacation.
4. Do not delete the negative balance.

### Mourning days exceed default limit

Actions:

1. Check relationship and applicable source.
2. Check collective agreement or sector practice.
3. Split paid/unpaid treatment only after review.
4. Avoid storing unnecessary personal details.

### Miluim deducted from vacation

Actions:

1. Change `absence_type` to `miluim`.
2. Recalculate summary.
3. Confirm payroll/National Insurance workflow.
4. Correct the payslip if already closed.

### Parental leave deducted from sick days

Actions:

1. Change `absence_type` to `parental`.
2. Recalculate summary.
3. Review protected-period handling.
4. Correct payroll records.

## command-line tool problems

### Command not found

Use Python explicitly:

```bash
python scripts/leave_sick_day_tracker_cli.py --help
```

### Click import error

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

### Pytest cannot import hyphenated scripts

Use the provided pytest configuration in `pyproject.toml`, which sets importlib mode.

```bash
python -m pytest
```

## Audit problems

### Closed month changed

Fix:

1. Restore the closed file from archive.
2. Move the change to a correction event in the current open month.
3. Use a reference such as `ADJ-YYYY-NNN`.
4. Add a note explaining the original error and correction.

### Missing approvals

Fix:

1. Keep event with `approved=false` until approval arrives.
2. Do not deduct unapproved events from balances.
3. If payroll already deducted the absence, create a warning and reconcile.

### Missing medical certificate

Fix:

1. Record the reported sick event.
2. Mark documentation status in `notes`.
3. Follow employer policy for certificate collection.
4. Reconcile payment only after lawful review.

## Web-validated 2026 correction issues

### Six-day employee in the 12th seniority year shows 24 annual days

Cause: older copies used the 13th-year cap one year too early.

Fix: update to version 1.2.0 or later, rerun the balance, and verify that the 12th seniority year returns `23` net days for a six-day workweek.

### VAT appears in a legal reference but not in the balance output

Cause: VAT is relevant to invoices and tax accounting, not to employee leave-balance arithmetic.

Fix: keep VAT out of annual leave, sick-day, miluim, birth and parenthood leave, and mourning calculations.

### A 2026 miluim case may affect annual leave accumulation

Cause: 2026 extension orders can create fact-specific rights for reserve servants and spouses.

Fix: add a manual review note, check the current order, and apply any more generous arrangement before payroll close.
