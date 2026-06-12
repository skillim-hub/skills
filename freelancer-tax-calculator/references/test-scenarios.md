# Test Scenarios

Use these cases for manual review, regression testing, and accountant-facing examples. Amounts are annual unless noted otherwise.

| ID | Scenario | Input highlights | Expected behavior |
|---:|---|---|---|
| 1 | Osek murshe without input VAT | Revenue ₪100,000 | Output VAT equals configured VAT rate times revenue. |
| 2 | Osek murshe with input VAT | Revenue ₪100,000, input VAT ₪3,400 | VAT payable is reduced by input VAT. |
| 3 | VAT refund position | Revenue ₪10,000, input VAT ₪3,000 | VAT payable is zero and refund position is positive. |
| 4 | Osek patur basic | Revenue ₪50,000 | VAT values are zero. |
| 5 | Osek patur with input VAT | Revenue ₪50,000, input VAT ₪1,000 | Input VAT is ignored with warning. |
| 6 | Osek patur near threshold | Revenue above warning ratio | Threshold warning appears. |
| 7 | Osek patur above threshold | Revenue above configured ceiling | Registration review warning appears. |
| 8 | Income-tax advances by revenue | Revenue ₪240,000, rate 8 percent | Annual advance equals ₪19,200. |
| 9 | Income-tax advances by profit | Revenue ₪240,000, expenses ₪60,000, rate 8 percent, base profit | Annual advance equals ₪14,400. |
| 10 | Zero advance rate | Rate 0 | Warning asks for official percentage. |
| 11 | Expenses exceed revenue | Revenue ₪20,000, expenses ₪30,000 | Estimated profit is zero. |
| 12 | National Insurance reduced tier only | Profit below reduced threshold | Regular tier is zero. |
| 13 | National Insurance regular tier | Profit above reduced threshold | Reduced and regular tiers are populated. |
| 14 | National Insurance ceiling | Profit above annual ceiling | Capped base equals ceiling. |
| 15 | Micro-business normative scenario | Osek patur, eligible revenue | Effective expenses use configured normative rate. |
| 16 | Micro-business normative scenario for low-turnover osek murshe | Osek murshe below configured patur ceiling with flag | Effective expenses use configured normative rate while VAT logic remains osek murshe. |
| 17 | Micro-business rejected above ceiling | Any business above ceiling with flag | Error `micro_business_ineligible`. |
| 18 | Negative revenue | Revenue -1 | Error `negative_amount`. |
| 19 | Invalid business type | `company` | Error `invalid_business_type`. |
| 20 | Invalid rate | Advance rate 8 | Error `invalid_rate`. |
| 21 | Invalid advance base | `cash` | Error `invalid_advance_base`. |
| 22 | Environment override | `FTC_VAT_RATE=0.17` | Output VAT uses override. |
| 23 | Saved scenario chain | Create then run by ID | Run loads the same payload. |
| 24 | Missing scenario | Unknown ID | Error `scenario_not_found`. |
| 25 | Gross-to-net helper | Gross ₪118 | Net ₪100 at 18 percent VAT. |
| 26 | CLI JSON output | `calculate --json` | JSON has `vat`, `income_tax_advances`, `national_insurance`, `summary`. |
| 27 | CLI VAT command | `vat --json` | JSON contains VAT-only section. |
| 28 | Async single calculation | `calculate_async` | Report equals sync result for key VAT fields. |
| 29 | Async batch calculation | Two payloads | Two reports returned. |
| 30 | Compile check | `python -m compileall scripts/ -q` | No syntax output and exit code 0. |

## Manual acceptance criteria

- All warnings remain visible.
- Money amounts are rounded to two decimals.
- JSON uses Unicode safely and keeps shekel symbols intact where displayed.
- Configuration changes alter calculations without code edits.
- Imports work after `pip install -e .`.
- The old hyphenated client path is not required.
