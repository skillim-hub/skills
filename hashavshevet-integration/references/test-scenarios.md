# Test scenarios

Use these scenarios for regression testing, dry runs, and acceptance checks.

## 1. Current VAT calculation

Input: net amount ₪100.00, invoice date 05-06-2026.

Expected result: VAT ₪18.00, gross ₪118.00.

## 2. Allocation threshold before June 2026

Input: tax invoice, B2B customer VAT number present, net amount ₪10,000.00, date 15-01-2026.

Expected result: allocation not required because the amount does not exceed the threshold.

## 3. Allocation threshold above January 2026 threshold

Input: tax invoice, B2B customer VAT number present, net amount ₪10,000.01, date 15-01-2026.

Expected result: allocation required.

## 4. Allocation threshold after June 2026

Input: tax invoice, B2B customer VAT number present, net amount ₪5,000.01, date 02-06-2026.

Expected result: allocation required.

## 5. Consumer invoice

Input: tax invoice, no customer VAT number, net amount ₪30,000.00, date 02-06-2026.

Expected result: allocation workflow not triggered by the local rule, and the record is treated as non-B2B until customer classification is corrected.

## 6. Receipt only

Input: receipt document, net amount ₪20,000.00, date 02-06-2026, customer VAT number present.

Expected result: allocation not required because the document is not a tax invoice or tax invoice/receipt.

## 7. Balanced journal entry

Input: debit customer ₪1,180.00, credit income ₪1,000.00, credit VAT output ₪180.00.

Expected result: journal entry passes balance validation.

## 8. Unbalanced journal entry

Input: debit customer ₪1,180.00, credit income ₪1,000.00.

Expected result: journal entry fails and no import file is generated.

## 9. Hebrew encoding conversion

Input: Windows-1255 CSV with customer name `לקוח בדיקה`.

Expected result: UTF-8 staging JSON preserves the Hebrew name.

## 10. Customer sync with normalized VAT number

Input: customer VAT number `514-087-337`.

Expected result: outgoing payload uses `514087337`.

## 11. Duplicate customer prevention

Input: two source customers with the same VAT number and different display names.

Expected result: staging report flags a duplicate and requires account-owner decision before import.

## 12. BTKN generation

Input: one entry with company ID `514087337`, entry ID `JE-1001`, date `05-06-2026`, debit `1100`, credit `4000`, net ₪1,000.00, VAT ₪180.00.

Expected result: generated `BTKN.TXT` includes one detail row, Windows-1255 encoding, and DD-MM-YYYY date.

## 13. Multi-company isolation

Input: two companies, each with separate config, token, and staging folder.

Expected result: each output path includes the matching company ID, and cross-company records are rejected.

## 14. OPENFORMAT skeleton dry run

Input: one balanced journal entry.

Expected result: generated staging files include `INI.TXT`, `BKMVDATA.TXT`, one B100 count, and a Z900 summary line.

## 15. SHAAM payload validation

Input: payload missing invoice number and customer VAT number.

Expected result: local validation reports both missing fields before any HTTP call.
