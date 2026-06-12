# Test Scenarios

Use these scenarios for acceptance testing, accountant review, and regression coverage.

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 1 | B2B invoice above 01-06-2026 threshold | Tax invoice/receipt, 15-06-2026, ₪6,000 before VAT, Israeli buyer VAT number | Allocation required; VAT is ₪1,080; send approval request. |
| 2 | B2B invoice below 01-06-2026 threshold | Tax invoice, 15-06-2026, ₪4,900 before VAT | Allocation not required; validate invoice normally. |
| 3 | January 2026 threshold | Tax invoice, 15-02-2026, ₪9,999 before VAT | Allocation not required because threshold is above ₪10,000. |
| 4 | January 2026 above threshold | Tax invoice, 15-02-2026, ₪10,001 before VAT | Allocation required. |
| 5 | VAT calculation mismatch | Payment ₪6,000 and VAT ₪1,000 | Validation error; expected VAT ₪1,080 at 18%. |
| 6 | Total mismatch | Payment ₪6,000, VAT ₪1,080, total ₪7,000 | Validation error; expected total ₪7,080. |
| 7 | Invalid seller VAT number | Seller number `123456789` | Validation error before API call. |
| 8 | Missing buyer VAT number | Above-threshold Israeli B2B tax invoice with no customer VAT number | Validation error; buyer VAT number required. |
| 9 | Foreign customer | Zero-rate export service to non-Israeli company | No Chashbonit Yisrael allocation request; keep export evidence. |
| 10 | Private consumer | Israeli private buyer, ₪8,000 before VAT | No B2B allocation required; issue consumer invoice/receipt according to bookkeeping rules. |
| 11 | Pro-forma before payment | Document code `332`, cash-basis supplier | Optional preliminary allocation confirmation; not input VAT deduction evidence. |
| 12 | Batch partial failure | Three invoices in batch, one returns code `460` | Store two confirmations; fix or decide on the failed invoice separately. |
| 13 | Old invoice date | API returns code `434` | Check retroactive request rules; do not change invoice facts just to pass validation. |
| 14 | Future invoice date | API returns code `435` | Use actual printed invoice date. |
| 15 | Held invoice continuation | Substantive refusal and user chooses continue | Submit `Continue` decision and print input-tax non-deduction notice. |
| 16 | Reverse charge path | Refusal followed by agreed reverse charge | Send special approval request with zero VAT and action value required by the API. |
| 17 | Customer verification | Recipient has full allocation number and supplier VAT number | Call invoice-information details endpoint and compare returned fields. |
| 18 | PCN874 reporting | Allocation number `20240704061109183186068226` | Store full value and report right-most 9 digits where required. |

## Regression expectations

- A threshold test must always use the invoice date, not the current date.
- A threshold test must always use amount before VAT.
- The validation layer must stop malformed VAT numbers before network calls.
- The API client must keep sandbox and production URLs separate.
- Error handling must expose code, parameter, and location to the caller.
