# Test scenarios

Use these scenarios to validate translation behavior, register control, terminology, localization, and edge-case handling.

| # | Scenario | Source | Direction | Register | Expected handling |
|---|---|---|---|---|---|
| 1 | Invoice request | Please issue a tax invoice/receipt for ₪1,250 plus VAT. | en-to-he | accounting | Use `חשבונית מס/קבלה`, `1,250 ₪`, `בתוספת מע״מ` |
| 2 | Receipt only | Please send the receipt after payment. | en-to-he | business | Use `קבלה` and avoid `חשבונית מס` unless present |
| 3 | VAT included | The price is ₪350 VAT included. | en-to-he | accounting | Use `350 ₪ כולל מע״מ` |
| 4 | Exempt dealer | I am registered as an exempt dealer. | en-to-he | accounting | Use `עוסק פטור` |
| 5 | Licensed dealer | The supplier is a licensed dealer. | en-to-he | accounting | Use `עוסק מורשה` |
| 6 | Withholding tax | Please send withholding tax approval. | en-to-he | accounting | Use `אישור ניכוי מס במקור` |
| 7 | Refund timing | Refund within 7 business days. | en-to-he | support | Use `החזר כספי` and `7 ימי עסקים` |
| 8 | Cancellation fee | The cancellation fee is non-refundable unless required by law. | en-to-he | legal | Use `דמי ביטול`, preserve condition, flag review |
| 9 | Delivery issue | The package arrived damaged and late. | en-to-he | support | Acknowledge issue, avoid blame, preserve facts |
| 10 | WhatsApp casual | Sounds good, I will send it today. | en-to-he | casual | Use short natural Hebrew, avoid stiff wording |
| 11 | Formal bank letter | Please confirm receipt of the attached documents. | en-to-he | formal | Use restrained formal Hebrew |
| 12 | Product name | Add Starter Plus to cart. | en-to-he | business | Preserve `Starter Plus`, translate `cart` |
| 13 | Coupon code | Use code SPRING25 at checkout. | en-to-he | business | Preserve `SPRING25`, use `קוד קופון` and `תשלום` |
| 14 | Privacy notice | We share personal information with service providers. | en-to-he | legal | Use `מידע אישי`, `ספקי שירות`, flag privacy review |
| 15 | Accessibility | Read our accessibility statement. | en-to-he | formal | Use `הצהרת נגישות` |
| 16 | Lease | The lease agreement includes a promissory note. | en-to-he | legal | Use `הסכם שכירות`, `שטר חוב`, flag review |
| 17 | Power of attorney | Please sign the power of attorney. | en-to-he | legal | Use `ייפוי כוח`, preserve legal-sensitive tone |
| 18 | Positive idiom | השירות היה חבל על הזמן. | he-to-en | casual | Translate as positive: excellent or awesome |
| 19 | Negative idiom | חבל על הזמן, לא שווה להתעסק עם זה. | he-to-en | business | Translate as negative: not worth the time |
| 20 | Poor quality idiom | המוצר הגיע על הפנים. | he-to-en | support | Translate as very poor or arrived in very poor condition |
| 21 | Agreement idiom | סבבה, נטפל בזה היום. | he-to-en | business | Translate as No problem or Understood depending on tone |
| 22 | Date localization | Please pay by 2026-03-05. | en-to-he | business | Convert to `05/03/2026` |
| 23 | Unknown gender | Please send your ID. | en-to-he | formal | Prefer `יש לשלוח צילום תעודה` |
| 24 | URL preservation | Upload the receipt at https://example.test/docs. | en-to-he | business | Preserve URL exactly |
| 25 | Email preservation | Send the invoice to billing@example.test. | en-to-he | business | Preserve email exactly |
| 26 | Mixed text | נא לשלוח invoice היום. | mixed | business | Translate or clean mixed terminology without damaging meaning |
| 27 | Nikud in source | טקסט עברי עם סימני ניקוד ולאחריו בקשת חשבונית. | he-to-en | business | Warn that nikud should be removed from technical prose |
| 28 | Consumer warranty | The warranty is valid for 12 months. | en-to-he | legal | Use `אחריות`, preserve 12 months, flag review if policy text |
| 29 | Self pickup | Self pickup is available from Tel Aviv. | en-to-he | business | Use `איסוף עצמי`, preserve city |
| 30 | Stored request | Create then show a request id. | en-to-he | support | Create response contains id and show returns same id |

| 29 | Current VAT reference facts | Ask for the release VAT reference. | n/a | accounting | Return 18% from 01/01/2025 with official-source warning |
| 30 | Current invoice-allocation threshold | Ask whether an invoice over 5,000 ₪ needs allocation review. | n/a | accounting | Flag 5,000 ₪ before VAT from 01/06/2026 and require professional verification |
