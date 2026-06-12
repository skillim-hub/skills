# Test Scenarios

Use these scenarios for acceptance testing, manual review, and regression checks.

| No. | Scenario | Input | Expected result |
|---:|---|---|---|
| 1 | Create private consultation claim | Private policy, ₪850, service 15/04/2026, submission 20/04/2026 | Claim id generated, status `submitted`, gap ₪850.00 |
| 2 | Create supplementary physiotherapy claim | Supplementary plan, ₪320 | Missing documents include plan and member details |
| 3 | Reject future service date | Service date after current date | `ValidationError` |
| 4 | Reject submission before service | Submission date one day before service | `ValidationError` |
| 5 | Reject zero amount | Amount `0` | `ValidationError` |
| 6 | Reject negative reimbursement | Reimbursement `-1` | `ValidationError` |
| 7 | Parse Israeli slash date | `31/05/2026` | Parsed as 31 May 2026 |
| 8 | Parse Israeli dash date | `31-05-2026` | Parsed as 31 May 2026 |
| 9 | Parse ISO date | `2026-05-31` | Parsed as 31 May 2026 |
| 10 | Reject dotted date | `31.05.2026` | `ValidationError` |
| 11 | Add receipt document | `tax_invoice_or_receipt` | Missing document list shrinks |
| 12 | Add missing document placeholder | `received=false` | Document appears but required item remains missing |
| 13 | Add partial reimbursement | Claim ₪1,200; reimbursement ₪300 | Gap ₪900 |
| 14 | Add full reimbursement | Claim ₪1,200; reimbursement ₪1,200 | Status becomes `paid` |
| 15 | Set follow-up date | Follow-up 10/06/2026 | Date stored and displayed as 10/06/2026 |
| 16 | Detect overdue claim | Follow-up 01/06/2026 and current date 04/06/2026 | Claim appears in overdue list |
| 17 | Paid claim not overdue | Paid status with old follow-up | Claim excluded from overdue list |
| 18 | Export CSV | One claim in store | CSV has headers and one row |
| 19 | Import CSV | Valid exported format | Claim imported and retrievable |
| 20 | Redacted JSON export | Claimant reference contains more than four characters | Reference is masked |
| 21 | Filter by status | One `in_review` claim | Only matching claim is returned |
| 22 | Filter by provider | Provider name with different case | Claim is returned |
| 23 | Private surgery checklist | Service kind `surgery` | Hospital discharge and procedure report are required |
| 24 | Medication checklist | Service kind `medication` | Prescription and pharmacy receipt are required |
| 25 | Storage path mismatch | Two different storage paths | Records are isolated by file |
| 26 | Corrupted JSON | Non-JSON file at storage path | `ClaimTrackerError` |
| 27 | Appeal after partial approval | Status changed to `appealed` with note | Timeline contains appeal event |
| 28 | Business handoff export | Claim tagged `bookkeeping` | CSV includes tags field |
| 29 | Async create and fetch | Async client writes a claim | Claim can be fetched asynchronously |
| 30 | Async summary | Async client has one claim | Summary count is one |
| 31 | Policy last four digits invalid | Value `77A8` | `ValidationError` |
| 32 | Unknown claim id | `missing` | `ClaimNotFoundError` |

## Manual acceptance script

1. Install package with `pip install -e .`.
2. Install development tools with `pip install -r requirements-dev.txt`.
3. Run `pytest`.
4. Run `python -m compileall scripts/ -q`.
5. Create a claim through the CLI.
6. Copy the returned claim id.
7. Add a document using that id.
8. Add a partial reimbursement.
9. Export CSV.
10. Open the CSV and confirm dates, amounts, and status values.
11. Export redacted JSON and check claimant reference masking.
12. Delete the sandbox storage file only after confirming backup behavior.
