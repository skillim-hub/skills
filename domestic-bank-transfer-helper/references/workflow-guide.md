# End-to-End Workflow Guide

Use these workflows to apply the helper in routine Israeli payment operations. Keep bank authorization, user permissions, and final submission inside the bank or approved payment system.

## Workflow 1: single supplier payment by a freelancer

1. Receive invoice and confirm supplier identity.
2. Compare recipient name, bank code, branch, and account with supplier master data.
3. Run validation:

   ```bash
   domestic-bank-transfer-helper --env sandbox validate      --recipient-name "Example Supplier Ltd"      --bank-code 12      --branch-code 456      --account-number 123456789      --amount-ils "2450.80"      --value-date "03/06/2026"      --purpose "Invoice 1007"      --reference "INV-1007"
   ```

4. Resolve errors before continuing.
5. Review warnings, especially branch padding, missing purpose, unknown bank code, and confirmation notes.
6. Copy normalized values into the bank portal only after review.
7. Save bank confirmation with the invoice.

## Workflow 2: urgent Zahav supplier payment

1. Confirm business reason for same-day transfer.
2. Verify bank details using an independent trusted channel.
3. Capture approval before bank entry.
4. Create a local record:

   ```bash
   CREATE_RESPONSE="$(domestic-bank-transfer-helper --env production create      --recipient-name "Critical Supplier Ltd"      --bank-code 12      --branch-code 456      --account-number 123456789      --amount-ils "18500"      --value-date "03/06/2026"      --purpose "Urgent equipment repair"      --reference "REPAIR-77"      --same-day      --approved-by "Finance Manager")"
   ```

5. Extract the identifier:

   ```bash
   TRANSFER_ID="$(printf '%s' "$CREATE_RESPONSE" | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')"
   ```

6. Build the payload:

   ```bash
   domestic-bank-transfer-helper --env production payload "$TRANSFER_ID"
   ```

7. Check bank cutoff and Zahav fee.
8. Submit in the bank portal with proper authorization.
9. Store final bank confirmation and approval record.

## Workflow 3: payroll MASAV batch

1. Export employee payment rows from payroll.
2. Include employee name, bank code, branch, account number, net salary, value date, and salary month.
3. Validate the CSV:

   ```bash
   domestic-bank-transfer-helper --env sandbox batch payroll.csv --json-output
   ```

4. Fix every row with `valid=false`.
5. Re-run validation until all rows pass.
6. Review warnings for weekend dates, missing purpose, unknown bank codes, and padded branches.
7. Generate the bank-specific MASAV file only after validation.
8. Upload through the bank or payroll system.
9. Reconcile accepted and rejected rows after bank response.
10. Keep payroll data access restricted because salary and account details are sensitive personal data.

## Workflow 4: customer refund

1. Receive refund approval from customer support or accounting.
2. Request official bank details from the customer through an approved channel.
3. Avoid storing extra personal data beyond what the refund requires.
4. Validate with purpose `refund` and a source order or credit note.
5. Use MASAV for non-urgent refunds.
6. Use Zahav only when same-day settlement is approved and justified.
7. Save the refund ticket and bank confirmation together.

## Workflow 5: rent or recurring payment

1. Confirm lease or recurring payment agreement.
2. Capture recipient bank confirmation once and review when details change.
3. Validate amount and value date each period.
4. Use `recurring=true` for routing guidance.
5. Keep purpose clear, such as `Rent 06/2026`.
6. Review changes in bank details as high-risk changes requiring independent confirmation.

## Workflow 6: tax or statutory payment

1. Confirm voucher, period, entity number, and amount.
2. Use purpose such as `VAT 05/2026`, `National Insurance 06/2026`, or `Withholding tax 05/2026`.
3. Verify due date separately from the value date.
4. Validate bank details and amount.
5. Store official voucher and bank confirmation.
6. Avoid inferring legal compliance from a successful technical validation.

## Workflow 7: migration from spreadsheet approval

1. Map spreadsheet columns to the request schema.
2. Add missing columns for purpose, reference, source document, and approver.
3. Export to CSV.
4. Run `batch` in sandbox.
5. Fix formatting failures, especially branch padding and account number separators.
6. Add approval rules for production.
7. Archive the previous spreadsheet template after the controlled workflow is accepted.

## Workflow 8: bank-detail change

1. Treat every changed bank detail as high-risk.
2. Compare old and new details.
3. Confirm the new details through a trusted channel not controlled by the original change request.
4. Run validation with the new details.
5. Add a note in the approval record.
6. Do not reuse an old successful transfer as proof of ownership.

## Workflow 9: high-value owner withdrawal

1. Confirm business authorization and tax/accounting treatment separately.
2. Select Zahav when same-day finality or high value requires it.
3. Capture approver and source document.
4. Verify bank details independently.
5. Run validation in production mode.
6. Resolve warnings before portal entry.
7. Reconcile bank confirmation.

## Workflow 10: support triage after rejection

1. Capture bank rejection message.
2. Find the local record by identifier.
3. Review normalized fields and issues.
4. Compare the bank portal fields with the normalized payload.
5. Correct source data, not only the portal entry.
6. Add the rejected case to `references/test-scenarios.md` when it represents a new pattern.
