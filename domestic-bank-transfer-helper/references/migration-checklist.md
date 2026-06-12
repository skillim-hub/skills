# Migration Checklist

Use this checklist when replacing ad hoc payment spreadsheets, email approvals, or manual copy-paste routines with a controlled domestic-transfer preparation workflow.

## 1. Inventory current process

- List payment sources: accounting exports, payroll systems, CRM refunds, supplier portals, rent schedules, tax vouchers, and manual bank entries.
- List all current fields: payer, recipient, bank, branch, account, amount, value date, purpose, reference, requester, approver, source document, status, and bank confirmation.
- Identify sensitive fields such as account number, salary amount, refund details, and identity-related notes.
- Record who can create, approve, submit, and reconcile payments.

## 2. Map fields

| Current field | Target field | Notes |
|---|---|---|
| Supplier name | `recipient_name` | Use legal or account name. |
| Bank | `bank_code` | Store numeric bank code, not only bank name. |
| Branch | `branch_code` | Preserve leading zeroes. |
| Account | `account_number` | Keep branch separate from account. |
| Amount | `amount_ils` | Store ₪ value as a positive decimal. |
| Payment date | `value_date` | Use `DD/MM/YYYY` in operator-facing files. |
| Invoice or salary period | `purpose` | Keep short and clear. |
| Internal reference | `reference` | Keep within bank field limits. |
| Approval | `approved_by` | Required by local policy for high-risk payments. |
| Source document | `source_document_id` | Invoice, payroll run, voucher, refund ticket, or lease. |

## 3. Clean data

- Remove spaces and hyphens from numeric identifiers only after preserving the original source document.
- Normalize branch codes to three digits.
- Separate account numbers from branch codes.
- Replace ambiguous purposes such as `payment` with invoice, salary, rent, refund, or tax period.
- Remove unnecessary personal data from references.
- Confirm bank details for new or changed recipients.

## 4. Configure local workflow

- Install with `pip install -e .`.
- Install development tooling with `pip install -r requirements-dev.txt`.
- Run sandbox validation for sample files.
- Add a state directory for staged records using `DOMESTIC_TRANSFER_STATE_DIR`.
- Keep production state and sandbox state separate.
- Store full logs in a restricted location.

## 5. Validate batches

- Export a representative CSV.
- Run `domestic-bank-transfer-helper --env sandbox batch sample.csv --json-output`.
- Fix every error in source data.
- Review every warning and classify it as accepted, corrected, or escalated.
- Repeat until the batch matches acceptance criteria.
- Add recurring failures to regression tests.

## 6. Add approvals

- Define thresholds for maker-checker review.
- Require independent bank-detail confirmation for new or changed recipients.
- Require documented approval for urgent, high-value, payroll, and refund batches.
- Record `approved_by` or an approval ticket.
- Keep approval evidence outside public logs when it contains personal data.

## 7. Pilot

- Run the helper in parallel with the existing process.
- Compare normalized payloads with portal entries.
- Check rejected bank entries against validation outputs.
- Train operators on warnings and anti-patterns.
- Stop using free-text spreadsheet columns that cause repeated errors.

## 8. Cutover

- Lock the old spreadsheet template.
- Use the new schema for all new payment preparations.
- Keep emergency manual entry documented and reviewed.
- Reconcile bank confirmations daily or per payment cycle.
- Review incident logs after the first payroll and supplier cycles.

## 9. Post-migration controls

- Review warning patterns monthly.
- Update bank-code reference data when confirmed by the bank.
- Keep test scenarios aligned with real rejection cases.
- Verify access to state files and logs.
- Confirm retention periods with accounting, tax, payroll, and privacy requirements.

## Rollback plan

- Keep the previous approved process available for one controlled payment cycle.
- Document why rollback is needed.
- Export current records before rollback.
- Reconcile any payments created during the pilot.
- Fix root causes before attempting cutover again.

## 2026 source-validation additions

- Replace spreadsheet-only bank-code lists with a process that checks the Bank of Israel identification-code register and branch locator before production rollout.
- Record whether a payment threshold is official, bank-specific, or an internal policy threshold.
- Update calendar logic to distinguish Friday or holiday-eve short days from Saturday or holiday closures.
- Keep open-banking/payment-initiation endpoint assumptions out of manual form helpers unless a regulated ASPSP or TPP integration is explicitly in scope.
