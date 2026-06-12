# Test Scenarios

Use these scenarios for automated tests, acceptance tests, and accountant review. Dates shown in user-facing examples use `DD/MM/YYYY`.

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 1 | Monthly schedule | Start `31/01/2026`, count 3 | `31/01/2026`, `28/02/2026`, `31/03/2026` |
| 2 | Monthly schedule without month-end anchor | Start `30/01/2026` | Next date `28/02/2026` |
| 3 | Quarterly schedule | Start `15/01/2026` | Next date `15/04/2026` |
| 4 | Yearly schedule | Start `29/02/2024` | Next date adjusted for non-leap year |
| 5 | Paused subscription | Status paused | No invoice generated |
| 6 | Cancelled subscription | Status cancelled | No new invoice generated |
| 7 | Empty line description | Blank description | Validation error |
| 8 | Zero quantity | Quantity `0` | Validation error |
| 9 | Negative price | Unit price `-1` | Validation error |
| 10 | VAT before 2025 | Issue `31/12/2024` | 17 percent default VAT |
| 11 | VAT from 2025 | Issue `01/01/2025` | 18 percent default VAT |
| 12 | VAT-exempt line | `exempt=True` | VAT amount `0.00` |
| 13 | Mixed taxable and exempt lines | One taxable, one exempt | VAT calculated only for taxable line |
| 14 | Tax ID with separators | `514-324-995` | Normalized to `514324995` |
| 15 | Missing leading zeros | Tax ID `18` | Normalized to `000000018` |
| 16 | Invalid checksum | `514324996` | Validation fails |
| 17 | January 2026 threshold | Issue `01/01/2026` | Threshold `₪10,000` |
| 18 | June 2026 threshold | Issue `01/06/2026` | Threshold `₪5,000` |
| 19 | Allocation below January 2026 threshold | Subtotal `₪9,999.99`, issue `31/01/2026` | No allocation required |
| 20 | Allocation at January 2026 threshold | Subtotal `₪10,000`, issue `31/01/2026` | Allocation required |
| 21 | Allocation below June 2026 threshold | Subtotal `₪4,999.99`, issue `01/06/2026` | No allocation required |
| 22 | Allocation at June 2026 threshold | Subtotal `₪5,000`, issue `01/06/2026` | Allocation required |
| 23 | Receipt document | Receipt above threshold | No allocation required by helper |
| 24 | Tax invoice receipt | Above threshold | Allocation required |
| 25 | Pro forma | Above threshold | No final allocation request by helper |
| 26 | Duplicate subscription ID | Same ID created twice | Validation error |
| 27 | Duplicate invoice run | Same period generated twice | Existing invoice reused or blocked |
| 28 | Sync allocation transport | Mock transport returns allocation | Response parsed and stored |
| 29 | Async allocation transport | Async mock returns allocation | Response parsed and stored |
| 30 | Async fallback to sync transport | No async transport | Sync transport called in thread |
| 31 | Allocation response with `confirmation_number` | Official-style lower-case response | Allocation number parsed |
| 32 | Allocation response with `Confirmation_Number` | Official-style upper-case response | Allocation number parsed |
| 33 | Allocation rejection | Response has errors and no number | Invoice remains candidate |
| 34 | Credit note | Original invoice exists | Negative credit document linked to original |
| 35 | Import/export state | JSON state exported and imported | Sequence continues correctly |
| 36 | Manual allocation fallback | Adapter unavailable | Required request details produced for manual service |
| 37 | Held invoice | Service returns substantive hold | Operator sees four alternatives |
| 38 | Stale 2026 yearly threshold | Custom config says `₪15,000` | Test fails until effective-date config is updated |
| 39 | Official endpoint conflict | Held-decision path needed | Adapter requires portal-verified endpoint |
| 40 | Branding audit | Public files checked | No branding, author, visual-asset, mark, or emoji issues |
