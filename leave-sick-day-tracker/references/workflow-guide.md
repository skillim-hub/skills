# Workflow Guide

Use these workflows to run the tracker from initial setup through monthly payroll close.

## Workflow 1: First-time setup for a small business

### Inputs

- Current employee list.
- Hire dates and recognized seniority.
- Workweek type for each employee.
- Opening annual leave and sick leave balances.
- Employment contracts or sector rules that grant more generous terms.
- Recent absence records.

### Steps

1. Create templates.

   ```bash
   python scripts/leave_sick_day_tracker_cli.py template ./data
   ```

2. Fill `employees.csv`.

   ```csv
   employee_id,name,hire_date,work_week_days,opening_annual_balance,opening_sick_balance,annual_override_days,sick_monthly_accrual,sick_cap_days,mourning_paid_days_limit,notes
   E001,Dana Levi,01/01/2024,5,0,0,,1.5,90,7,Full-time
   E002,Noam Cohen,15-03-2022,6,3,12,18,1.5,90,7,Contractual uplift
   ```

3. Fill `events.csv`.

   ```csv
   employee_id,absence_type,start_date,end_date,days,approved,reference,notes
   E001,annual,18/08/2024,22/08/2024,,true,VAC-2024-001,Approved
   E001,sick,01/09/2024,03/09/2024,,true,MED-4432,Certificate received
   ```

4. Validate data.

   ```bash
   python scripts/leave_sick_day_tracker_cli.py validate-data ./data/employees.csv ./data/events.csv --as-of 31/12/2024
   ```

5. Produce summary.

   ```bash
   python scripts/leave_sick_day_tracker_cli.py summary ./data/employees.csv ./data/events.csv --as-of 31/12/2024 --output ./data/summary-2024-12.csv
   ```

6. Review warnings with payroll.

7. Lock files after payroll close.

### Acceptance criteria

- Every approved absence has a reference or note.
- No event references an unknown employee.
- Negative balances have written approval or payroll treatment.
- Sick events match certificates.
- Miluim events have separate reserve-duty references.
- Parental and mourning leave are not mixed into annual or sick balances.

## Workflow 2: Monthly payroll close

1. Export or collect all approved absence requests for the month.
2. Add events to `events.csv`.
3. Confirm medical certificates and reserve-duty certificates.
4. Run validation with the month-end date.
5. Export summary.
6. Compare summary against payroll system balances.
7. Resolve differences.
8. Save final files in a locked payroll folder.
9. Send only required data to payroll; avoid sending unnecessary medical details.

## Workflow 3: Employee self-check

Use this workflow when an employee or consumer wants to check a payslip.

1. Extract hire date, workweek, opening balance, and current payslip balance.
2. Recreate known absences from payslips, emails, approvals, and certificates.
3. Run the tracker as of the payslip date.
4. Compare calculated balance with the payslip.
5. If a gap exists, ask payroll for:
   - Opening balance basis.
   - Workweek and entitlement table used.
   - Events deducted.
   - Sick certificates applied.
   - Carryover or expiry rules.

Use neutral wording when contacting payroll:

```text
Please provide the annual leave and sick leave balance calculation basis as of 31/12/2024, including opening balance, monthly accrual, absence events deducted, and any carryover or expiry rule applied.
```

## Workflow 4: Miluim handling

1. Record the absence as `miluim`.
2. Attach the reserve-duty certificate reference.
3. Do not deduct annual or sick leave.
4. Notify payroll to handle payment/reimbursement.
5. Reconcile any National Insurance payment or employer payment adjustment.
6. Keep the event in the capacity calendar.

Example:

```csv
E003,miluim,10-10-2024,17-10-2024,,true,RES-2024-044,Certificate received
```

## Workflow 5: Sick leave with insufficient balance

1. Record the sick event exactly as certified.
2. Calculate paid-day equivalent for the continuous event.
3. Check accrued sick balance.
4. If the event exceeds balance, flag unpaid excess or special arrangement.
5. Do not convert to annual leave without explicit lawful approval.
6. Document payroll decision.

Example command-line tool command:

```bash
python scripts/leave_sick_day_tracker_cli.py sick-pay --days 5
```

## Workflow 6: Parental leave

1. Record the protected period as `parental`.
2. Link the payroll case or National Insurance reference.
3. Do not deduct annual or sick leave by default.
4. Review benefit continuation, pension handling, and return-to-work protections.
5. Set a return review date before the expected end date.
6. Update event dates if the leave is shortened or extended.

## Workflow 7: Mourning days

1. Record the absence as `mourning`.
2. Capture minimal relationship/eligibility note.
3. Apply the configured paid-day limit.
4. If days exceed the limit, create a warning and review policy/agreement.
5. Do not automatically deduct excess from vacation.
6. Keep sensitive details minimal.

## Workflow 8: Year-end carryover review

1. Export balances as of `31-12-YYYY`.
2. Apply company carryover and expiry policy only after legal review.
3. Record adjustments as events or opening balance updates in the new year.
4. Notify employees of balances where required by policy.
5. Archive year-end CSVs and summaries.

## Workflow 9: Correcting a closed month

1. Never overwrite closed CSV files.
2. Add a correction event in the next open month.
3. Use a clear `reference`, such as `ADJ-2025-001`.
4. Explain the original error in `notes`.
5. Reconcile the next payslip.

## Workflow 10: Spreadsheet to command-line tool migration

1. Freeze the old spreadsheet.
2. Export employees and absences as CSV.
3. Map columns according to `references/migration-checklist.md`.
4. Load data with `validate-data`.
5. Compare five employees manually.
6. Approve cutover only after differences are explained.

## Web-validated 2026 payroll-close check

1. Open `references/verification-log.md` before closing the period.
2. For six-day employees in the 12th seniority year, verify that the annual entitlement uses `23` net days.
3. For six-day employees from the 13th seniority year onward, verify that the annual entitlement uses `24` net days.
4. For five-day employees, verify whether a short-workweek extension order, collective agreement, or personal contract grants more than the statutory floor.
5. For reserve-duty cases in 2026, record a manual review note because the extension order may affect annual leave accumulation depending on the employee and spouse facts.
6. Ignore VAT in leave-balance calculations; keep VAT only in invoices, accounting exports, or external finance systems.
