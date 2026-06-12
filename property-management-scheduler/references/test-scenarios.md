# Test Scenarios

Use these scenarios for manual validation, automated tests, and user acceptance review.

| # | Scenario | Input | Expected result |
|---|---|---|---|
| 1 | Create residential property | Address and city in Hebrew | Property id starts with `prop_`. |
| 2 | Reject empty address | Empty address, valid city | Validation error. |
| 3 | Add email tenant | Property id, name, email | Tenant id starts with `ten_`. |
| 4 | Reject email channel without email | Preferred channel email, no email | Validation error. |
| 5 | Add SMS tenant | Valid Israeli phone | Tenant saved with phone. |
| 6 | Reject bad phone | `12345` | Validation error. |
| 7 | Create lease | Valid tenant, dates, rent | Lease stores rent with two decimals. |
| 8 | Reject lease ending before start | End date before start | Validation error. |
| 9 | Reject due day 31 | Due day 31 | Validation error. |
| 10 | Generate three rent charges | Lease, start date, months 3 | Three due dates generated. |
| 11 | Avoid duplicate charges | Generate same range twice | Second call returns empty list. |
| 12 | Stop at lease end | Request months beyond end | Charges stop after final valid due date. |
| 13 | Record full payment | Charge, full amount, reference | Status becomes paid. |
| 14 | Record partial payment | Charge, lower amount | Status becomes partial. |
| 15 | Reject overpayment | Charge, amount above expected | Validation error. |
| 16 | Mark overdue | Date after due plus grace | Charge status becomes overdue. |
| 17 | Generate rent reminder | Charge id | Hebrew message contains ₪ amount and DD/MM/YYYY date. |
| 18 | Log communication | Tenant, property, channel, body | Communication id starts with `comm_`. |
| 19 | Build daily agenda | Date with rent and communication | Counts reflect due items. |
| 20 | Create urgent maintenance | Gas, fire, electricity, or flood words | Severity is urgent. |
| 21 | Create high maintenance | Leak or mold report | Severity is high. |
| 22 | Complete maintenance | Existing task | Status is completed and timestamp is set. |
| 23 | Export accounting pack | Paid charge inside period | Total equals paid amount. |
| 24 | Exclude unpaid charge from export | Pending charge | Total excludes pending amount. |
| 25 | Save and reload store | File-backed client | Reloaded client sees records. |
| 26 | Async property creation | Await async method | Record is created. |
| 27 | Async agenda | Await agenda method | Date is returned in ISO format. |
| 28 | Hebrew JSON output | Example script | Hebrew remains readable, not escaped. |
| 29 | Production environment flag | `--env production` | Client accepts production mode. |
| 30 | Sandbox isolation | Separate store paths | Records do not mix. |
| 31 | Manual review notice | Deposit deduction request | Automation stops; reviewer handles. |
| 32 | Tenant privacy request | Export contact details | Verify identity and minimize disclosure. |
| 33 | Contractor entry request | Task needs apartment entry | Tenant consent and time window are recorded. |
| 34 | Accounting review | Commercial property | VAT and document issuance are reviewed externally. |
| 35 | Backup recovery | Store file damaged | Restore backup and rerun validation. |

## Acceptance thresholds

1. At least 20 automated tests pass.
2. Public Markdown contains no organization marks, visual assets, or emoji.
3. Hebrew pages contain no nikud and use ₪ plus DD/MM/YYYY examples.
4. CLI examples print valid JSON.
5. Package import works with `from property_management_scheduler import PropertyManagementScheduler`.
6. `python -m compileall scripts/ -q` exits successfully.


## Reference value checks

| # | Scenario | Input | Expected result |
|---:|---|---|---|
| 35 | Israel Invoices threshold before June 2026 | `31/05/2026` | Threshold is `10000.00`. |
| 36 | Israel Invoices threshold from June 2026 | `01/06/2026` | Threshold is `5000.00`. |
| 37 | Bank of Israel host | Reference values | Host starts with `https://edge.boi.gov.il/`. |
