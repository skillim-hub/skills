# Verification Log

Access date for all web checks: 2026-06-02.

Status legend: `` double-confirmed, `→` corrected in pass 2, `final ` not confirmed.

| Status | Check | Pass 1 source | Pass 2 source |
|---|---|---|---|
|  | Current standard Israeli VAT rate is 18%, effective 01/01/2025 and still current for 2026. | Israel Tax Authority glossary, https://www.gov.il/en/pages/taxes-glossary. Quote: "uniform rate of 18% starting from January 1, 2025". | PwC Worldwide Tax Summaries, https://taxsummaries.pwc.com/israel/corporate/other-taxes. Quote: "The 2025 current rate of VAT is 18%." |
|  | VAT history shows the rate rose to 18% on 01/01/2025. | Israel Tax Authority VAT history, https://www.gov.il/he/pages/vat-history. Quote: "1.1.25 עלה המע"מ ל-18%". | Knesset press release, https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx. Quote: "effective January 1, 2025". |
| → | Israel Invoice allocation threshold for 2026 is accelerated: above ₪10,000 before VAT from 01/01/2026 and above ₪5,000 before VAT from 01/06/2026. | Older API v2 PDF, https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-180724.pdf. Quote: "בשנת -2026 ... גבוה מ- 15,000". | VAT Implementation Order 01/2025, https://www.gov.il/BlobFolder/policy/inst-071225-1/he/vat_inst-071225-1.pdf. Quote: "01.01.2026 ... 10,000 ₪ ... 01.06.2026 ... 5,000 ₪". |
|  | Tax Authority request page confirms the 2026 online allocation threshold is above ₪5,000 before VAT. | Request allocation number service, https://www.gov.il/he/service/request-assignment-number-for-tax-invoice. Quote: "סכום העסקה לפני מע"מ גבוה מ-5,000 ₪ (מעודכן לשנת 2026)". | Green Invoice 2026 explainer, https://www.greeninvoice.co.il/magazine/israel-invoice/. Quote: "החל מיוני 2026 ... מ-5000 ש"ח". |
|  | Israel Invoice APIs use OAuth2 user-restricted authorization. | English API PDF, https://www.gov.il/BlobFolder/generalpage/israel-invoice-160723/he/vat_software-houses-180724-en.pdf. Quote: "All services are powered by an OAuth2 protocol". | Hebrew API PDF, https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-180724.pdf. Quote: "כל השירותים מופעלים ... בפרוטוקול 2OAUTH". |
|  | MinimumAmount API endpoint and hosts are official reference data; this package does not call them. | MinimumAmount PDF, https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-260825.pdf. Quote: "general-information/v2/MinimumAmount". | Same official PDF listing hosts. Quote: "Sandbox url ... ita-api.taxes.gov.il" and "Production Url ... openapi.taxes.gov.il". |
|  | MultiApproval API endpoint and hosts are official reference data; this package does not call them. | Hebrew API PDF, https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-180724.pdf. Quote: "Multi-invoices/v2/MultiApproval". | English API PDF, https://www.gov.il/BlobFolder/generalpage/israel-invoice-160723/he/vat_software-houses-180724-en.pdf. Quote: "Invoice Number Allocation Service". |
|  | Official line-item API fields support multi-line calculations: quantity, unit price, discount, line amount, VAT rate, VAT amount. | Hebrew API PDF table 2.2, https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-180724.pdf. Quote: "Quantity ... price_per_unit ... Discount ... vat_rate ... amount_vat". | Supplier invoice retrieval PDF, https://www.gov.il/BlobFolder/generalpage/israel-invoice-160723/he/vat_software-houses-140725.pdf. Quote: "items ... index ... id_catalog ... amount_vat". |
|  | Manual allocation-number service exists for invoice books or non-connected software and is free. | Request service page, https://www.gov.il/he/service/request-assignment-number-for-tax-invoice. Quote: "השירות ניתן ללא עלות". | Israel Invoice landing page, https://www.gov.il/he/departments/topics/israel-invoice. Quote: "בקשה למספר הקצאה לחשבונית מס". |
|  | Supplier invoice verification by allocation number exists and is free. | Verification service page, https://www.gov.il/he/service/verify-vendor-invoice-information. Quote: "אימות פרטי חשבונית הספק". | Israel Invoice English landing page, https://www.gov.il/en/departments/topics/israel-invoice/govil-landing-page. Quote: "Supplier invoice details verification based on allocation number". |
|  | Official terminology includes tax invoice, allocation number, input tax, VAT, zero-rate, and reverse charge. | VAT Implementation Order 01/2025. Quote: "חשבונית מס", "מספר הקצאה", "מס תשומות". | English API PDF. Quote: "tax invoice", "Allocation Number", "Input tax", "reverse charge". |
| final  | Webhook event names for Israel Invoice APIs. | Search across gov.il for "חשבוניות ישראל webhook" returned no relevant Tax Authority API webhook documentation. | Search across gov.il for "Israel Invoice webhook Tax Authority" returned unrelated public tenders, not invoice API event names. |
|  | The skill claim about multi-line invoices, discounts and per-line VAT is supported as a local calculation use case, not as an official product claim. | Hebrew API line table includes `Discount`, `amount_total`, `vat_rate`, `amount_vat`. Quote: "הנחת פריט ... שיעור המע"מ ... סכום המע"מ". | Supplier invoice retrieval PDF contains returned `items` and VAT/total fields. Quote: "items ... amount_vat ... payment_amount_including_vat". |

## Summary

| Total checks |  count | → count | final  count |
|---:|---:|---:|---:|
| 13 | 11 | 1 | 1 |

## Corrections applied

- Updated references to state the accelerated 2026 Israel Invoice allocation thresholds: above ₪10,000 before VAT from 01/01/2026 and above ₪5,000 before VAT from 01/06/2026.
- Added explicit API reference rows for `general-information/v2/MinimumAmount` and `Multi-invoices/v2/MultiApproval` as reference-only official endpoints.
- Added a clear note that webhook event names could not be confirmed from official Israel Invoice API documentation and are not used by this package.
- Kept the package as a local calculation helper and did not add official API calls.
