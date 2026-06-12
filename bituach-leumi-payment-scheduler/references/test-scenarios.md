# Test Scenarios

Use these scenarios for manual QA, scripted tests, and acceptance checks.

| # | Scenario | Input highlights | Expected result |
|---:|---|---|---|
| 1 | self-employed 12-month plan | `self-employed`, `2026-01`, income ₪10,000 | 12 obligations, first coverage month January |
| 2 | known official amount | amount override ₪1,240 | every row uses ₪1,240 |
| 3 | employer Form 102 schedule | `employer`, payroll ₪65,000 | employer action list appears |
| 4 | consumer installment | `consumer`, amount ₪350 | consumer balance-check action appears |
| 5 | small-business owner schedule | `small-business`, income ₪18,000 | self-employed-style actions appear |
| 6 | Friday due date | due date on Friday | adjusted date moves to Sunday |
| 7 | Saturday due date | due date on Saturday | adjusted date moves to Sunday |
| 8 | previous-business-day policy | Saturday with previous policy | adjusted date moves to Thursday |
| 9 | keep-date policy | Saturday with keep policy | adjusted date remains Saturday |
| 10 | holiday supplied | `--holiday 15/06/2026` | due date skips supplied holiday |
| 11 | reminder on weekend | reminder lands on Friday | reminder moves to previous business day |
| 12 | zero reminder list | empty reminder offsets | obligations have no reminders |
| 13 | invalid date format | `15/06/2026` | validation error |
| 14 | invalid payer type | `company-owner` | validation error |
| 15 | missing income | self-employed without income or amount | validation error |
| 16 | missing payroll | employer without payroll or amount | validation error |
| 17 | negative amount | amount `-1` | validation error |
| 18 | duplicate reminder offsets | `7,7,1` | validation error |
| 19 | long horizon | 61 months | validation error |
| 20 | JSON export | format `json` | valid JSON with obligations array |
| 21 | CSV export | format `csv` | header and one row per obligation |
| 22 | ICS export | format `ics` | valid VCALENDAR text with due events |
| 23 | CLI output file | `--output schedule.csv` | file created and command reports path |
| 24 | next due after first due date | today after first adjusted due | second obligation returned |
| 25 | overdue status | today after adjusted due | status `overdue` |
| 26 | due today status | today equals adjusted due | status `due-today` |
| 27 | due soon status | due within 7 days | status `due-soon` |
| 28 | upcoming status | due more than 7 days away | status `upcoming` |
| 29 | Hebrew alias | payer type `עצמאי` in client | maps to `self-employed` |
| 30 | mapping workflow | JSON config with profile/options | plan generated successfully |

## Acceptance criteria

- All automated tests pass.
- No generated file contains full personal identity numbers in examples.
- No generated file contains passwords, card numbers, or one-time codes.
- All dates are deterministic.
- Exports preserve `ILS` currency and ₪ display where text formatting is used.
- Schedules remain useful when estimates are replaced with official amounts.
- Every workflow instructs official verification before payment.

## Manual spot checks

### Check 1: start month interpretation

Input `2026-01` should create a January coverage period with a February payment target. This prevents accidental use of payment month as coverage month.

### Check 2: first three rows

For any production plan, manually inspect the first three obligations:

1. period start;
2. period end;
3. statutory due date;
4. adjusted due date;
5. reminder dates;
6. amount source;
7. action list.

### Check 3: year boundary

Input starting `2026-11` for 4 months should create periods November, December, January, and February, with payment targets in the following months.

### Check 4: calendar import

Import ICS into a test calendar first. Confirm all-day event behavior and duplicate handling before importing into an operational calendar.


## Additional web-validation scenarios

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 24 | web-validated defaults | import `ContributionPolicy()` | self-employed rates 7.70% and 18.00% |
| 25 | employer Form 102 default rates | employer payroll ₪20,000 | calculation uses 8.78% and 19.77% combined rates |
| 26 | no-income consumer default | consumer without amount override | amount is ₪266 |
| 27 | official override wins | `--amount 1234` | scheduler uses ₪1,234.00 regardless of defaults |
| 28 | standing-order due day | `--due-day 22` | statutory due date uses the 22nd of the following month |
