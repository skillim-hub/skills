# Test Scenarios

Use these scenarios for manual QA, automated fixtures, and acceptance checks.

| ID | Scenario | Input focus | Expected result |
|---:|---|---|---|
| 1 | B2B tax invoice above the 15/06/2026 threshold | ₪18,000 before VAT, business customer | Allocation required warning until number is stored. |
| 2 | B2B tax invoice below threshold | ₪100 before VAT | No allocation required. |
| 3 | Consumer tax invoice | Consumer customer type | No allocation required by helper logic. |
| 4 | Osek patur receipt | `issuer.status: patur`, receipt | VAT is ₪0.00 and validation passes. |
| 5 | Osek patur tax invoice | `issuer.status: patur`, tax invoice | Validation error. |
| 6 | Tax invoice receipt paid by transfer | Lines plus payment | Validation passes and totals include VAT. |
| 7 | Receipt without payment | Receipt with empty payments | Validation error. |
| 8 | Credit note with original reference | Original number and reason | Negative subtotal, VAT, and total. |
| 9 | Credit note without original reference | Missing original number | Validation error. |
| 10 | Credit note without reason | Missing reason | Warning. |
| 11 | Foreign currency with exchange note | USD and note containing exchange data | Validation passes without exchange warning. |
| 12 | Foreign currency without exchange note | USD and empty notes | Warning about exchange-rate note. |
| 13 | Zero-rate export with basis | `vat_rate: 0`, basis present | VAT is zero and no zero-rate mismatch warning. |
| 14 | Zero-rate basis with standard VAT line | Basis present and VAT not zero | Warning about mismatch. |
| 15 | Fixed discount | `discount: 50` | Subtotal decreases by ₪50.00. |
| 16 | Percentage discount | `discount_percent: 10` | Subtotal decreases by 10%. |
| 17 | Excessive discount | Discount greater than line amount | Validation error. |
| 18 | Invalid issuer tax id | Less than 9 digits | Validation error. |
| 19 | Invalid customer tax id | Less than 9 digits | Validation error. |
| 20 | Legacy 2024 VAT | Date before 01/01/2025 | Default VAT is 17%. |
| 21 | Current VAT | Date on or after 01/01/2025 | Default VAT is 18%. |
| 22 | Future allocation threshold | Year after configured table | Latest configured threshold is used. |
| 23 | Stored document id | Create then render by id | Same document is resolved from store. |
| 24 | Wrong environment id lookup | Create in sandbox, read in production | Not found error. |
| 25 | Sync allocation client | Mocked HTTP response | Payload and authorization header are sent. |
| 26 | Async allocation client | Mocked async HTTP response | Payload and authorization header are sent. |
| 27 | Hebrew renderer | Date `15/06/2026` | Rendered output uses `DD/MM/YYYY` and ₪ for ILS. |
| 28 | CLI example | `invoice-generator example --kind receipt` | Valid JSON receipt sample is printed. |
| 29 | CLI create chain | Create, extract id, render id | Rendered Hebrew draft is produced. |
| 30 | Compile scripts | `python -m compileall scripts/ -q` | No syntax errors. |
| 31 | January 2026 allocation threshold | 15/01/2026, ₪10,000.01 before VAT, business customer | Allocation required because amount exceeds ₪10,000.00. |
| 32 | January 2026 exact threshold | 15/01/2026, exactly ₪10,000.00 before VAT | No allocation required because amount does not exceed the threshold. |
| 33 | June 2026 allocation threshold | 15/06/2026, ₪5,000.01 before VAT, business customer | Allocation required because amount exceeds ₪5,000.00. |
| 34 | June 2026 exact threshold | 15/06/2026, exactly ₪5,000.00 before VAT | No allocation required because amount does not exceed the threshold. |
| 35 | Zero-rate B2B invoice above threshold | Israeli business customer, amount above threshold, `vat_rate: 0` | No allocation required by helper because VAT component is zero. |
| 36 | Missing customer tax id for allocation candidate | Business customer above threshold without `tax_id` | Warning asks for customer tax id before official request. |

