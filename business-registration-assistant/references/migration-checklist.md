# Migration Checklist: עוסק פטור to עוסק מורשה

## Triggers

Start migration planning when year-to-date turnover approaches the current ceiling, signed contracts make crossing likely, activity changes to an excluded occupation, clients require VAT invoices, large VAT-bearing expenses become material, or rapid growth is expected.

## Calculation

```yaml
year_to_date_turnover_nis: 0
signed_contracts_not_yet_billed_nis: 0
expected_remaining_year_sales_nis: 0
current_osek_patur_ceiling_nis: null
forecast_total_nis: 0
likely_crossing_date: "DD/MM/YYYY"
```

Use gross turnover before expenses.

## Before migration

- Verify current ceiling.
- Identify whether the ceiling was already crossed.
- Contact accountant, tax adviser, or VAT office.
- Confirm effective date for עוסק מורשה.
- Review client contracts and VAT wording.
- Decide whether prices are before VAT or including VAT.
- Update invoice software.
- Prepare VAT reporting calendar.

## Documents

- Current עוסק פטור registration.
- Receipt list and sales ledger.
- Client contracts and quotes.
- Forecast invoices.
- Supplier tax invoices from the relevant period.
- Bank statements for reconciliation.
- VAT office/accountant confirmation.

## Client notice

```text
Starting DD/MM/YYYY, the business will operate as עוסק מורשה. Future taxable invoices will include VAT according to law. Please confirm whether existing prices are before VAT or include VAT.
```

## Software changes

- Switch from receipt-only flow to VAT invoice or invoice-receipt flow.
- Verify VAT rate.
- Add input VAT tracking.
- Keep invoice numbering and audit trail.
- Disable incorrect exempt-dealer templates.

## Anti-patterns

Do not delay receipts, split income artificially, issue exempt-dealer receipts after status changes, issue VAT invoices before status is effective without professional instruction, or deduct input VAT without valid tax invoices.
