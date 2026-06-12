# Migration Checklist

Use this checklist when replacing ad-hoc handling with the structured workflow.

## Applicability

Applies to email folders, WhatsApp messages, paper binders, leasing-company statements, individual employee handling, or unstructured spreadsheets.

## Phase 1: Inventory

- [ ] Collect all open parking, traffic, toll, and collection notices.
- [ ] Export bank and credit-card payment history.
- [ ] Request statements from leasing companies.
- [ ] Export toll-road account statements.
- [ ] Collect employee receipts.
- [ ] Identify all business vehicles.
- [ ] Identify all parking app accounts.
- [ ] Identify who receives notices.

## Phase 2: Data model

- [ ] Create the register fields from `SKILL.md`.
- [ ] Normalize vehicle numbers to digits only.
- [ ] Store dates as ISO internally.
- [ ] Display Hebrew dates as `DD/MM/YYYY`.
- [ ] Store amounts as decimal strings.
- [ ] Use canonical statuses only.

## Phase 3: Privacy cleanup

- [ ] Remove full ID numbers from broad-access spreadsheets.
- [ ] Remove payment-card numbers completely.
- [ ] Restrict notice folders.
- [ ] Define retention period.
- [ ] Store credentials in a password manager.

## Phase 4: Open case triage

For each case: identify issuer, check official source, save proof, reconcile amount, set due date, assign status, assign owner, add next action.

## Phase 5: Accounting alignment

- [ ] Separate parking payment from parking fine.
- [ ] Separate toll principal from enforcement and collection fees.
- [ ] Identify employee reimbursements.
- [ ] Identify leasing admin fees.
- [ ] Confirm material treatment with accountant.
- [ ] Ensure every payment has receipt or confirmation.

## Phase 6: Employee and fleet policy

- [ ] Define driver identification.
- [ ] Define liability transfer process.
- [ ] Define reimbursement process.
- [ ] Define mandatory legal review triggers.
- [ ] Define employee chargeback rules.

## Phase 7: Technical migration

- [ ] Install dependencies.
- [ ] Run `pytest`.
- [ ] Test CLI validation.
- [ ] Use mock transport before live integration.
- [ ] Confirm no scraping or CAPTCHA bypass.
- [ ] Confirm logs redact identifiers.

## Phase 8: Cutover

- [ ] Freeze old spreadsheet.
- [ ] Import active cases.
- [ ] Assign owners.
- [ ] Verify due dates.
- [ ] Run duplicate detection.
- [ ] Reconcile recent payments.
- [ ] Start weekly review.

## Phase 9: Ongoing controls

Weekly review open, overdue, appeal, collection, and duplicate-risk cases. Monthly reconcile receipts and payments. Quarterly review access, thresholds, scenarios, and issuer-channel list.



## Web-validation migration checks

- [ ] Label internal endpoint paths as internal middleware examples.
- [ ] Confirm no public issuer API or webhook is assumed without written documentation.
- [ ] Add a field for source URL and access date for every issuer rule.
- [ ] Add a field for source-specific deadline.
- [ ] Record VAT treatment separately from payment status.
