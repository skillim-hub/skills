# Test Scenarios

Use these scenarios for manual QA, automated tests, and migration checks.

| # | Scenario | Inputs | Expected result |
|---|---|---|---|
| 1 | Equal zero-interest plan | ₪1,200, 6 payments | Six payments of ₪200.00 |
| 2 | Single payment | ₪999, 1 payment | One payment equals cash price |
| 3 | Down payment | ₪9,800, ₪2,800 down, 4 payments | Financed amount is ₪7,000 |
| 4 | Interest only | ₪3,600, 12 payments, 7.5 percent | Interest is positive and final balance is zero |
| 5 | Per-installment fee | ₪1,200, 6 payments, ₪2.90 fee | Total monthly fees are ₪17.40 |
| 6 | Upfront fee | ₪1,000, 2 payments, ₪50 upfront | Total fees include ₪50 |
| 7 | Percent upfront fee | ₪2,000, 10 payments, 2.5 percent | Upfront fee is ₪50 |
| 8 | Zero interest with fee | ₪1,200, 6 payments, ₪1.50 fee | Finance charge is positive |
| 9 | High upfront fee | ₪1,000, 3 payments, ₪120 upfront | Warning is emitted |
| 10 | Missing date | ₪500, 5 payments | Warning asks for date rule |
| 11 | Date format with slash | First due date 15/07/2026 | Date parses and formats as 15/07/2026 |
| 12 | Date format with dash | First due date 15-07-2026 | Date parses and formats as 15/07/2026 |
| 13 | ISO date | First due date 2026-07-15 | Date parses and formats as 15/07/2026 |
| 14 | Month-end clipping | First due date 31/01/2026 | February due date clips to 28/02/2026 |
| 15 | Invalid price | Cash price ₪0 | `PRICE_MUST_BE_POSITIVE` |
| 16 | Invalid installment count | 0 payments | `INSTALLMENTS_MUST_BE_POSITIVE` |
| 17 | Down payment equals price | ₪100 price, ₪100 down | `DOWN_PAYMENT_OUT_OF_RANGE` |
| 18 | Negative rate | -0.1 percent | `RATE_MUST_NOT_BE_NEGATIVE` |
| 19 | Negative fee | -₪1 fee | `FEE_MUST_NOT_BE_NEGATIVE` |
| 20 | Invalid date | 2026/31/12 | `INVALID_DATE` |
| 21 | Compare plans | 3 and 12 payments | Results sorted by total paid |
| 22 | Refund after partial payment | 12 payments, 4 paid | Remaining principal is reported |
| 23 | Async calculation | Valid request | Same total as sync calculation |
| 24 | VAT-exclusive business quote | `vat_included=False` | VAT warning is emitted |
| 25 | Long plan | 48 payments | Long-term warning is emitted |
| 26 | Custom rounding | Rounding ₪0.05 | Money fields use the requested quantum |
| 27 | JSON serialization | Any valid plan | Hebrew and shekel sign are not escaped when requested |
| 28 | CLI JSON output | Calculate command with `--output json` | Valid JSON with environment field |
| 29 | Disclosure checklist | Consumer plan | Contains legal-review item |
| 30 | Invalid environment | Client environment `dev` | `INVALID_ENVIRONMENT` |

| 25 | VAT split from gross | `vat_components_from_gross("118")` | Net ₪100, VAT ₪18 |
| 26 | Gross from net | `gross_from_net("100")` | Gross ₪118 |
| 27 | Cancellation cap below ₪100 | `statutory_cancellation_fee_cap("1000")` | ₪50 |
| 28 | Cancellation cap at ₪100 | `statutory_cancellation_fee_cap("3000")` | ₪100 |
| 29 | CLI VAT JSON | `installment-calculator vat --gross 118` | JSON with net, VAT, gross |
| 30 | CLI cancellation cap JSON | `installment-calculator cancellation-fee-cap --total 3000` | JSON cap ₪100 |
