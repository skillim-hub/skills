# Workflow Guide

Follow these workflows as operational checklists. Replace sample values with the business records, customer data, and official system responses.

## Workflow 1: B2B tax invoice with allocation check

1. Collect issuer name, tax id, status, customer legal name, customer tax id, and customer type.
2. Enter line descriptions, quantities, unit prices, discounts, and date as `DD/MM/YYYY`.
3. Run validation.
4. Confirm the amount before VAT exceeds or does not exceed the active threshold.
5. If allocation is required, create the allocation payload and submit it through the official integration.
6. Store the returned allocation number with the invoice record.
7. Render the Hebrew review copy.
8. Issue the official document through the production system.

```bash
invoice-generator example --kind tax-invoice > b2b.json
invoice-generator validate b2b.json --env sandbox
invoice-generator allocation-required b2b.json --env sandbox
invoice-generator shaam-payload b2b.json --env sandbox --output b2b-allocation.json
```

## Workflow 2: Receipt for osek patur

1. Set `issuer.status` to `patur`.
2. Set `document_type` to `receipt`.
3. Add payment details for cash, transfer, credit card, cheque, payment app, or another method.
4. Validate that VAT is zero.
5. Render the Hebrew draft and issue the official receipt in the accounting system.

## Workflow 3: Tax invoice receipt for immediate payment

1. Set `document_type` to `tax_invoice_receipt`.
2. Add taxable lines and payment details.
3. Validate the document.
4. Check whether allocation is required based on customer type and amount before VAT.
5. Store allocation number before final issuance when required.
6. Reconcile the payment record with bank or card data.

## Workflow 4: Credit note against prior invoice

1. Set `document_type` to `credit_note`.
2. Enter the new credit-note number.
3. Add `original_document_number` and `original_allocation_number` when the original invoice had an allocation number.
4. Add `credit_reason` in plain Hebrew.
5. Enter positive line amounts; the helper applies the negative sign.
6. Render and review the negative totals.
7. Issue the official credit note and link it to the original transaction.

## Workflow 5: Foreign customer zero-rate invoice

1. Confirm eligibility for zero-rate VAT before drafting.
2. Set `currency` to the foreign currency code.
3. Set `vat_rate` to `0`.
4. Add `zero_rate_basis` and a clear exchange-rate note.
5. Keep export, residency, and service evidence in the transaction file.
6. Validate and render before issuing officially.

## Workflow 6: Migrating from manual or spreadsheet process

1. Freeze the current document-number sequence.
2. Export open customers, products, services, and prior document references.
3. Convert one recent invoice, receipt, and credit note into JSON examples.
4. Run the test suite.
5. Compare totals against historical documents.
6. Move sandbox tests to production only after reconciliation succeeds.

## Web-validated 2026 threshold note

For documents dated from 01/01/2026 through 31/05/2026, compare the amount before VAT to ₪10,000.00. For documents dated 01/06/2026 or later, compare the amount before VAT to ₪5,000.00. Treat the rule as greater than the threshold, not equal to the threshold.
