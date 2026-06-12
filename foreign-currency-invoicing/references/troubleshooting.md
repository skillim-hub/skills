# Troubleshooting

## Rate lookup failures

### Symptom

The Bank of Israel lookup fails or returns no currency.

### Checks

1. Confirm the currency code is a three-letter code.
2. Confirm the requested date is not a weekend, Israeli holiday, or future date.
3. Confirm the endpoint returned CSV, JSON, or XML rather than an HTML error page.
4. Confirm the currency is published by the Bank of Israel.

### Fix

Search backward for the most recent published representative rate and save the selected rate date. Prefer the SDMX series endpoint for date-specific lookup. Retry later if the public endpoint is temporarily unavailable. Do not invent a rate.

## VAT amount is wrong

### Common causes

- Rate unit ignored, especially for JPY.
- VAT applied to foreign total and then converted again.
- A zero-rated line was treated as standard.
- Rounding occurred per line in one system and per document in another.

### Fix

Recalculate from the NIS taxable base. Confirm whether rounding is per line or per document. Keep one rounding policy across the accounting workflow.

## Zero-rate warning appears

The client warns when zero-rate, exempt, reverse-charge, or outside-scope lines have no note. Add a concise evidence note. Example:

```json
{
  "vat_category": "zero",
  "note": "Foreign-resident customer; contract and use-abroad evidence retained."
}
```

## CLI cannot show a created invoice

### Causes

- `FCI_INVOICE_DIR` changed between `create` and `show`.
- `--env` changed between `create` and `show`.
- The invoice was created with `--no-save`.

### Fix

Use the same `--env` value and the same storage directory. Keep `--save` enabled when a later `show` step is required.

## Import fails after extraction

Run installation from the package root:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Then test:

```bash
python -c "from foreign_currency_invoicing_client import calculate_invoice; print(calculate_invoice)"
```

## Hebrew document output looks inconsistent

Use DD/MM/YYYY for Israeli-facing dates and ₪ for shekel amounts. Keep JSON decimals with a dot to avoid parsing errors.

## Accounting-system import rejects the document

Check these fields:

- Document type matches the accounting-system import schema.
- Customer identifier is present when required.
- Currency code is valid.
- NIS VAT amount is present.
- Date is in the format expected by the import file.
- Number formatting uses plain decimal digits, not localized thousands separators.

## Manual rate override was used

Manual rate entry is acceptable only when supported by a documented source and internal approval. Save the source and reason. Prefer Bank of Israel representative rates whenever they are available.

## Production incident checklist

1. Stop issuing affected invoices.
2. Identify all documents using the wrong rate or VAT category.
3. Export affected JSON outputs and PDFs.
4. Ask the accountant whether cancellation, credit invoice, or corrected document is required.
5. Record the corrective action and retain supporting files.
