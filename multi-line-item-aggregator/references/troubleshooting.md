# Troubleshooting

## Fast diagnosis table

| Symptom | Likely cause | Fix |
|---|---|---|
| Total differs by ₪0.01 | Rounding stage mismatch | Compare line-level and document-level rounding. |
| Total differs by several agorot | Many tiny lines accumulated residuals | Review fractional agorot fields. |
| VAT differs by exactly VAT on discount | Discount applied after VAT | Apply discount before VAT unless documented otherwise. |
| VAT too high | Gross prices were entered as net | Convert gross to net. |
| VAT too low | Zero rate used on taxable line | Check VAT rate per line. |
| Line total negative | Discount exceeds line or negative quantity | Use credit-note workflow or correct input. |
| Invoice discount distribution looks wrong | Wrong allocation method | Choose `by_net`, `by_gross`, or `equal` based on the document. |
| CSV import fails | Header names differ | Rename columns to supported names. |
| Hebrew descriptions appear garbled | Wrong file encoding | Save CSV as UTF-8 or UTF-8-SIG. |
| JSON output has strings for amounts | Decimal-safe serialization | Treat money strings as fixed-point values. |

## Step-by-step investigation

### 1. Confirm net versus gross

Ask whether the source line prices include VAT. If yes, convert to net before using the helper.

Formula:

```text
net = gross / (1 + vat_rate)
```

For 18% VAT:

```text
₪118.00 / 1.18 = ₪100.00
```

### 2. Confirm discount timing

Most commercial discounts reduce the taxable base before VAT. If a source document shows a discount after VAT, document the reason and do not silently normalize it.

### 3. Confirm discount scope

An invoice-level discount can apply to:

- all lines,
- taxable lines only,
- a specific department or item group,
- a manual commercial basis.

Use the same scope as the source document.

### 4. Confirm rounding stage

Common methods:

| Method | Description |
|---|---|
| Line VAT rounding | Round VAT on each line and sum rounded VAT. |
| Document VAT rounding | Sum exact VAT and round once. |
| Line total rounding | Round each line total and sum. |
| Final total rounding | Sum exact totals and round once. |

The helper defaults to line-level VAT rounding and line total rounding for auditability.

### 5. Inspect fractional agorot

Look at:

- `fractional_agorot_vat`
- `fractional_agorot_total`
- `fractional_agorot_vat_total`
- `fractional_agorot_grand_total`
- `rounding_adjustment`

A tiny residual is not necessarily an error. A large residual requires a documented adjustment.

## Common error messages

### `Invalid numeric value`

Cause: amount contains unsupported text or a blank field.

Fix: use values such as `100`, `100.50`, `₪100.50`, `18%`.

### `VAT rate cannot be negative`

Cause: input such as `-18%`.

Fix: use a non-negative VAT rate. Use credit lines for refunds, not negative VAT rates.

### `Percent discount cannot exceed 100`

Cause: discount percentage above 100.

Fix: use a credit note or fixed adjustment if the source document is a refund.

### `Fixed discount cannot exceed line amount`

Cause: line discount is larger than `quantity × unit_price`.

Fix: check the unit price, quantity, gross/net basis, or document type.

### `Invoice discount cannot exceed allocation basis`

Cause: invoice-level discount is larger than eligible line amounts.

Fix: verify whether discount was entered in gross terms or whether only selected lines are eligible.

### `zero quantity`

Cause: a line with quantity `0`.

Fix: remove informational lines or explicitly allow zero-quantity lines in a controlled workflow.

### `negative quantity`

Cause: a line has a negative quantity without override.

Fix: switch to a credit-note workflow or correct the sign.

## CSV import checklist

- Use UTF-8 or UTF-8-SIG encoding.
- Include a header row.
- Use exact supported column names.
- Avoid thousands separators when exporting from spreadsheets, or verify parsing.
- Keep percentages as `18%` or `18`.
- Keep empty discount fields blank.

Supported columns:

```csv
sku,description,quantity,unit_price,vat_rate,discount_type,discount_value,discount_reason
```

## JSON import checklist

- Use a top-level array or an object with `lines`.
- Use strings for money to preserve exact decimal values.
- Do not use comments in JSON.
- Keep date fields as strings in DD/MM/YYYY when used in Israeli workflows.

## When to escalate

Escalate to a bookkeeper, accountant, tax adviser, or the official software provider when:

- VAT treatment is uncertain.
- The source document combines exempt, zero-rated, and taxable items.
- The invoice is subject to official digital invoice reporting.
- The discrepancy is material.
- The document is a credit note or correction for a prior tax invoice.
- The invoice affects a tax filing already submitted.

## Minimal reproducible example

Create `debug-invoice.json`:

```json
{
  "lines": [
    {
      "sku": "DEBUG",
      "description": "Debug line",
      "quantity": "1",
      "unit_price": "100",
      "vat_rate": "18%"
    }
  ]
}
```

Run:

```bash
python -m multi_line_item_aggregator.cli aggregate debug-invoice.json --json-output
```

Expected total:

```text
₪118.00
```

If this fails, check Python version and dependencies before investigating business data.


## Web-validated 2026 note

Access date: 2026-06-02. For Israel Invoice allocation-number checks, use the updated 2026 thresholds: above ₪10,000 before VAT from 01/01/2026 and above ₪5,000 before VAT from 01/06/2026, when the legal conditions apply. This package does not request allocation numbers.
