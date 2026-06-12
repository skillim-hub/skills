# Migration Checklist

## Metadata

- [ ] Remove creator and maintainer metadata fields.
- [ ] Remove non-neutral names, decorative media, decorative media and promotional callouts.
- [ ] Use neutral MIT license attribution.
- [ ] Bump version to `2.1.0`.

## Schema

| Old field | New field |
|---|---|
| `supplier` | `vendor` |
| `invoiceNo` | `document_number` |
| `invoiceDate` | `date` |
| `amount` | `total_gross` |
| `tax` | `vat_amount` |
| `subtotal` | `total_net` |
| `warnings` | `review_flags` |
| `score` | `confidence` |

## Parser

- [ ] Add Hebrew and English labels.
- [ ] Add exempt dealer logic.
- [ ] Add credit-note sign handling.
- [ ] Add foreign currency flags.
- [ ] Add payment app warning.
- [ ] Exclude approval, phone, business ID, and allocation numbers from document number.
- [ ] Add raw evidence snippets.

## Tests

- [ ] Cover at least 20 scenarios.
- [ ] Include Hebrew, English, exempt dealer, credit note, foreign currency, payment app, OCR errors, and VAT mismatch.

## Production

- [ ] Require review below confidence `0.85`.
- [ ] Store source hash and schema version.
- [ ] Protect raw OCR text.
- [ ] Verify current Israeli tax and bookkeeping requirements.

## 9. Web-validated 2026 allocation-threshold migration

- [ ] Replace stale 2026 threshold assumptions of ₪15,000 with the verified phase-down schedule.
- [ ] Use ₪10,000 before VAT for 01/01/2026 through 31/05/2026.
- [ ] Use ₪5,000 before VAT from 01/06/2026.
- [ ] Keep allocation number separate from document number.
- [ ] Route missing allocation numbers to manual review rather than blocking OCR extraction.
