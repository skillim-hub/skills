# Troubleshooting Guide

Use this guide when validation fails, a bank form rejects normalized fields, or an operator cannot decide between MASAV and Zahav.

## Bank rejects branch code

Possible causes:

- Branch code was entered without required leading zeroes.
- Branch code belongs to a different bank.
- Branch closed, merged, or moved.
- Bank portal uses a branch list that differs from the local reference table.
- Operator pasted the account number into the branch field.

Actions:

1. Confirm the bank and branch from an official recipient bank confirmation.
2. Enter branch as three digits.
3. Keep bank code and branch code in separate fields.
4. Avoid padding beyond three digits.
5. Escalate to the bank when a valid branch is still rejected.

## Unknown bank code warning

Possible causes:

- Local reference table is stale.
- Recipient supplied an incorrect code.
- Bank merger, brand change, or special clearing code is involved.
- Test data uses a nonstandard code.

Actions:

1. Treat the warning as a manual verification task.
2. Confirm current bank code from the bank, recipient, or bank portal list.
3. Update local reference data after confirmation.
4. Do not block automatically unless policy requires strict allow lists.

## Invalid account number

Possible causes:

- Account number includes branch prefix.
- Account number is too short after removing separators.
- Operator copied an IBAN or foreign account into a domestic field.
- Digit grouping from a PDF was copied incorrectly.

Actions:

1. Remove spaces and hyphens.
2. Keep only the domestic account number in the account field.
3. Confirm expected account length with the recipient bank when uncertain.
4. Request a new bank confirmation if the recipient cannot explain the format.

## Amount rejected

Possible causes:

- Amount contains a currency word instead of a number.
- Amount is zero or negative.
- Bank daily limit or user authorization limit is lower than the payment.
- Amount requires Zahav or additional approval.

Actions:

1. Enter a positive numeric ₪ amount.
2. Compare amount with invoice, payroll run, refund approval, or voucher.
3. Check bank limits and user permissions.
4. Add approver for production and high-value transfers.
5. Use Zahav when same-day finality or high value requires it.

## Value date warning or error

Possible causes:

- Date is in the past.
- Date uses unsupported format.
- Date falls on Friday, Saturday, a holiday eve, or a listed closure day.
- Bank holiday or special closure is not represented in the helper.
- Operator confused invoice date with value date.

Actions:

1. Use `DD/MM/YYYY`, `DD-MM-YYYY`, or `YYYY-MM-DD`.
2. Select today or a future date.
3. Treat Friday and holiday eves as short-day candidates and Saturday or holidays as closure candidates.
4. Check Bank of Israel operating-day calendars, bank cutoffs, and branch notifications separately.
5. Keep due date and value date as separate business concepts.

## MASAV versus Zahav mismatch

Possible causes:

- Manual MASAV selected for an urgent payment.
- Manual MASAV selected for a high-value payment.
- Recurring or batch payment was incorrectly marked as urgent.
- Operator selected Zahav out of habit despite routine processing needs.

Actions:

1. Review urgency, amount, settlement finality, and fees.
2. Use MASAV for routine, batch, and recurring payments.
3. Use Zahav for same-day, urgent, and high-value payments after approval.
4. Record the reason when overriding the recommendation.

## Missing purpose warning

Possible causes:

- Operator expects the invoice attachment to explain the payment.
- Bank reference field is used for all context.
- Payroll or tax period was omitted.
- Refund ticket was not linked.

Actions:

1. Add a short purpose: invoice, salary month, rent month, refund, or tax period.
2. Keep sensitive personal data out of the bank reference when not required.
3. Store the full explanation in the internal payment record.

## Record not found

Possible causes:

- Wrong `--env` selected.
- Different `DOMESTIC_TRANSFER_STATE_DIR` is in use.
- Local state file was deleted.
- Identifier was copied incorrectly.

Actions:

1. Run `domestic-bank-transfer-helper --env sandbox list`.
2. Check the state directory used during `create`.
3. Use the same environment for `create`, `show`, and `payload`.
4. Recreate the record when the state file is intentionally temporary.

## Payroll batch fails

Possible causes:

- One row has missing recipient name.
- One account number is invalid.
- Salary amount has commas or currency text in an unsupported format.
- Value date is in the past.
- CSV has mismatched headers.

Actions:

1. Validate with `--json-output`.
2. Sort failures by field.
3. Correct source payroll data, not only the exported CSV.
4. Re-export and rerun validation.
5. Keep rejected examples for regression tests.

## Production warning about approver

Possible causes:

- `--env production` was selected.
- Amount is above the production approval threshold.
- Approver was not recorded in the request.
- Approval exists in email but not in the payment record.

Actions:

1. Add `--approved-by` with the approver name, role, or ticket.
2. Keep approval evidence outside public logs when it contains personal data.
3. Re-run validation before bank portal entry.

## Data protection issue

Possible causes:

- Full account numbers appear in screenshots, chat, or logs.
- Payroll files are shared too broadly.
- Refund files contain unnecessary customer details.
- References include identity numbers or private notes.

Actions:

1. Redact account numbers in routine reports.
2. Restrict access to payroll and refund files.
3. Store only data needed for payment operations.
4. Remove personal data from bank references unless required by the payment purpose.

## Escalation checklist

Escalate to the bank or qualified professional when:

- The bank portal rejects a field that passes validation.
- A high-value transfer is unusual for the business.
- Recipient bank details changed unexpectedly.
- Money laundering, fraud, sanctions, tax, or privacy questions arise.
- The transfer involves a court order, estate, lien, garnishment, or regulated trust.
