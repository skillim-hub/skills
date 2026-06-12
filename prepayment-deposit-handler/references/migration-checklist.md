# Migration Checklist

Use this checklist when moving from spreadsheets, manual receipts, or an older bookkeeping workflow into a structured deposit-handling process.

## 1. Inventory current records

- Export all open customer balances.
- Export all receipts that are not linked to final invoices.
- Export all open orders, quotes, and projects.
- Export unapplied credits and overpayments.
- Export refunds issued in the last 24 months.
- Export tax invoices that include advance/deposit wording.

## 2. Normalize terminology

| Old label | New category |
|---|---|
| מקדמה | `advance_for_taxable_supply` unless refundable terms prove otherwise |
| פיקדון | `security_deposit_held_in_trust` if refundable |
| דמי הרשמה | `non_refundable_booking_fee` or `refundable_booking_deposit` by terms |
| יתרת זכות | `gift_card_or_credit_balance` or overpayment |
| עיכבון | `retention_held_by_customer` |
| תשלום ראשון | Usually `advance_for_taxable_supply` |

## 3. Add required fields

Every migrated deposit should have:

- Deposit ID.
- Customer name.
- Customer tax ID where available.
- Contract/order/reference ID.
- Receipt number.
- Receipt date in DD/MM/YYYY or ISO format.
- Original amount.
- Applied amount.
- Remaining amount.
- Refundable flag.
- Deposit nature.
- Payment reference.
- Linked final invoice number, if settled.
- Notes explaining migration assumptions.

## 4. Reconcile accounting balances

- Total migrated refundable security deposits equals the deposit liability account.
- Total customer advances equals customer advance or unapplied receipt balance.
- Retentions withheld by customers are not included in cash deposits.
- VAT report agrees to tax invoices, not receipt-only deposits.
- Overpayments are separated from ordinary deposits.

## 5. Handle unclear records

| Status | Meaning | Action |
|---|---|---|
| `ready` | Record has all required fields | Import |
| `needs_customer_reference` | Missing order/project link | Search or contact owner |
| `needs_tax_review` | Tax invoice or VAT treatment unclear | Send to accountant |
| `needs_refund_decision` | Overpayment or stale credit | Contact customer |
| `do_not_import` | Duplicate or cancelled item | Keep audit note only |

## 6. Validate document numbering

- Do not renumber legal receipts or invoices.
- Preserve original document number and source system.
- Store migrated deposit ID separately from official receipt/invoice number.
- Keep source exports read-only.

## 7. Import sequence

1. Import customers.
2. Import open orders/projects.
3. Import receipts and deposit records.
4. Import tax invoices and credit invoices.
5. Apply deposits to final invoices.
6. Import refunds and credit balances.
7. Run reconciliation reports.
8. Freeze old workflow.

## 8. Acceptance checks

- No deposit has negative remaining balance.
- No deposit is applied to more than one invoice unless explicitly split.
- No receipt-only refundable security deposit appears as revenue.
- Every overpayment has refund or credit decision.
- Every tax invoice correction has linked original invoice.
- Every open deposit older than 90 days appears in review report.
- Hebrew customer statements display ₪ and DD/MM/YYYY correctly.

## 9. Staff rollout

- Train staff on the classification decision tree.
- Disable ambiguous document templates.
- Require deposit nature on every new receipt.
- Require order reference before final settlement.
- Review first 20 migrated settlements manually.
- Schedule month-end open-deposit review.

## 10. Rollback plan

- Preserve original exports.
- Keep import mapping file.
- Keep hash or checksum of source files.
- Document all manual adjustments.
- Reopen old workflow only for correction, not for new deposits.
