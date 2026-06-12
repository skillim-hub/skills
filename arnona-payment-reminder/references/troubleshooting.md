# Troubleshooting Guide

## Payment Page Rejects the Bill

### Symptoms

- "Voucher not found"
- "Invalid payer number"
- "This bill cannot be paid online"
- Blank page after entering details

### Checks

1. Re-enter all numbers manually from the bill.
2. Verify that the selected payment type is Arnona or municipal taxes.
3. Confirm that the bill belongs to the selected municipality.
4. Check whether the bill was replaced by a newer voucher.
5. Try the official municipality homepage rather than a saved old link.
6. Contact the municipal collection department when rejection persists.

### Do Not

- Do not use a search advertisement as a substitute for the official payment page.
- Do not change digits to make the form accept the bill.
- Do not pay a different account number because the amount looks similar.

## Amount in Payment Page Differs From Bill

### Likely Causes

- Interest or linkage after the due date.
- Discount or credit applied after the bill was printed.
- Partial payment or standing-order debit.
- Corrected bill issued by the municipality.
- Collection costs added after enforcement.
- Wrong period selected.

### Resolution

1. Capture the bill amount and the payment-page amount.
2. Check due date and current date.
3. Request current balance if overdue.
4. Confirm property and period.
5. Pay only after the difference is understood or approved.

## Duplicate Reminder or Duplicate Bill

### Deduplication Key

Use:

```text
municipality + account_reference + property_address + period_start + period_end + bill_number
```

If a newer bill replaces an older bill, link them and cancel the older reminder schedule.

## No Receipt After Payment

### Action

1. Check whether the payment page displayed a confirmation number.
2. Check email and SMS messages from the municipality or payment provider.
3. Check bank or credit-card authorization.
4. Enter the municipal personal area and look for receipts.
5. Contact the municipality with payer number, voucher number, date, amount, and authorization.
6. Keep the bill status as pending until a receipt or official confirmation exists.

## Standing Order Creates Confusion

### Correct Handling

- Treat standing order as an automatic payment route.
- Replace pay-now reminders with verification reminders.
- Verify debit date, amount, and receipt.
- Do not pay manually unless the municipality confirms the debit failed.

## Discount Request Pending

### Correct Handling

- Add a status-check reminder before the due date.
- Ask the municipality whether to pay pending the decision.
- Keep evidence of the discount request.
- If payment is made, mark it as subject to possible credit or refund.

## Bill Is Overdue

### Correct Handling

- Do not pay the old amount automatically.
- Request updated balance.
- Check interest, linkage, collection costs, and enforcement state.
- Ask about payment arrangements if the amount is high.
- Save proof of updated balance and receipt.

## Wrong Property Address

### Correct Handling

- Stop payment.
- Compare property address, asset number, payer number, and period.
- Check whether the user moved, sold the property, changed tenant, or received another person's bill.
- Contact the municipality for correction.

## OCR Extracted Wrong Numbers

### High-Risk Fields

- מספר משלם
- מספר שובר
- מספר נכס
- מספר זהות
- סכום
- מועד לתשלום

### Resolution

Require manual verification for all numeric fields before generating payment instructions.

## Hebrew Date Ambiguity

Use `DD/MM/YYYY` in Hebrew messages and ISO `YYYY-MM-DD` in JSON. Reject ambiguous formats like `03/04/26` unless the source clearly states the year and locale.

## Business Bookkeeping Rejection

### Missing Items

- Receipt
- Confirmation number
- Municipality name
- Property address
- Billing period
- Amount paid
- Payment date
- Business purpose or branch label

### Resolution

Create a receipt evidence pack and ask the accountant to classify deductibility.

## Privacy Incident

### Examples

- Full ID number sent to the wrong recipient.
- Bill uploaded to an open folder.
- Payment link forwarded to an unauthorized tenant or employee.
- Receipt screenshot includes unrelated personal data.

### Response

1. Stop further sharing.
2. Remove or restrict the exposed file.
3. Notify the responsible owner.
4. Replace public logs with masked values.
5. Review access permissions.
6. Keep an incident note.

## CLI Troubleshooting

### `Invalid date`

Use `YYYY-MM-DD` for JSON and `DD/MM/YYYY` for Hebrew-facing text.

### `amount_nis must be positive`

Check OCR output and decimal separator.

### No future events

The bill may be paid, the due date may have passed, or `--include-past` may be needed for audit exports.

### Hebrew output appears garbled

Use a UTF-8 terminal and redirect output to a UTF-8 file if needed:

```bash
python scripts/arnona-payment-reminder-cli.py plan bill.json --language he > plan.json
```


## Business user asks whether to add VAT

Do not add VAT to the Arnona amount. Use the official municipal bill or current-balance result for payment. Store the receipt and let the accountant decide how the payment is recorded.

## Official source changed after import

If a municipal payment page, order, or current-balance source changes after import, mark the bill `needs_review`, store the new source URL and access date, and regenerate the reminder plan only after the property, period, account reference, voucher number, and amount are confirmed.
