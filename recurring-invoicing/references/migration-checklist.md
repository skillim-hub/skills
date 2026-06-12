# Migration Checklist

Use this checklist when moving from spreadsheets, manual invoices, legacy billing software, or payment-provider-only records.

## 1. Prepare

- Assign an owner for billing, accounting review, and technical import.
- Freeze the source data at a clear cutoff date.
- Export customers, subscriptions, invoices, payments, credit notes, and open balances.
- Keep original exports unchanged.

## 2. Map fields

| Source field | Target field | Notes |
|---|---|---|
| Customer name | `customer.name` | Use legal name when available |
| VAT or company number | `customer.tax_id` | Normalize to nine digits |
| Email | `customer.email` | Validate delivery address |
| Product description | `line_items.description` | Use customer-visible wording |
| Price before VAT | `line_items.unit_price` | Store as Decimal-compatible string |
| Quantity | `line_items.quantity` | Default to `1` only after review |
| Billing date | `start_date` | Convert to ISO in code and `DD/MM/YYYY` in reports |
| Frequency | `interval` | Map monthly, bimonthly, quarterly, yearly |
| Status | `status` | active, paused, cancelled |
| Last invoice number | sequence counter | Preserve to avoid duplicates |

## 3. Clean data

- Remove duplicate customers.
- Fix missing leading zeros in tax IDs.
- Validate checksum for business customers.
- Normalize dates.
- Separate taxable and VAT-exempt lines.
- Identify cancelled subscriptions with future dates.
- Identify payments without invoices.
- Identify invoices without payments.

## 4. Import

1. Import customers.
2. Import active subscriptions.
3. Import paused subscriptions with reasons.
4. Import cancelled subscriptions for reference only when needed.
5. Import sequence counters.
6. Store historical invoices as read-only records.
7. Do not regenerate historical invoices unless an accountant instructs it.

## 5. Validate

- Compare next issue date against legacy schedule.
- Compare subtotal, VAT, and total for a sample.
- Test allocation requirement for high-value invoices.
- Reconcile open balances.
- Run the test matrix.
- Run one full parallel billing cycle.

## 6. Cut over

- Stop edits in the old system.
- Export final delta.
- Import final delta.
- Run production validation.
- Issue the first live cycle.
- Reconcile immediately after issue.

## 7. Rollback plan

- Keep source exports and old system access.
- Store every generated invoice candidate.
- Define a cutoff point after which rollback requires accounting review.
- Avoid deleting records in either system.
- Use correction documents for accounting changes.

## 8. 2026 allocation threshold correction

- Search legacy rules for a full-year ₪15,000 threshold in 2026.
- Replace it with effective-date rules: ₪10,000 from 01/01/2026 and ₪5,000 from 01/06/2026.
- Recalculate only unissued invoice candidates.
- Do not alter issued historical invoices without accounting approval.
- Add regression tests for 31/05/2026 and 01/06/2026.
- Document the source and access date used for the change.
