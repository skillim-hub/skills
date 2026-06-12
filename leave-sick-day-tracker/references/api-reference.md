# Israeli Leave Tracker Reference

This reference describes the legal/regulatory sources, local data contracts, and command-line/client behavior for the Annual Leave and Sick-Day Tracker.

No canonical public government API exists for calculating an individual employee's Israeli annual leave, sick-day, reserve-duty, birth and parenthood leave, or mourning-day balance. Use this package as a local calculation and audit helper. Keep every statutory value configurable and verify the current employee-specific legal context before payroll close.

## Web-validated source register

Access date for the v3 validation pass: 04/06/2026.

| Area | Verified baseline | Primary source | Secondary source | Tracker setting |
|---|---|---|---|---|
| VAT reference | 18% from 01/01/2025; not used in leave balances | Israel Tax Authority VAT history and interpretation note | Current 2026 accounting exam materials/search results showing 18% | Reference only |
| Annual leave, 5-day week | Statutory floor: 12 net workdays for years 1-5; 20 net cap from year 12+ if no more generous order applies | Kol Zchut 5-day calculation page, linked to Ministry of Labor | Payroll/legal table source | `ANNUAL_ENTITLEMENT_NET_WORKDAYS[5]` and `annual_override_days` |
| Annual leave, 6-day week | 14 net workdays for years 1-5; year 12 is 23; year 13+ is 24 | Kol Zchut 6-day calculation page | Payroll/legal table source | `ANNUAL_ENTITLEMENT_NET_WORKDAYS[6]` |
| Annual leave excluded days | Reserve duty, birth and parenthood leave, sickness/incapacity, mourning days, and holidays are not counted as annual leave days | Annual Leave Law references and Kol Zchut overview | Ministry of Labor newsletter/search result | Separate ledgers for `miluim`, `parental`, `sick`, `mourning` |
| Sick-day accrual | 1.5 days per full month, cumulative cap 90 days | Ministry of Labor paid sick leave page | Kol Zchut sick pay/calculation pages | `sick_monthly_accrual=1.5`, `sick_cap_days=90` |
| Sick-pay equivalent | Day 1: 0%; days 2-3: 50%; day 4+: 100%, unless more generous agreement applies | Kol Zchut calculation page | Ministry of Labor paid sick leave page/search result | `sick_pay_equivalent_days()` |
| Reserve duty | Employer pays usual wage/benefit and seeks National Insurance reimbursement | National Insurance Hebrew/English employer pages | National Insurance form page 501 | `absence_type=miluim`; no annual/sick deduction |
| Reserve-duty form | Employer reimbursement form is 501; current online paths are forms/pages, not this package's API | National Insurance form 501 page | English employer reimbursement page | Store form/certificate in `reference` |
| Birth and parenthood leave | Official terminology: `תקופת לידה והורות`; English source uses `birth and parenthood leave` | National Insurance maternity allowance page | Ministry/BTL Hebrew pages | `absence_type=parental`; no default annual/sick deduction |
| Mourning days | Up to 7 calendar days depending on religion/custom/sector; not deducted from annual leave | Ministry of Labor mourning page | Kol Zchut mourning page | `absence_type=mourning`, `mourning_paid_days_limit=7` |
| 2026 reserve-duty extension orders | 2026 orders may add rights for reservists/spouses and annual leave accumulation; check before payroll close | Official gazette/search result | Labor-law update/search result | Manual review note; use overrides/events |
| External API/webhooks | No public leave-balance API endpoint or webhook event model is referenced by this package | Official sources are pages/forms | Package CLI/client are local only | No endpoint host, path, or webhook names |

## Official/public reference URLs

Use these links as starting points and confirm that they apply to the employee, employer, sector, date, and agreement.

- Israel Tax Authority VAT history: `https://www.gov.il/he/pages/vat-history`
- Israel Tax Authority VAT interpretation note: `https://www.gov.il/BlobFolder/dynamiccollectorresultitem/represent-info-051224-2/he/vat_represent-info-051224-2.pdf`
- Ministry of Labor annual leave page: `https://www.gov.il/he/pages/annual-vacations`
- Kol Zchut 5-day annual leave calculation: `https://www.kolzchut.org.il/he/חישוב_מספר_ימי_החופשה_השנתית_לעובדים_במקומות_עבודה_שבהם_מונהג_שבוע_עבודה_בן_5_ימים`
- Kol Zchut 6-day annual leave calculation: `https://www.kolzchut.org.il/he/חישוב_מספר_ימי_החופשה_השנתית_לעובדים_במקומות_עבודה_שבהם_מונהג_שבוע_עבודה_בן_6_ימים`
- Ministry of Labor paid sick leave: `https://www.gov.il/he/pages/paid-sick-leave`
- National Insurance reserve service benefits: `https://www.btl.gov.il/benefits/Reserve_Service/Pages/default.aspx`
- National Insurance employer reserve reimbursement form 501: `https://www.btl.gov.il/טפסים%20ואישורים/forms/Reserve_Service_forms/Pages/501%20-%20תביעת%20מעסיק%20להחזרת%20תגמולי%20מילואים.aspx`
- National Insurance maternity allowance: `https://www.btl.gov.il/benefits/maternity/Childbirth_Allowance/Pages/default.aspx`
- National Insurance English maternity allowance: `https://www.btl.gov.il/English%20Homepage/Benefits/Maternity%20Insurance/Maternity%20Allowance/Pages/default.aspx`
- Ministry of Labor mourning days: `https://www.gov.il/he/pages/absence-due-to-mourning`
- Kol Zchut mourning days: `https://www.kolzchut.org.il/he/ימי_אבל`

## Data contract: Employee CSV

### Required columns

| Column | Type | Example | Validation |
|---|---|---|---|
| `employee_id` | string | `E001` | Required, unique |
| `name` | string | `Dana Levi` | Required for readable reports |
| `hire_date` | date | `01/01/2024` | `DD/MM/YYYY`, `DD-MM-YYYY`, or ISO |
| `work_week_days` | integer | `5` | Must be `5` or `6` |

### Optional columns

| Column | Type | Default | Purpose |
|---|---:|---:|---|
| `opening_annual_balance` | decimal | `0` | Imported vacation balance before tracker start |
| `opening_sick_balance` | decimal | `0` | Imported sick balance before tracker start |
| `annual_override_days` | decimal/blank | blank | More generous annual entitlement, including extension orders |
| `sick_monthly_accrual` | decimal | `1.5` | Sick accrual rate |
| `sick_cap_days` | decimal | `90` | Sick balance cap |
| `mourning_paid_days_limit` | decimal | `7` | Default paid mourning allowance |
| `notes` | string | blank | Audit explanation |

### Example request file

```csv
employee_id,name,hire_date,work_week_days,opening_annual_balance,opening_sick_balance,annual_override_days,sick_monthly_accrual,sick_cap_days,mourning_paid_days_limit,notes
E001,Dana Levi,01/01/2024,5,0,0,,1.5,90,7,Full-time
E002,Noam Cohen,15/03/2022,6,3,12,18,1.5,90,7,Contractual vacation uplift
```

## Data contract: Events CSV

| Column | Type | Example | Validation |
|---|---|---|---|
| `employee_id` | string | `E001` | Must exist in employees CSV |
| `absence_type` | enum | `annual` | `annual`, `sick`, `miluim`, `parental`, `mourning` |
| `start_date` | date | `18/08/2024` | Required |
| `end_date` | date | `22/08/2024` | Must be on/after start |
| `days` | decimal/blank | blank | Blank means auto-count workdays |
| `approved` | boolean | `true` | False events do not deduct balances |
| `reference` | string | `VAC-2024-001` | Approval/document/form/certificate ID |
| `notes` | string | `Manager approved` | Audit details |

### Example request file

```csv
employee_id,absence_type,start_date,end_date,days,approved,reference,notes
E001,annual,18/08/2024,22/08/2024,,true,VAC-2024-001,Summer vacation
E001,sick,01/09/2024,03/09/2024,,true,MED-4432,Medical certificate
E002,miluim,10/10/2024,17/10/2024,,true,RES-2024-044,Reserve certificate
```

## Command-line tool reference

### Create templates

```bash
leave-sick-day-tracker template ./data
```

Response:

```json
{
  "employees_csv": "data/employees.csv",
  "events_csv": "data/events.csv"
}
```

### Calculate entitlement

```bash
leave-sick-day-tracker entitlement --hire-date 01/01/2013 --as-of 31/12/2024 --work-week-days 6
```

Response:

```json
{
  "entitlement_days": 23.0,
  "accrued_days": 209.0
}
```

The example response illustrates the annual entitlement for the calculation date. Actual accrued totals depend on the full employment period and any overrides.

### Calculate sick pay equivalent

```bash
leave-sick-day-tracker sick-pay --days 5
```

Response:

```json
{
  "sick_days": 5.0,
  "paid_equivalent_days": 3.0
}
```

### Produce summary

```bash
leave-sick-day-tracker summary ./data/employees.csv ./data/events.csv --as-of 31/12/2024 --output ./data/summary.csv
```

Response fields:

| Field | Meaning |
|---|---|
| `annual_accrued` | Opening balance plus calculated annual accrual |
| `annual_used` | Approved annual-leave event days |
| `annual_balance` | Accrued annual leave minus used annual leave |
| `sick_accrued` | Opening balance plus accrued sick days, capped |
| `sick_used` | Approved sick event days |
| `sick_balance` | Accrued sick days minus used sick days |
| `sick_paid_equivalent_days` | Statutory paid-day equivalent for sick events |
| `miluim_days` | Tracked reserve duty days |
| `parental_days` | Tracked birth and parenthood leave days |
| `mourning_days` | Tracked mourning days |
| `warnings` | Payroll/legal review flags |

## Client API reference

### Sync usage

```python
from leave_sick_day_tracker import EmployeeProfile, LeaveEvent, LeaveTrackerClient

employee = EmployeeProfile("E001", "Dana Levi", "01/01/2024", work_week_days=5)
tracker = LeaveTrackerClient([employee])
tracker.record_event(LeaveEvent("E001", "annual", "18/08/2024", "22/08/2024"))
snapshot = tracker.balance("E001", "31/12/2024")
print(snapshot.to_dict())
```

### Async usage

```python
snapshot = await tracker.abalance("E001", "31/12/2024")
```

The async methods wrap CPU/local-file operations with `asyncio.to_thread()` so an automation can call the tracker without blocking an event loop.

## Error table

| Error | Trigger | Fix |
|---|---|---|
| `Invalid date` | Unsupported date such as `31.01.2024` | Use `31/01/2024`, `31-01-2024`, or `2024-01-31` |
| `work_week_days must be 5 or 6` | Unsupported workweek | Enter `5` or `6`, or pass manual event days |
| `Unknown employee_id` | Event references missing employee | Add employee row or correct ID |
| `event end_date must be on or after start_date` | Reversed date range | Correct event dates |
| `event days must be non-negative` | Negative event days | Use positive event days; record adjustments as separate events |
| `Annual leave balance is negative` | Annual leave used exceeds accrued balance | Confirm advance leave approval or payroll deduction rules |
| `Sick balance is negative` | Sick days used exceed accrued balance | Confirm unpaid sick leave or special arrangement |
| `Long sick event detected` | Sick event above 30 days | Verify certificates and National Insurance/disability implications |
| `Mourning absence exceeds default paid-day limit` | Mourning days exceed configured policy limit | Check agreement, policy, and lawful treatment |

## Versioning and audit

- Store source CSV files with payroll month in the filename, for example `events-2026-12.csv`.
- Export `summary-YYYY-MM.csv` after payroll close.
- Do not edit closed files. Add an adjustment event in the next open month.
- Record statutory table updates in `CHANGELOG.md` and cite them in `references/verification-log.md`.
- Re-run `pytest` and `python -m compileall scripts/ -q` after any statutory-table change.
