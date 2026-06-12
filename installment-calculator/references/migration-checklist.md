# Migration Checklist

Use this checklist when replacing a spreadsheet, checkout plug-in, CRM formula, or manual quote template.

## Inventory current behavior

- List every location that calculates installments.
- Capture formulas for interest, fees, rounding, VAT, dates, refunds, and cancellation.
- Export at least 30 historical examples across products and payment counts.
- Identify which fields are customer-facing and which are internal.

## Map fields

| Existing field | Target field |
|---|---|
| Immediate price | `cash_price` |
| Deposit | `down_payment` |
| Number of payments | `installments` |
| Annual nominal rate | `annual_interest_rate` |
| Setup fee | `upfront_fee` |
| Setup percentage | `upfront_fee_percent` |
| Monthly handling fee | `per_installment_fee` |
| First charge date | `first_due_date` |
| Preferred debit day | `payment_day` |
| VAT flag | `vat_included` |

## Reconcile calculations

1. Run the old and new calculations side by side.
2. Compare financed amount, regular payment, total interest, total fees, total paid, and final balance.
3. Classify every difference as rounding, fee timing, date clipping, VAT handling, or data-entry error.
4. Obtain accounting approval for the chosen rounding policy.
5. Obtain legal review for consumer-facing disclosure wording.

## Cutover

1. Freeze old formulas.
2. Deploy the package and CLI in a staging environment.
3. Run the scenarios in `references/test-scenarios.md`.
4. Store serialized plan output with every accepted order or quote.
5. Train support staff to read the schedule and refund estimate.
6. Monitor failed payments, chargebacks, refunds, and customer disputes.

## Rollback plan

- Keep the last approved spreadsheet or checkout formula read-only.
- Store all generated schedules during pilot operation.
- Reconcile totals daily during the first billing cycle.
- Roll back only after preserving accepted plan records and customer disclosures.

## Web-validated 2026 migration checkpoints

1. Replace hard-coded 17% VAT with a configurable value and set the reviewed baseline to 18%.
2. Add a pre-VAT invoice-threshold check for B2B workflows that may need an Israel Invoice allocation number.
3. Replace manual cancellation-fee spreadsheets with `statutory_cancellation_fee_cap`, then keep legal eligibility checks outside the arithmetic helper.
4. Add a review gate when old API descriptions mention stale Israel Invoice thresholds.
