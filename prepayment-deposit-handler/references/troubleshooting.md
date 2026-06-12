# Troubleshooting

## Triage sequence

1. Identify the deposit record and receipt number.
2. Confirm supplier status: VAT-registered, VAT-exempt, non-profit/Malkar, or other.
3. Read written refund and cancellation terms.
4. Determine whether goods/services were supplied.
5. Check whether a tax invoice already exists.
6. Compare deposit applied amount to final invoice amount.
7. Reconcile customer card, deposit liability account, bank movement, and VAT report.

## Customer balance is negative

### Symptoms

- Customer card shows credit balance.
- Final invoice is closed but unapplied money remains.
- Customer asks why money is still open.

### Causes

- Deposit exceeded final invoice.
- Deposit applied twice.
- Credit invoice posted without refund.
- Bank receipt imported twice.

### Resolution

1. Locate all receipts and deposit applications.
2. Reverse duplicate applications.
3. If real overpayment exists, refund or document customer-approved credit.
4. Keep refund reference.
5. Add a settlement note to the customer account.

## VAT appears twice

### Symptoms

- VAT was reported when the deposit was received and again when final invoice was issued.
- Customer sees same advance on two tax invoices.
- Revenue and VAT exceed contract value.

### Causes

- Deposit was treated as taxable consideration and final invoice repeated the full amount.
- No link exists between deposit tax invoice and final invoice.
- Tax invoice/receipt was used when only receipt was intended.

### Resolution

1. Compare original tax invoice, receipt, and final invoice.
2. Determine whether the first tax invoice was valid.
3. Issue credit invoice if a prior tax invoice must be corrected.
4. Reissue or amend settlement display according to bookkeeping software rules.
5. Add controls preventing unlinked deposit tax invoices.

## VAT-exempt supplier used tax-invoice wording

### Resolution

1. Stop using the incorrect template.
2. Issue corrected receipt or cancellation/correction document according to system and accountant guidance.
3. Notify the customer that no VAT was charged and no input VAT can be deducted.
4. Review all open documents using the wrong template.

## Refundable deposit was recorded as revenue

### Resolution

1. Reclassify from revenue to deposit liability/customer deposit.
2. Confirm no tax invoice was incorrectly issued.
3. If tax invoice exists, evaluate credit invoice.
4. Store supporting explanation.
5. Add account mapping rule for future refundable deposits.

## Deposit cannot be matched to invoice

### Causes

- Missing contract ID.
- Customer paid using a different name.
- Receipt number not entered in settlement.
- Multiple branches/projects share same customer card.

### Resolution

1. Search by amount, date, payment reference, payer name, and bank reference.
2. Add cross-reference once matched.
3. Split deposits by project/order where needed.
4. Require deposit ID on every final invoice note.

## Retention was treated as received cash

### Resolution

1. Reverse receipt if money was never received, using the bookkeeping system correction process.
2. Reclassify as retention receivable or open customer balance.
3. Issue receipt only when retention is actually released.
4. Attach contract clause and acceptance certificate.

## Customer cancels after non-refundable booking fee

### Checks

- Is the non-refundable term written clearly?
- Does consumer protection law override the term?
- Was a tax invoice issued?
- Was any service already supplied?
- Is a partial refund commercially agreed?

### Resolution paths

- Keep fee: document basis and issue/keep required tax document.
- Partial refund: calculate retained amount, refund balance, issue correction if needed.
- Full refund: issue refund and credit/correction where needed.

## Israel Invoice allocation failed

### Causes

- Incorrect customer tax ID.
- Invoice threshold mismatch.
- Software integration outage.
- Supplier not authorized in the relevant system.
- Data mismatch between invoice lines and request.

### Resolution

1. Validate customer details.
2. Retry through approved software.
3. Use official portal if available.
4. Follow documented fallback process.
5. Store request/response/error evidence.
6. Do not issue a fake allocation number.

## Cash deposit violates policy

### Resolution

1. Check current cash restriction rules.
2. Escalate if amount exceeds permitted ceiling.
3. Prefer bank transfer or card payment.
4. If accepted lawfully, document payer identity and receipt details.
5. Add warning to future quote/payment instructions.

## Old deposits remain open

### Resolution

1. Create an aged deposit report.
2. Contact customers for settlement, refund, or credit confirmation.
3. Review limitation, abandoned balance, and consumer rules with a professional.
4. Clear only with documented basis.
5. Add monthly review owner.

## Preventive controls

- Unique deposit IDs.
- Mandatory contract/order reference.
- Required nature classification.
- Separate accounts for refundable deposits, advances, and retentions.
- Automated warning when deposit exceeds invoice.
- Block duplicate deposit application.
- Month-end open-deposit report.
- Review queue for deposits older than 90 days.



## Issue: hard-coded thresholds became stale

### Resolution

1. Check the transaction date.
2. Load the VAT rate and Israel Invoice threshold from configuration.
3. Compare against current official sources.
4. Recalculate the settlement and document the source used.
5. Keep the old threshold only for transactions inside the old effective period.
