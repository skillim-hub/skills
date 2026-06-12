# Test Scenarios

Use these scenarios for QA, regression tests, support training, and acceptance review. Expected outcomes assume current date `02/06/2026`.

| # | Scenario | Input highlights | Expected result |
|---:|---|---|---|
| 1 | Routine supplier MASAV | Bank 12, branch 456, account 123456789, ₪2,450.80, value date 03/06/2026 | Valid; recommend MASAV |
| 2 | Urgent supplier payment | Same as scenario 1, `same_day=true` | Valid; recommend Zahav |
| 3 | High-value transfer | Amount ₪1,000,000, method auto | Valid; recommend Zahav |
| 4 | High-value MASAV override | Amount ₪1,000,000, method masav | Valid with high-value MASAV warning |
| 5 | Missing recipient | Empty recipient name | Invalid; required-field error |
| 6 | Unknown bank | Bank code 777 | Valid with unknown bank warning |
| 7 | Invalid bank format | Bank code ABC | Invalid bank-code error |
| 8 | Branch padding | Branch 7 | Valid with padding warning; normalized branch 007 |
| 9 | Branch too long | Branch 1234 | Invalid branch error |
| 10 | Account with separators | Account 12-345 678 | Valid when normalized to 12345678 |
| 11 | Account too short | Account 12 | Invalid account error |
| 12 | Amount with ₪ and comma | Amount ₪1,234.56 | Valid; parsed as 1234.56 |
| 13 | Zero amount | Amount 0 | Invalid amount error |
| 14 | Negative amount | Amount -10 | Invalid amount error |
| 15 | Text amount | Amount `ten` | Invalid amount error |
| 16 | Past value date | Value date 01/06/2026 | Invalid past-date error |
| 17 | Friday value date | Value date 05/06/2026 | Valid with calendar warning for possible short business day |
| 18 | Unsupported date | Value date 06.03.2026 | Invalid date-format error |
| 19 | Missing purpose | Empty purpose | Valid with purpose warning |
| 20 | Long reference | Reference longer than 35 characters | Valid with reference warning |
| 21 | Production high value without approver | Env production, amount ₪60,000, no approver | Valid with production approval warning |
| 22 | Production high value with approver | Env production, amount ₪60,000, approver present | Valid without production approval warning |
| 23 | Payroll batch valid | Two salary rows, value date 09/06/2026, purpose Salary 05/2026 | All rows valid; recommend MASAV |
| 24 | Payroll batch one bad row | One row account number 12 | Batch contains one invalid row |
| 25 | Refund to customer | Purpose refund, amount ₪320, known bank | Valid; recommend MASAV unless urgent |
| 26 | Urgent refund | Refund with `urgent=true` | Valid; recommend Zahav |
| 27 | Recurring rent | `recurring=true`, purpose Rent 06/2026 | Valid; recommend MASAV |
| 28 | Tax payment | Purpose VAT 05/2026, source document present | Valid; preserve source document |
| 29 | Changed bank details | Existing supplier, new account, amount ₪25,000 | Valid with independent confirmation info |
| 30 | Local record chain | Create record, extract `id`, call payload with same environment | Payload returned for valid record |
| 31 | Wrong environment lookup | Create in sandbox, show in production | Record not found |
| 32 | Invalid local record payload | Create invalid record, call payload | Payload raises validation error |
| 33 | Hebrew report | Valid request with Hebrew recipient and purpose | Human report uses ₪ and DD/MM/YYYY |
| 34 | Arabic-indic digits | Bank and account contain Arabic-indic digits | Digits normalize correctly |
| 35 | Hebrew digit input | Input contains mixed Hebrew text and digits | Non-digits removed from numeric fields |
| 36 | Same-day after cutoff | Same-day flag supplied after internal cutoff policy | Helper recommends Zahav; bank cutoff remains external check |
| 37 | Bank portal shorter reference | Bank limit lower than 35 characters | Shorten bank reference and preserve full internal reference |
| 38 | Salary personal data in reference | Reference contains unnecessary personal identifier | Warning should be handled by operational policy |
| 39 | Bank merger or code-format change | Bank code no longer appears in local table, or code becomes three digits | Unknown-bank warning triggers manual verification against official sources |
| 40 | Large batch | 500 rows with one invalid row | Reject or hold batch until invalid row is corrected |

## Acceptance criteria

- Every scenario with an expected error returns `valid=false`.
- Every scenario with expected warnings returns `valid=true` unless an error is also present.
- Batch validation reports row-level failures without hiding successful rows.
- CLI record chaining uses the identifier from `create` in the next command.
- Production-mode warnings do not appear in sandbox-only checks unless the same business risk applies.

| 40 | Verified code 9 | Bank code 9 | Bank name normalizes to D.I. Postal Finance Ltd |
| 41 | Verified code 54 | Bank code 54 | Bank name normalizes to Bank of Jerusalem Ltd |
