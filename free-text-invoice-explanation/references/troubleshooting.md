# Troubleshooting

## VAT amount is zero

Likely causes:

- `business_type` is `exempt_dealer`.
- `exempt_from_vat` is `true`.
- `reverse_charge` is `true`.

Actions:

1. Confirm business classification.
2. Confirm whether the line is actually VAT-exempt.
3. Confirm reverse-charge treatment before sending the explanation.
4. Recalculate after correcting the fields.

## VAT appears on a receipt

A receipt confirms payment received. It should not be described as a tax invoice unless the document is an invoice-receipt.

Actions:

1. Set `document_type` to `invoice_receipt` when the document is both an invoice and a receipt.
2. Keep `document_type` as `receipt` when only payment is documented.
3. Remove tax-invoice wording from the client message.

## Hebrew text sounds unnatural

Likely causes:

- The line description is copied from an internal accounting code.
- English terms are used where Hebrew terms are standard.
- The explanation is too long for a consumer.

Actions:

1. Replace internal abbreviations with client-facing words.
2. Use `חשבונית מס`, `קבלה`, `עוסק פטור`, `עוסק מורשה`, `מע״מ`, and `החזר הוצאה`.
3. Use `detail_level` set to `short` for simple consumer-facing messages.
4. Keep dates in `DD/MM/YYYY` and amounts with `₪`.

## Totals do not match the accounting system

Likely causes:

- The source system rounds at document level instead of line level.
- Unit price includes VAT in the source system.
- Foreign currency conversion differs.
- A discount line is missing.

Actions:

1. Compare every line amount before VAT.
2. Confirm whether `unit_price` includes VAT or excludes VAT.
3. Use the source system exchange rate when currency conversion is needed.
4. Add discounts as explicit lines or use the source document calculation.

## Credit note is explained as a charge

Likely cause:

- `document_type` is not `credit_note`.

Actions:

1. Set `document_type` to `credit_note`.
2. Use a negative amount only if the source system represents credits that way.
3. Add a note explaining the original invoice or reason for the credit.

## Reimbursement causes client questions

Likely causes:

- The explanation does not say the cost was paid for the client.
- Supporting documentation is missing.
- VAT treatment is unclear.

Actions:

1. Set `reimbursable` to `true`.
2. Add a client note.
3. Attach the supplier document or payment proof.
4. Avoid claiming tax treatment unless verified.

## CLI cannot read input

Error:

```text
Provide --input or pipe a JSON payload to standard input.
```

Fix:

```bash
invoice-explain explain --input invoice.json
```

or:

```bash
cat invoice.json | invoice-explain explain
```

## Import fails after extraction

Likely cause:

- The project was not installed in editable mode.

Fix:

```bash
pip install -e .
```

Then verify:

```bash
python - <<'PY'
from free_text_invoice_explanation import InvoiceExplanationClient
print(InvoiceExplanationClient)
PY
```

## Tests fail because async plugin is missing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

The development requirements include `pytest-asyncio`.

## Allocation-number question appears on a high-value B2B invoice

Possible causes:

- The invoice amount before VAT is above the Israel Invoice threshold for the document date.
- The customer wants to deduct input VAT and needs the allocation number.
- The source document does not show whether an allocation number was issued.

Actions:

1. Do not invent an allocation number.
2. Ask for the source invoice or accounting-system export.
3. Tell the customer to verify the allocation number through the official Tax Authority service when relevant.
4. Keep the explanation separate from legal or accounting advice.
