# Test Scenarios

1. Standard Hebrew tax invoice receipt: extract vendor, number, date, net, VAT, gross, high confidence.
2. English tax invoice: parse English labels and ISO date.
3. Exempt dealer receipt: set VAT to zero and flag no inference.
4. Missing vendor: keep fields and flag vendor missing.
5. Customer block before supplier: avoid customer as vendor.
6. Multiple totals: prefer gross total over subtotal.
7. VAT math mismatch: preserve visible values and flag.
8. Visible VAT rate only: infer VAT when enabled.
9. Missing VAT rate: infer only when configuration allows.
10. Two-digit year: normalize to `DD/MM/YYYY`.
11. ISO date: normalize correctly.
12. Invalid date: set null and flag.
13. Credit note with negative amounts: preserve negatives.
14. Credit note with positive amounts: flag sign review.
15. Foreign currency invoice: preserve USD/EUR/GBP and flag conversion.
16. Payment app screenshot: mark digital wallet and warn.
17. Card approval number: do not use as document number.
18. Allocation number: store separately.
19. OCR digit confusion: parse `₪l18.OO` as `118.00`.
20. RTL amount order: detect `118.00 ₪ לתשלום סה"כ`.
21. Duplicate copy: flag copy/duplicate.
22. Proforma invoice: flag review before import.
23. Receipt without VAT: gross extracted, VAT null, flag.
24. Restaurant tip: select total paid and flag unclear VAT if needed.
25. Multiple documents in one image: flag manual review.
26. Very short OCR: low confidence.
27. Mixed Hebrew/English: parse both label sets.
28. Phone number near top: ignore as amount or document number.
29. Bank transfer receipt: `payment_method = bank_transfer`.
30. Cash receipt: `payment_method = cash`.

## 31. High-value 2026 tax invoice without allocation number

Input contains a June 2026 ILS tax invoice above ₪5,000 before VAT and no `מספר הקצאה`.

Expected:

- extraction succeeds
- `requires_allocation_number` is true
- review flag prompts verification of the missing allocation number

## 32. High-value 2026 tax invoice with allocation number

Input contains a June 2026 ILS tax invoice above ₪5,000 before VAT and `Allocation Number: 123456789`.

Expected:

- `allocation_number = 123456789`
- no missing-allocation review flag
