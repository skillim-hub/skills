# Test Scenarios

Run these scenarios before using the tracker for payroll. Expected values assume default settings unless stated otherwise.

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 1 | New full-year 5-day employee | Hire `01/01/2024`, as-of `31/12/2024` | Annual accrued `12`, sick accrued `18` |
| 2 | Mid-year hire | Hire `01/07/2024`, as-of `31/12/2024` | Annual accrued `6`, sick accrued `9` |
| 3 | 6-day employee first year | Hire `01/01/2024`, 6-day week | Annual entitlement `14` |
| 4 | Contractual annual override | Override `22` days | Annual entitlement `22` |
| 5 | Annual leave Sunday-Thursday | `18/08/2024` to `22/08/2024`, 5-day week | Used `5` |
| 6 | Annual leave including Friday | `18/08/2024` to `23-08-2024`, 5-day week | Used `5` |
| 7 | Annual leave including Friday, 6-day | Same dates, 6-day week | Used `6` |
| 8 | Half-day annual leave | `days=0.5` | Deduct `0.5` |
| 9 | Unapproved annual leave | `approved=false` | No deduction |
| 10 | Duplicate annual leave | Two identical approved events | Double deduction; audit must catch duplicate |
| 11 | Sick one day | 1 day | Sick used `1`, paid equivalent `0` |
| 12 | Sick three days | 3 days | Paid equivalent `1` |
| 13 | Sick five days | 5 days | Paid equivalent `3` |
| 14 | Sick balance cap | Hire `01-01-2010` | Sick accrued capped at `90` |
| 15 | Sick negative balance | New employee, 10 sick days in first month | Negative sick warning |
| 16 | Miluim week | `absence_type=miluim`, 5 days | Miluim tracked, annual/sick unchanged |
| 17 | Birth and parenthood leave | `absence_type=parental`, 60 days | Parental tracked, annual/sick unchanged |
| 18 | Mourning within limit | `mourning`, 7 days | Mourning tracked, no warning |
| 19 | Mourning over limit | `mourning`, 8 days | Warning generated |
| 20 | Unknown employee | Event `employee_id=BAD` | Error raised |
| 21 | Reversed dates | End before start | Error raised |
| 22 | Invalid date format | `31.12.2024` | Error raised |
| 23 | Employee switches workweek | 6-day then 5-day in same year | Manual split or override required |
| 24 | Holiday inside vacation | Vacation includes Rosh Hashanah | Manual holiday adjustment required |
| 25 | Closed month correction | Prior event omitted | Add adjustment event; do not edit closed file |
| 26 | Consumer payslip check | Opening balances from payslip | Calculated balance matches or differences explained |
| 27 | Employee with opening sick balance | Opening `12`, current year accrual `18` | Sick accrued total `30` unless cap applies |
| 28 | Long sick event | 35 sick days | Long-sick warning generated |
| 29 | Annual negative balance approved | Balance `-2` | Warning retained with approval note |
| 30 | Hebrew CSV export | Export summary | UTF-8 BOM opens correctly in Excel |

## Detailed scenario scripts

The `scripts/examples/` directory includes runnable examples for:

1. Basic annual balance.
2. Sick pay calculation.
3. Miluim, birth and parenthood leave, and mourning.
4. CSV summary export.
5. Async client usage.

Run all automated tests:

```bash
python -m pytest
```

Expected result: all tests pass.

## Web-validated 2026 correction scenarios

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 31 | Six-day 12th seniority year | Hire `01/01/2013`, check 2024 | Annual entitlement is `23`, not `24` |
| 32 | Six-day 13th seniority year | Hire `01/01/2013`, check 2025 | Annual entitlement is `24` |
| 33 | Five-day 14th seniority year statutory floor | Hire `01/01/2010`, check 2023 | Annual entitlement remains capped at `20` unless a more generous arrangement applies |
| 34 | VAT reference isolation | VAT rate changes in business data | Leave balances remain unchanged because VAT is not used in leave math |
| 35 | 2026 miluim extension-order review | Worker or spouse served in reserve duty in 2026 | Add manual review note before closing annual leave balance |
