# Migration Checklist

Use this checklist when moving calculations from spreadsheets, manual templates, legacy scripts, marketplace exports, or accounting-system previews into this package.

## 1. Inventory existing calculation sources

- List every spreadsheet, script, template, and accounting export that calculates totals.
- Identify who owns each source.
- Record which documents each source supports.
- Capture sample files with known correct totals.
- Mark sources that use gross prices and sources that use net prices.

## 2. Map fields

| Legacy field | New field | Notes |
|---|---|---|
| Item code | `sku` | Optional but useful for reconciliation. |
| Item details | `description` | Preserve source wording. |
| Units | `quantity` | Convert commas to decimal points if needed. |
| Price | `unit_price` | Ensure net basis. |
| VAT | `vat_rate` | Store per line. |
| Discount | `discount_value` | Pair with `discount_type`. |
| Discount kind | `discount_type` | Use `amount` or `percent`. |
| Invoice discount | `invoice_discount` | Store separately from line discounts. |

## 3. Normalize money and percentages

- Remove currency symbols only after preserving original input.
- Convert `18` and `18%` to `0.18`.
- Keep values as decimal strings.
- Avoid binary floating-point transformations.
- Preserve more than two decimals for metered billing.

## 4. Decide rounding policy

Document:

- VAT rounding stage.
- Total rounding stage.
- Invoice-level discount allocation method.
- Treatment of fractional agorot.
- Warning threshold for residual accumulation.

## 5. Migrate discount logic

- Identify whether legacy discounts were applied before or after VAT.
- Identify whether invoice discounts applied to all lines or selected lines.
- Recreate the same logic in test scenarios.
- Change the logic only after approval and documentation.

## 6. Build regression set

Include at least:

- 5 simple invoices.
- 5 discounted invoices.
- 3 mixed VAT invoices.
- 3 fractional-agorot invoices.
- 2 refunds or credit-note examples.
- 2 Hebrew CSV examples.
- 1 large invoice with 100+ lines.

## 7. Run parallel calculation

For each historical document:

1. Export legacy input.
2. Convert to the new schema.
3. Run the helper.
4. Compare subtotal, VAT, and total.
5. Classify differences:
   - expected rounding difference,
   - gross/net mismatch,
   - discount timing mismatch,
   - VAT-rate mismatch,
   - data-entry error.

## 8. Update operational process

- Replace spreadsheet formulas with CLI or library calls.
- Store JSON results with draft invoices.
- Train staff to distinguish net and gross prices.
- Add a checklist item for current VAT rate verification.
- Define escalation for material differences.

## 9. Cutover controls

Before cutover:

- All regression tests pass.
- Business owner approves known differences.
- Accounting owner approves rounding policy.
- Rollback plan exists.
- Official invoice software remains the system of record.

After cutover:

- Review first 20 production invoices.
- Track rounding adjustments.
- Log validation failures.
- Update test scenarios for every discovered edge case.

## 10. Rollback plan

Keep the old calculation source available for a defined period. Roll back only when:

- A production defect affects totals.
- Official software rejects output.
- VAT treatment is uncertain.
- Required audit fields are missing.

Document every rollback with invoice ID, date, cause, correction, and approver.

## Spreadsheet migration tips

- Export as CSV UTF-8.
- Replace localized decimal comma before import when necessary.
- Remove hidden subtotal rows.
- Remove blank lines.
- Do not import formulas as text.
- Use one row per taxable line.
- Keep discount rows separate unless they clearly apply to a specific line.

## Accounting-system migration tips

- Compare against draft invoices, not issued documents when possible.
- Do not overwrite official records from this helper.
- Store external accounting document IDs in metadata.
- Keep allocation-number or official reporting statuses outside this helper.


## Web-validated 2026 note

Access date: 2026-06-02. For Israel Invoice allocation-number checks, use the updated 2026 thresholds: above ₪10,000 before VAT from 01/01/2026 and above ₪5,000 before VAT from 01/06/2026, when the legal conditions apply. This package does not request allocation numbers.
