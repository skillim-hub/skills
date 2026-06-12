# Test Scenarios

Use these scenarios for manual QA, demonstrations, and regression testing. The automated pytest suite covers the calculation engine; these examples cover operator judgment and workflow quality.

| # | Scenario | Key inputs | Expected check |
|---:|---|---|---|
| 1 | Standard fixed business loan | ₪250,000, 72 months, 6.5% | Final balance is zero |
| 2 | Zero-interest family loan | ₪60,000, 24 months, 0% | Payment is principal divided by term |
| 3 | Prime + margin loan | Prime 6%, margin 1.5% | Annual rate shown as 7.5% |
| 4 | Prime missing base rate | `rate_type=prime`, no `prime_rate` | Validation error |
| 5 | CPI base case | 4.2% interest, 2.5% CPI | CPI adjustment is positive |
| 6 | CPI zero case | 4.2% interest, 0% CPI | CPI adjustment is zero |
| 7 | CPI stress case | 4.2% interest, 5% CPI | Higher total paid than base |
| 8 | Negative CPI assumption | CPI `-0.01` | Model handles negative adjustment |
| 9 | Three-month grace | `grace_months=3` | First three periods are interest-only |
| 10 | Invalid full-term grace | grace equals term | Validation error |
| 11 | Balloon vehicle loan | 25% balloon | Lower interim payment and large final payment |
| 12 | Invalid 100% balloon | `balloon_percent=1` | Validation error |
| 13 | Extra repayment from VAT refund | Period 7 extra ₪25,000 | Schedule shortens or interest falls |
| 14 | Extra repayment above balance | Large late extra payment | Balance closes without going negative |
| 15 | Rate increase after year one | `rate_changes={"13":"0.085"}` | Period 13 uses new annual rate |
| 16 | Rate decrease after year one | `rate_changes={"13":"0.045"}` | Later interest is lower |
| 17 | Quarterly repayments | 60 months quarterly | 20 periods |
| 18 | Invalid quarterly term | 10 months quarterly | Validation error |
| 19 | Month-end start date | 31/01/2026 | Next due date is 28-02-2026 |
| 20 | Leap-year handling | 31-01-2028 | Next due date is 29-02-2028 |
| 21 | Origination fee comparison | Fee ₪1,500 | Effective cash cost includes fee |
| 22 | Early repayment fee | Fee ₪350 plus extra payment | Effective cash cost includes fee |
| 23 | Compare fixed vs prime | Same principal and term | Sorted by effective cash cost |
| 24 | Compare CPI scenarios | CPI 0%, 2.5%, 5% | Higher CPI raises total adjustment |
| 25 | JSON export | Any valid scenario | File contains scenario, summary, rows |
| 26 | CSV export | Any valid scenario | Row count equals generated periods |
| 27 | Hebrew date input | `01/07/2026` | Date parses correctly |
| 28 | ISO date input | `2026-07-01` | Date parses correctly |
| 29 | Decimal notation mistake | `annual_interest_rate=6.5` | Payment is obviously extreme; operator should correct to `0.065` |
| 30 | Missing principal | No `principal` key | CLI exits with error |

## Manual scenario template

```json
{
  "name": "manual QA scenario",
  "principal": "100000",
  "term_months": 60,
  "start_date": "01/07/2026",
  "rate_type": "fixed",
  "annual_interest_rate": "0.06",
  "payment_frequency": "monthly",
  "grace_months": 0,
  "balloon_percent": "0",
  "origination_fee": "0",
  "early_payment_fee": "0",
  "rate_changes": {},
  "extra_payments": {}
}
```

## Acceptance checks

- Inputs are preserved in the exported JSON.
- Rows are ordered by period.
- Due dates progress consistently.
- Opening balance of period N equals closing balance of period N-1, after rounding.
- CPI adjustment is shown separately from interest.
- The final standard amortizing row closes the balance.
- Comparison output includes `name`, `rate_type`, `term_months`, and summary fields.
