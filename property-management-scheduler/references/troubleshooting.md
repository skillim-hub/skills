# Troubleshooting

## Installation

| Symptom | Diagnosis | Correction |
|---|---|---|
| `ModuleNotFoundError: property_management_scheduler` | Package root was not installed | Run `pip install -e .` from the extracted package directory. |
| CLI command not found | Editable install did not complete or environment changed | Activate the environment and rerun `pip install -e .`. |
| Typer import error | Runtime dependency missing | Run `pip install -e .` or install requirements. |
| Tests cannot import package | Pytest is running from the wrong directory | Run tests from the package root. |

## Data store

| Symptom | Diagnosis | Correction |
|---|---|---|
| Records disappear between commands | Different `--store` paths were used | Use the same store path for all commands. |
| JSON contains escaped Hebrew | Custom print call did not use `ensure_ascii=False` | Use package examples or `json.dumps(..., ensure_ascii=False, indent=2)`. |
| Store file is corrupted | Manual edit introduced invalid JSON | Restore backup and reapply changes through the client. |
| Production data mixed with tests | Same file used for sandbox and production | Separate store paths by environment. |

## Dates and amounts

| Symptom | Diagnosis | Correction |
|---|---|---|
| Date rejected | Format not recognized | Use DD/MM/YYYY, DD-MM-YYYY, or ISO in code. |
| Rent charge not created for a month | Lease ended before that due date | Extend or renew lease before generating charges. |
| Due day rejected | Day is outside 1 to 28 | Use a stable day to avoid invalid months. |
| Amount rejected | Non-numeric value or negative value | Use a numeric ₪ amount such as `5200` or `5200.50`. |
| Overpayment rejected | Paid amount exceeds charge | Record the exact charge amount and reconcile extra funds separately. |

## Tenant contact validation

| Symptom | Diagnosis | Correction |
|---|---|---|
| Tenant creation fails | Preferred channel requires missing contact detail | Add email for email channel or phone for phone-based channels. |
| Phone rejected | Number is not an Israeli local or international format | Use `0501234567` or `+972501234567`. |
| Email rejected | Address is malformed | Correct the email before saving. |
| Tenant opted out | Messaging integration refused delivery | Use another documented channel. |

## Rent collection

| Symptom | Diagnosis | Correction |
|---|---|---|
| Duplicate charges not created | Duplicate protection is active | Use `overwrite=True` only after review. |
| Charge marked overdue | Grace period expired | Record payment, change grace period, or follow up manually. |
| Partial payment not treated as paid | Amount is lower than expected | Keep partial status until the balance is received. |
| Reminder text looks wrong | Wrong charge id was used | Generate the message from the correct charge id. |

## Maintenance

| Symptom | Diagnosis | Correction |
|---|---|---|
| Priority too low | Report text lacked urgent terms | Override severity manually. |
| Contractor visit delayed | No due date or contractor was recorded | Add contractor and due date. |
| Completed task lacks evidence | Status changed before confirmation | Attach proof outside the JSON store and update notes. |
| Entry not coordinated | Task requires access to a rented unit | Schedule a tenant-approved time window. |

## Accounting export

| Symptom | Diagnosis | Correction |
|---|---|---|
| Export total is zero | No paid charges in period | Record payments or adjust date range. |
| Deposit appears missing | Deposits are stored on lease, not rent charges | Export lease records separately for deposit review. |
| VAT flag seems wrong | Configuration was not set | Set `ClientConfig(vat_registered=True)` where applicable. |
| Accountant needs different format | Local export is generic JSON | Transform JSON into the accounting system import format. |

## Safe escalation

Escalate to a qualified professional when any of these appears:

1. Eviction or termination notice.
2. Deposit deduction dispute.
3. Refusal to allow urgent repair access.
4. Structural defect, gas, electricity, fire, sewage, or flood risk.
5. Tax classification uncertainty.
6. Request to disclose tenant personal data.
7. Court, police, insurance, or municipal enforcement matter.


## Verified-source troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Bank of Israel endpoint fails | Old `edge.boi.org.il` host was copied from older material | Use `https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS`. |
| Commercial invoice threshold looks stale | 2026 threshold changed during the year | Use `reference-values --as-of 01/06/2026` and verify against the Tax Authority before issuing documents. |
| VAT rate in an accounting system differs | Accounting system has not been updated or transaction date differs | Stop issuance and verify rate, date, and invoice type with accounting support. |
