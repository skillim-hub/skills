# Workflow Guide

## Workflow 1: Single invoice photo to expense row

1. Photograph the full page in good light.
2. Rotate, crop, deskew, and run Hebrew+English OCR.
3. Extract vendor, document type, number, date, gross, VAT, net, payment method, and business ID.
4. Validate VAT arithmetic.
5. Show original image beside extracted JSON.
6. Export JSON for audit and CSV for bookkeeping.

CLI:

```bash
python -m invoice_ocr_extractor.cli parse --text-file invoice.txt --pretty
```

## Workflow 2: Monthly folder to CSV

```bash
python -m invoice_ocr_extractor.cli batch may-expenses --output may-expenses.csv --pretty-summary
```

Sort by confidence ascending, review rows below `0.85`, confirm VAT, then import.

## Workflow 3: Exempt dealer receipt

Expected behavior: set VAT to `0.0`, set net equal to gross, flag that VAT was not inferred, and avoid VAT deduction assumptions.

## Workflow 4: Credit note

Detect `credit_note`, preserve negative amounts, validate signs, and verify destination-system import convention before export.

## Workflow 5: Payment app screenshot

Classify `Bit` or `PayBox` as digital wallet. Add `Payment confirmation may not be a tax invoice` unless invoice or receipt wording appears.

## Workflow 6: Foreign currency invoice

Preserve original currency and amount. Add `Foreign currency; conversion rate required for local bookkeeping`.

## Workflow 7: Low-quality OCR

Crop, increase contrast, rotate, deskew, rerun OCR, then route to manual entry if confidence remains low.

## Workflow 8: Duplicate detection

Use `normalized_vendor + document_number + date + total_gross`. Fallback to `normalized_vendor + date + total_gross + business_id` when document number is missing.

## Human review triggers

Review when confidence is below `0.85`, VAT is inferred, document type is `unknown`, `proforma`, or `credit_note`, vendor/date/number is missing, currency is not ILS, a duplicate indicator appears, or a payment screenshot lacks tax document wording.

## Workflow 9: Allocation-number review for 2026 tax invoices

When a tax invoice or tax-invoice receipt is in ILS and the amount before VAT is above the current Tax Authority threshold, verify whether `מספר הקצאה` is visible. From 01/01/2026 through 31/05/2026, review invoices above ₪10,000 before VAT. From 01/06/2026, review invoices above ₪5,000 before VAT. If the number is missing, keep the extraction but route the record to manual review before claiming input VAT.
