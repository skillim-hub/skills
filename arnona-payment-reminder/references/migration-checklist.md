# Migration Checklist

## Purpose

Migrate from a rate calculator, discount optimizer, spreadsheet tracker, or manual reminder list to a payment-reminder workflow focused on current bills, safe payment, receipts, and auditability.

## Migration Principles

- Use the official bill as the source of truth for payment amount and due date.
- Keep rate/order analysis separate from payment reminders.
- Preserve historical calculations as reference only.
- Do not import non-neutral presentation or distribution fields.
- Remove any field that implies legal or tax certainty without source documents.
- Add receipt tracking before enabling reminder cancellation.

## Field Mapping

| Old field | New field | Action |
|---|---|---|
| city | municipality | Normalize to official authority name. |
| zone | optional analysis metadata | Do not use for payment instructions unless current bill confirms classification. |
| usage_type | optional analysis metadata | Keep for review, not for pay-now decisions. |
| annual_rate | optional rate reference | Do not use to override bill amount. |
| discount_type | discount_status / note | Track pending, approved, denied, or unknown. |
| calculated_amount | amount_nis | Replace with official bill amount. |
| bimonthly_estimate | amount_nis | Replace with official voucher amount. |
| appeal_text | objection_note | Keep as context; add payment deadline warning. |
| due_date_text | due_date | Convert to date object. |
| paid_flag | status + receipt | Require receipt or confirmation number. |
| receipt_file | receipt_file | Preserve path and metadata. |

## Step-by-Step Migration

1. Export existing records.
2. Remove duplicate properties and obsolete municipalities.
3. Create a bill record for every open unpaid voucher.
4. Convert dates to ISO `YYYY-MM-DD`.
5. Convert amounts to decimal strings with two digits.
6. Add municipality, account reference, bill number, property address, period, issue date, due date, and amount.
7. Mark records without bill numbers as `needs_review`.
8. Mark records with calculated but unbilled amounts as `estimate_only`.
9. Import paid records only when a receipt or confirmation exists.
10. Create reminder plans for unpaid records.
11. Cancel reminders for replaced or duplicate bills.
12. Add receipt storage and naming conventions.
13. Add privacy masking for payer IDs and account references.
14. Run test scenarios before production use.
15. Perform a reconciliation cycle after the first paid period.

## Data Cleanup Rules

- If two records share municipality, account, property, period, and amount, check whether one is a duplicate.
- If two records share property and period but have different voucher numbers, check for replacement.
- If a record has no period, request the original bill.
- If a record is overdue, request current balance before payment.
- If a record is under objection, add an objection-status reminder.
- If a standing order exists, replace payment reminders with debit-verification reminders.

## Migration Risks

| Risk | Mitigation |
|---|---|
| Calculated amount differs from official bill | Use official bill for payment. Keep calculation as review note. |
| Old reminders trigger after payment | Require receipt status and cancel future events. |
| Voucher was replaced | Link records and cancel old reminder plan. |
| OCR converted Hebrew numerals incorrectly | Manual verification for all numeric fields. |
| Business expense classification imported as fact | Mark accountant review required. |
| Personal identifiers copied to logs | Mask or hash identifiers. |

## Rollback Plan

1. Keep original export read-only.
2. Store migrated records in a separate namespace.
3. Disable automated notifications during validation.
4. Compare migrated due dates and amounts against source bills.
5. Activate reminders only after spot-checking a sample from every municipality.
6. Keep manual payment process available for the first billing cycle.

## Completion Checklist

- All open bills have municipality, account reference, bill number, due date, amount, and property address.
- Every paid bill has a receipt or confirmation number.
- Every overdue bill has a current-balance check task.
- Every standing-order bill has a debit-verification task.
- Every discount/objection bill has a status-check task.
- Duplicate and replaced bills are marked.
- Future reminders do not exist for paid bills.
- Accounting handoff fields are present for business bills.
- Privacy controls mask sensitive identifiers outside the payment workflow.


## Version 2.2.0 source-verification step

When migrating existing reminders, add source metadata for the municipal bill, payment page, current-balance check, and receipt. Do not migrate any calculated VAT adjustment into Arnona payment amounts.
