# Workflow Guide

## Workflow 1: Freelancer issuing a simple tax invoice

Use when a freelancer invoices a business client for services.

1. Collect service lines from the work log.
2. Confirm all prices are before VAT.
3. Enter quantity, unit price, and VAT rate per line.
4. Apply line-level commercial discounts where agreed.
5. Aggregate the invoice.
6. Compare the calculated total to the accounting system draft.
7. Save JSON output with the draft invoice record.
8. Issue the invoice through approved accounting software.

Example command:

```bash
python -m multi_line_item_aggregator.cli aggregate invoice.json \
  --invoice-id INV-2026-017 \
  --invoice-date 15/06/2026 \
  --vat-number 515555555
```

## Workflow 2: Small shop checking a supplier invoice

Use when a shop receives a supplier invoice with many items.

1. Export or type the supplier lines into CSV.
2. Preserve supplier SKU and description.
3. Enter unit prices exactly as shown.
4. Add line discounts from the document.
5. Add invoice discount when shown at the bottom of the invoice.
6. Run aggregation.
7. Compare subtotal, VAT, and total.
8. Investigate differences above ₪0.01.
9. Store the result next to the supplier invoice.

CSV format:

```csv
sku,description,quantity,unit_price,vat_rate,discount_type,discount_value
A100,Printer paper,5,22.90,18%,percent,5
B200,Delivery,1,35.00,18%,,
```

## Workflow 3: Consumer checking a repair bill

Use when a consumer wants to verify a bill containing labor, parts, call-out fees, and discounts.

1. Separate labor and parts into lines.
2. Confirm whether the displayed prices are before or after VAT.
3. Convert gross amounts to net if needed.
4. Enter discounts exactly as shown.
5. Run calculation.
6. Compare the total and VAT.
7. Ask the supplier for an explanation when the mismatch is larger than rounding.

Gross-to-net formula when a price includes VAT:

```text
net = gross / (1 + vat_rate)
```

Example: `₪118 ÷ 1.18 = ₪100`.

## Workflow 4: Subscription or metered billing

Use when tiny usage charges create fractional agorot.

1. Keep unit prices with all decimal places.
2. Do not round usage charge lines before aggregation.
3. Use the helper to calculate VAT per line.
4. Review `fractional_agorot_vat_total`.
5. Apply a documented rounding adjustment if the billing policy requires it.
6. Add a regression test for the exact usage pattern.

## Workflow 5: Mixed VAT rates

Use when an invoice contains taxable and zero-rated lines.

1. Assign VAT rate per line.
2. Avoid applying one VAT rate to the whole invoice.
3. Allocate invoice-level discounts only to eligible lines when the document or tax treatment requires it.
4. Calculate VAT per line.
5. Store the reason for zero-rated treatment outside this helper.
6. Review with a professional when the treatment is uncertain.

## Workflow 6: Credit note preparation

Use when a correction or refund must reverse prior invoice lines.

1. Retrieve the original invoice calculation.
2. Enable negative lines only inside a controlled credit workflow.
3. Match original VAT rates and discount basis.
4. Calculate the credit note.
5. Compare reversed totals with the original document.
6. Issue the credit note through approved accounting software.

## Workflow 7: Marketplace payout reconciliation

Use when a seller receives a payout statement with item prices, platform fees, discounts, shipping, and VAT.

1. Treat each sale, fee, shipping charge, and discount as a separate line where possible.
2. Confirm whether platform fees include VAT.
3. Use negative lines only when the statement represents a deduction and the workflow permits it.
4. Separate taxable, zero-rated, and non-tax lines.
5. Track fractional agorot across many small items.
6. Reconcile the calculated total to the payout amount.
7. Keep the original payout statement for audit.

## Workflow 8: Migrating from spreadsheet formulas

1. Export spreadsheet rows to CSV.
2. Map column names to `sku`, `description`, `quantity`, `unit_price`, `vat_rate`, `discount_type`, and `discount_value`.
3. Run the CLI on the CSV.
4. Compare totals for at least 20 historical documents.
5. Document differences caused by spreadsheet rounding.
6. Replace spreadsheet formulas only after regression tests pass.

## Workflow 9: Accounting-system pre-check

1. Calculate the draft invoice using this helper.
2. Send the same line data to the accounting system draft.
3. Compare subtotal, VAT, and grand total.
4. If totals differ, inspect:
   - gross versus net basis,
   - line-level versus invoice-level rounding,
   - allocation of invoice discount,
   - VAT rate per line.
5. Use the accounting system as the system of record for official issuance.

## Workflow 10: Internal approval

1. Sales enters draft lines and discounts.
2. Finance runs the aggregation.
3. Finance reviews residuals and warnings.
4. A manager approves discounts above policy threshold.
5. The approved JSON output is attached to the invoice draft.
6. Official issuance occurs only after approval.

## End-to-end JSON example

Input:

```json
{
  "lines": [
    {
      "sku": "CONSULT",
      "description": "Consulting hours",
      "quantity": "3.5",
      "unit_price": "250",
      "vat_rate": "18%",
      "discount_type": "percent",
      "discount_value": "10"
    },
    {
      "sku": "DELIVERY",
      "description": "Courier",
      "quantity": "1",
      "unit_price": "39.90",
      "vat_rate": "18%"
    }
  ]
}
```

Command:

```bash
python -m multi_line_item_aggregator.cli aggregate invoice.json --json-output
```

Expected checks:

- Subtotal before discounts equals `3.5 × 250 + 39.90`.
- Line discount applies only to consulting.
- VAT is calculated on post-discount amounts.
- Grand total equals the sum of rounded line totals.


## Web-validated 2026 note

Access date: 2026-06-02. For Israel Invoice allocation-number checks, use the updated 2026 thresholds: above ₪10,000 before VAT from 01/01/2026 and above ₪5,000 before VAT from 01/06/2026, when the legal conditions apply. This package does not request allocation numbers.
