# Test Scenarios

Use these concrete scenarios for regression tests. Every production correction should become a new fixture.

| # | Scenario | Expected |
|---:|---|---|
| 1 | Clear Hebrew חשבונית מס/קבלה with vendor, ח.פ., number, date, subtotal, VAT, total | accepted |
| 2 | קבלה from עוסק פטור with total only | accepted, VAT null |
| 3 | Text-only WhatsApp message | unsupported, request attachment |
| 4 | Unsupported `.heic` file | unsupported |
| 5 | Blurry OCR confidence 0.35 | needs_review |
| 6 | Cropped total | needs_review |
| 7 | Cropped supplier header | needs_review |
| 8 | VAT mismatch | needs_review |
| 9 | Decimal comma `117,00 ₪` | accepted, 117.00 |
| 10 | Thousands separator `1,416.00 ₪` | accepted, 1416.00 |
| 11 | Israeli date `14/02/2026` | ISO `2026-02-14` |
| 12 | Impossible date `31/02/2026` | needs_review |
| 13 | Future date more than a year ahead | needs_review |
| 14 | Exact duplicate | duplicate |
| 15 | Duplicate without tax ID but same vendor/name/number/date/total | duplicate |
| 16 | Same vendor/date/amount but different invoice number | accepted |
| 17 | חשבונית זיכוי with negative total | credit classification |
| 18 | חשבונית פרופורמה | unsupported |
| 19 | הצעת מחיר | unsupported |
| 20 | Allocation required and present | accepted |
| 21 | Allocation required and missing | needs_review |
| 22 | Mixed Hebrew/English invoice | accepted |
| 23 | Credit card slip only | unsupported or review |
| 24 | Forwarded screenshot with WhatsApp UI | ignore UI numbers |
| 25 | Group chat | generic reply by default |
| 26 | `מעמ` without punctuation | VAT alias recognized |
| 27 | Total before subtotal | labelled total wins |
| 28 | דרישת תשלום | unsupported |
| 29 | Missing invoice number | needs_review |
| 30 | USD invoice | needs_review unless policy supports it |

## Fixture: clear invoice

```text
א.ב. שירותים בע"מ
ח.פ. 516123456
חשבונית מס/קבלה מס' 8841
תאריך 14/02/2026
סה"כ לפני מע"מ 99.00 ₪
מע"מ 18% 18.00 ₪
סה"כ לתשלום 117.00 ₪
מספר הקצאה 987654321
```

Expected fields: `accepted`, vendor `א.ב. שירותים בע"מ`, tax ID `516123456`, number `8841`, date `2026-02-14`, subtotal `99.00`, VAT `18.00`, total `117.00`, allocation `987654321`.

## Fixture: VAT mismatch

```text
כהן ייעוץ
ע.מ. 012345678
חשבונית מס 1007
תאריך 05/02/2026
לפני מע"מ 100.00 ₪
מע"מ 12.00 ₪
סה"כ 112.00 ₪
```

Expected: `needs_review` with `vat_mismatch`.

## Fixture: pro forma

```text
לוי אספקה
חשבונית פרופורמה 9001
תאריך 02/02/2026
סה"כ 1,200.00 ₪
```

Expected: `unsupported`.

## Test assertions

Accepted records must have vendor, supported document type, ISO date, positive total except credit, consistent VAT or null VAT, stable dedupe key, Hebrew reply with ₪, and DD/MM/YYYY date. Review records must have at least one warning and blocked export. Unsupported records must never create bookkeeping export.
