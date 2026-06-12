# Test Scenarios

Use these scenarios for regression tests, spreadsheet migration checks, accounting-system comparison, and user acceptance testing.

| # | Scenario | Input summary | Expected check |
|---:|---|---|---|
| 1 | Single taxable line | 1 × ₪100, VAT 18% | Total ₪118.00 |
| 2 | Decimal quantity | 1.5 × ₪80, VAT 18% | Taxable ₪120.00 |
| 3 | Line percent discount | 1 × ₪100, 10% discount | Taxable ₪90.00 |
| 4 | Line amount discount | 1 × ₪100, ₪15 discount | Taxable ₪85.00 |
| 5 | Two taxable lines | ₪100 + ₪50 | VAT ₪27.00 at 18% |
| 6 | Invoice percent discount | ₪100, 10% invoice discount | Taxable ₪90.00 |
| 7 | Invoice amount discount | ₪100 + ₪50, ₪15 discount | Discount shares sum to ₪15.00 |
| 8 | Equal allocation | Two lines, ₪20 invoice discount | ₪10.00 per line |
| 9 | Mixed VAT | ₪100 taxable + ₪100 zero-rated | VAT ₪18.00 |
| 10 | Zero VAT only | ₪100 at 0% | Total ₪100.00 |
| 11 | Fractional agorot | ₪0.05 at 18% | VAT rounds to ₪0.01 |
| 12 | Many micro lines | 100 lines of ₪0.05 | Residual fields are non-zero |
| 13 | Unit price with four decimals | 10 × ₪0.0475 | Do not round before VAT |
| 14 | Discount equals line | ₪100 with ₪100 discount | Total ₪0.00 |
| 15 | Discount exceeds line | ₪100 with ₪101 discount | Reject |
| 16 | Percent discount 100% | ₪100 with 100% discount | Total ₪0.00 |
| 17 | Percent discount 101% | ₪100 with 101% discount | Reject |
| 18 | Empty invoice | No lines | Reject |
| 19 | Zero quantity | Quantity 0 | Reject by default |
| 20 | Zero quantity allowed | Quantity 0 with override | Total ₪0.00 |
| 21 | Negative quantity | Quantity -1 | Reject by default |
| 22 | Credit workflow | Quantity -1 with override | Negative subtotal allowed |
| 23 | Invalid VAT | VAT `abc` | Reject |
| 24 | Negative VAT | VAT `-18%` | Reject |
| 25 | CSV UTF-8 Hebrew | Hebrew descriptions in CSV | Load without mojibake |
| 26 | JSON object input | Top-level object with `lines` | Load correctly |
| 27 | JSON list input | Top-level array | Load correctly |
| 28 | Gross entered as net | Enter ₪118 as net at 18% | Detect mismatch against expected supplier total |
| 29 | Rounding threshold warning | Many tiny lines | Warning when residual exceeds threshold |
| 30 | Allocation by net | Lines ₪900 and ₪300, discount ₪120 | Shares ₪90 and ₪30 |

## Detailed scenario definitions

### Scenario 1: Single taxable line

```json
{
  "lines": [
    {"sku": "A", "description": "Item", "quantity": "1", "unit_price": "100", "vat_rate": "18%"}
  ]
}
```

Expected:

- taxable total `100.00`
- VAT total `18.00`
- grand total `118.00`

### Scenario 7: Invoice amount discount allocation

```json
{
  "invoice_discount": {"type": "amount", "value": "15"},
  "lines": [
    {"sku": "A", "description": "A", "quantity": "1", "unit_price": "100", "vat_rate": "18%"},
    {"sku": "B", "description": "B", "quantity": "1", "unit_price": "50", "vat_rate": "18%"}
  ]
}
```

Expected:

- discount shares sum to `15.00`
- taxable total equals `135.00`

### Scenario 11: Fractional agorot

```json
{
  "lines": [
    {"sku": "MICRO", "description": "Usage", "quantity": "1", "unit_price": "0.05", "vat_rate": "18%"}
  ]
}
```

Expected:

- exact VAT `0.0090`
- rounded VAT `0.01`
- fractional VAT residual `-0.0010`

### Scenario 25: Hebrew CSV

```csv
sku,description,quantity,unit_price,vat_rate
A,שעת ייעוץ,2,250,18%
```

Expected:

- description remains readable
- taxable total `500.00`
- VAT total `90.00`

## Acceptance criteria

A production implementation passes acceptance when:

- At least 20 scenarios above have automated tests.
- All test data uses decimal-safe values.
- Rounding behavior is documented.
- Mixed VAT and discount allocation scenarios are included.
- Hebrew CSV import is verified with UTF-8.
- A failed validation produces a clear error message.
- Historical invoices can be recalculated with the same version.


## Web-validated 2026 note

Access date: 2026-06-02. For Israel Invoice allocation-number checks, use the updated 2026 thresholds: above ₪10,000 before VAT from 01/01/2026 and above ₪5,000 before VAT from 01/06/2026, when the legal conditions apply. This package does not request allocation numbers.
