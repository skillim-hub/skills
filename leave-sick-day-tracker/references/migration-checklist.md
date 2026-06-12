# Migration Checklist

Use this checklist when moving from a spreadsheet, payroll bureau export, HR system, or manual notes into the tracker.

## 1. Freeze the source

- [ ] Save a read-only copy of the old spreadsheet or export.
- [ ] Record export date and payroll period.
- [ ] Keep the original file unchanged.
- [ ] Identify the person who approved the migration.

## 2. Map employee fields

| Source field | Target field | Notes |
|---|---|---|
| Employee number | `employee_id` | Must be stable and unique |
| Full name | `name` | Use payroll spelling |
| Start date | `hire_date` | Use recognized employment start |
| Work pattern | `work_week_days` | `5` or `6`; part-time may require manual event days |
| Vacation opening | `opening_annual_balance` | Balance at cutover date |
| Sick opening | `opening_sick_balance` | Balance at cutover date |
| Contractual vacation | `annual_override_days` | Use only if more generous entitlement applies |
| Notes | `notes` | Include source file and assumptions |

## 3. Map absence fields

| Source field | Target field | Notes |
|---|---|---|
| Employee number | `employee_id` | Must match employees CSV |
| Absence category | `absence_type` | Map carefully |
| Start | `start_date` | Convert to `DD/MM/YYYY` |
| End | `end_date` | Convert to `DD/MM/YYYY` |
| Units | `days` | Leave blank only when auto-counting is correct |
| Approval status | `approved` | Use `true` only for approved events |
| Document number | `reference` | Approval/certificate/payroll case |
| Comments | `notes` | Preserve audit context |

## 4. Category mapping

| Old category | New type | Warning |
|---|---|---|
| Vacation / חופשה | `annual` | Check holidays and half-days |
| Sick / מחלה | `sick` | Check certificate and continuous-event split |
| Reserve / מילואים | `miluim` | Must not deduct annual/sick |
| Maternity / parental / לידה | `parental` | Protected-period review required |
| Bereavement / אבל | `mourning` | Check paid-day limit and agreement |
| Unpaid leave / חל"ת | Not covered by default | Track separately or extend the enum |
| Holiday / חג | Not an absence event | Handle through holiday calendar/payroll |

## 5. Clean data before import

- [ ] Remove duplicate rows.
- [ ] Convert dates.
- [ ] Replace comma decimals with dot decimals.
- [ ] Normalize employee IDs.
- [ ] Split combined absence rows.
- [ ] Mark pending requests as `approved=false`.
- [ ] Remove unnecessary medical details from notes.
- [ ] Add references for certificates and approvals.

## 6. Validate import

```bash
python scripts/leave_sick_day_tracker_cli.py validate-data ./data/employees.csv ./data/events.csv --as-of 31/12/2024
```

Resolve:

- Unknown employee IDs.
- Invalid date ranges.
- Wrong workweek values.
- Negative balances without explanation.
- Mourning over-limit warnings.
- Long sick warnings.

## 7. Reconcile

Select at least five employees:

- One new employee.
- One senior employee.
- One part-time employee.
- One employee with sick leave.
- One employee with miluim or birth and parenthood leave.

For each employee:

1. Compare annual accrued.
2. Compare annual used.
3. Compare annual balance.
4. Compare sick accrued.
5. Compare sick used.
6. Compare sick balance.
7. Explain every gap.

## 8. Cut over

- [ ] Approve opening balances.
- [ ] Archive old source.
- [ ] Store mapping file.
- [ ] Use the tracker for new events only after cutover.
- [ ] Keep payroll bureau informed of the calculation basis.
- [ ] Schedule a review after the first payroll close.

## 9. Rollback

Prepare rollback before production:

- [ ] Keep old spreadsheet available.
- [ ] Store all generated CSVs.
- [ ] Record commands used.
- [ ] Keep summary output.
- [ ] Define who can approve rollback.

## Migration notes for version 1.2.0

- Replace any local six-day annual-leave table that grants `24` net days in the 12th seniority year with `23` net days.
- Keep `24` net days for six-day employees from the 13th seniority year onward.
- Re-run historical balances for employees whose 12th seniority year was calculated by an older package copy.
- Review five-day employees for short-workweek extension-order or agreement-based entitlements that exceed the statutory floor.
- Review 2026 reserve-duty cases manually before final payroll close.
- Treat VAT as reference-only for this package; do not add VAT fields to leave-balance imports.
