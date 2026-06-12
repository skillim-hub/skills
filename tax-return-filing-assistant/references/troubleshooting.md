# Troubleshooting Guide

## General filing problems

| Problem | Likely cause | Diagnostic steps | Resolution |
|---|---|---|---|
| Required form is unclear | User supplied role but not income type | Ask for tax year, salary/business/rental/capital/foreign income, employees, supplier payments, and turnover | Run form recommendation again |
| Deadline conflicts between sources | Filing year, online/paper status, representative extension, or official update differs | Identify tax year and submission channel; check official current instructions | Use official deadline and keep planning reminders only |
| User expects guaranteed refund | Withholding comparison is incomplete | Compare Form 106 totals, credits, deductions, and prior payments | State that refund depends on official calculation |
| Personal data risk | User pasted full ID, payroll, or bank data | Stop processing unnecessary sensitive data | Ask for redacted totals or masked documents |
| Tax year missing | User described situation without year | Request tax year before field/deadline guidance | Continue only after tax year is known |

## Form 1301 issues

### Business profit does not match bookkeeping

Check:

1. Revenue ledger.
2. Receipt sequence.
3. Credit notes.
4. Bank deposits.
5. VAT/exempt-occupation reports.
6. Year-end journal entries.
7. Personal expenses removed from business expenses.

Resolution: reconcile the profit and loss report before preparing Form 1301. Do not force a balancing number into the return.

### Rental track is uncertain

Check:

1. Monthly rent amount.
2. Number of apartments.
3. Residential or commercial use.
4. Ownership share.
5. Expenses available.
6. Effect on surtax and National Insurance where relevant.

Resolution: compare available tracks and advise official/professional review when amounts are near thresholds or ownership is shared.

### Foreign income is present

Check:

1. Israeli tax residency.
2. Foreign tax paid.
3. Treaty position.
4. Currency conversion method.
5. Foreign account or asset disclosure requirements.
6. New immigrant/returning resident relief period.

Resolution: prepare a separate foreign-income evidence schedule and avoid refund-only Form 135 unless official rules allow it.

## Form 135 issues

### Missing Form 106

Use payslips only as interim support. Request the official Form 106 from the employer. If the employer closed, collect available payroll slips, bank deposits, and National Insurance records, then seek official guidance.

### Donation credit rejected

Check that the receipt:

- Is in the taxpayer's name.
- Shows the institution details.
- Relates to the correct tax year.
- Refers to a recognized institution where required.
- Was not already claimed by the spouse or employer.

### Old refund year near deadline

Calculate the limitation date. Prioritize filing and official confirmation. Do not wait for non-essential optimization when the year is about to expire.

## Form 126 issues

### Employee total mismatch

Check monthly payroll for:

- Retroactive pay.
- Termination adjustment.
- Maternity leave.
- Reserve duty.
- Negative correction.
- Benefits in kind.
- Pension/study-fund adjustments.

Resolution: reconcile employee-by-employee and reissue corrected Form 106 if required.

### Invalid employee identity

Validate the number format and legal identity type. Preserve leading zeros. Confirm foreign worker handling in payroll software.

### Withholding payments do not match annual report

Compare monthly payroll liabilities to payment confirmations. Identify payments posted to wrong month or wrong withholding file.

## Form 856 issues

### Supplier certificate expired

Split payments by payment date. Apply the rate valid on each date. Request updated certificate for later payments.

### Payment amount is wrong

Check whether the report expects amount before or after VAT according to current instructions. Reconcile invoices, credit notes, and actual payments.

### Supplier appears under two names

Determine whether a legal entity changed. Do not merge different IDs. Correct supplier master data before reporting.

## Form 6111 issues

### Balance sheet does not balance

Check opening balances, closing entries, owner drawings, bank reconciliation, suspense accounts, and retained earnings. Export again only after the trial balance is closed.

### Account code mapping is uncertain

Use accounting software defaults only after review. Flag accounts mapped to “other” or “miscellaneous”. Request adviser review for material balances.

### Revenue differs from VAT reports

Classify differences:

- Exempt revenue.
- Out-of-scope revenue.
- Timing differences.
- Credit notes after period end.
- Foreign revenue.
- Manual journal entries.

Resolution: document differences and update the annual return totals if the accounting records were wrong.

## CLI problems

| CLI symptom | Cause | Fix |
|---|---|---|
| `No such option: --profile` | Command name omitted | Use `recommend --profile profile.json` |
| `Invalid value for FORM` | Unsupported form number | Use one of 1301, 135, 126, 856, 6111 |
| JSON parse error | Invalid profile JSON | Validate with `python -m json.tool profile.json` |
| No field found | Field ID typo | Run `fields FORM` to list valid field IDs |
| Validation warning about 6111 | Turnover threshold or requirement uncertainty | Verify current Form 6111 instructions |

## Escalation triggers

Recommend professional review when:

- Foreign income, foreign assets, or treaty issues exist.
- Capital gains involve non-Israeli brokers or complex loss offsets.
- Rental income is near exemption or surtax thresholds.
- A business has employees and supplier withholding corrections.
- Form 6111 mapping materially affects taxable income.
- Late filing, penalties, or prior-year amendments are involved.
- The user asks for tax planning rather than filing preparation.
