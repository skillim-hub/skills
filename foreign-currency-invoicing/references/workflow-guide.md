# Workflow Guide

Use these workflows to move from transaction facts to an audit-ready invoice calculation.

## Workflow 1: Israeli customer, USD price, standard VAT

1. Confirm the customer is an Israeli taxable customer.
2. Confirm the tax event date and issue date.
3. Fetch the Bank of Israel USD representative rate for the issue date.
4. Convert the USD net amount to NIS.
5. Calculate VAT at the standard rate for the issue date.
6. Show the USD commercial total and the NIS VAT amount.
7. Store the rate source and calculation output.

Command:

```bash
foreign-currency-invoicing create \
  --env sandbox \
  --currency USD \
  --issue-date 02/06/2026 \
  --exchange-rate 3.70 \
  --lines-json '[{"description":"Maintenance","quantity":"1","unit_price":"1000","vat_category":"standard"}]'
```

## Workflow 2: Foreign-resident customer, potential zero-rate

1. Collect customer legal name, country, tax number if available, and contract.
2. Confirm the service qualifies for zero-rate and no exception applies.
3. Confirm service use is outside Israel when that fact matters.
4. Add a line note describing retained evidence.
5. Calculate VAT as 0 and preserve the evidence file.
6. Reclassify to standard VAT if evidence is incomplete.

Example line:

```json
{
  "description": "Research advisory services",
  "quantity": "1",
  "unit_price": "1800",
  "vat_category": "zero",
  "note": "Foreign-resident business; contract and use-abroad evidence retained."
}
```

## Workflow 3: Receipt after foreign-currency payment

1. Match the receipt to the original invoice.
2. Record the received amount in the received currency.
3. Convert the receipt amount using the rate required by the bookkeeping process for payment recording.
4. Record exchange-rate differences separately from VAT.
5. Do not change the original invoice VAT calculation merely because the payment rate changed.

## Workflow 4: Credit invoice for a USD invoice

1. Locate the original invoice and its rate evidence.
2. Confirm the credit reason: cancellation, discount, return, or error correction.
3. Use the original line allocation and VAT category.
4. Use the original exchange-rate basis unless professional guidance requires another basis.
5. Issue a credit document through the accounting system rather than editing the original invoice.
6. Link the credit document to the original invoice.

## Workflow 5: JPY invoice with unit 100

1. Read the Bank of Israel unit field.
2. Divide the quoted rate by the unit.
3. Multiply the JPY amount by the effective NIS-per-JPY rate.
4. Calculate VAT on the NIS base for standard lines.
5. Store both the quoted rate and the unit.

Python:

```python
from foreign_currency_invoicing_client import ExchangeRate, calculate_invoice

rate = ExchangeRate("JPY", "2.40", unit="100", date="02/06/2026")
result = calculate_invoice(
    [{"description": "License", "quantity": "100000", "unit_price": "1", "vat_category": "standard"}],
    "JPY",
    "02/06/2026",
    rate,
)
```

## Workflow 6: Weekend or holiday issue date

1. Try to fetch the representative rate for the issue date.
2. If unavailable, search backwards for the most recent published rate.
3. Document the issue date, selected rate date, and reason.
4. Do not use a future rate.
5. Include the selected rate date in the invoice support file.

## Workflow 7: Batch processing from JSON

1. Prepare a JSON array of invoice jobs.
2. Validate every job has currency, issue date, exchange rate, and lines.
3. Run `scripts/examples/05_batch_from_json.py` with `--env sandbox` first.
4. Review warnings for zero-rate, exemption, reverse-charge, and outside-scope lines.
5. Save accepted outputs into the accounting import folder.

## Approval gates

- Gate 1: Currency and rate date verified.
- Gate 2: VAT category selected and evidence retained.
- Gate 3: NIS VAT and total reconcile to accounting system totals.
- Gate 4: Document number issued by approved accounting system.
- Gate 5: JSON, PDF, and evidence archived.
