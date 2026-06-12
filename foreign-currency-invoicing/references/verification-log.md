# Web Verification Log

Access date for all rows: 2026-06-02. Snippets are short excerpts or search-result text from live web validation. Pass 2 used different queries or different sources where possible.

| Check | Status | Pass 1 source and snippet | Pass 2 source and snippet | Package action |
|---|---|---|---|---|
| Standard Israeli VAT rate is 18% from 01/01/2025 and remains the active 2026 default. | ✓✓ | Israel Tax Authority, https://www.gov.il/en/pages/taxes-glossary: "uniform rate of 18% starting from January 1, 2025" | PwC Worldwide Tax Summaries, https://taxsummaries.pwc.com/israel/corporate/other-taxes: "Last reviewed - 01 January 2026" and "VAT is 18%" | Kept default VAT rate at 0.18 from 01/01/2025. |
| VAT rate before 01/01/2025 was 17% for the helper's date split. | ✓✓ | Israel Tax Authority VAT history, https://www.gov.il/he/pages/vat-history: "1.1.25 עלה המע"מ ל-18%" and "01.10.15 ירד המע"מ ל-17%" | Knesset, https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx: "increased by one percentage point, effective January 1, 2025" | Kept pre-2025 default at 0.17. |
| Bank of Israel publishes representative exchange rates on foreign-currency business days. | ✓✓ | Bank of Israel English, https://boi.org.il/en/economic-roles/financial-markets/exchange-rates/: "publishes the representative exchange rate" | Bank of Israel Hebrew, https://www.boi.org.il/roles/markets/exchangerates/: "מפרסם בנק ישראל את שערי החליפין היציגים" | Kept Bank of Israel as the authoritative rate source. |
| Representative rate is an indicator and is not mandatory by law between private parties. | ✓✓ | Bank of Israel English, https://boi.org.il/en/economic-roles/financial-markets/exchange-rates/: "has no obligatory status under law" | Bank of Israel Hebrew, https://www.boi.org.il/roles/markets/exchangerates/: "אין לו מעמד מחייב על פי דין" | Added wording to retain the selected source and contract context. |
| Current Bank of Israel public API exposes `PublicApi/GetExchangeRates` and JSON. | ✓✓ | Bank of Israel QA, https://boi.org.il/qawebsite/: "https://boi.org.il/PublicApi/GetExchangeRates" and "JSON" | Bank of Israel extraction PDF, https://www.boi.org.il/media/ljsokufq/: "Boi.org.il/PublicApi/GetExchangeRates?asXml=true" | Kept current API parsing but stopped treating it as the primary dated endpoint. |
| Date-specific representative-rate extraction should use the SDMX series API. | ✗→✓ | Package v2 used unconfirmed `asOfDate` on `PublicApi/GetExchangeRate`. | Bank of Israel API guide, https://www.boi.org.il/information/bank-paymnts/guide/api-guide/: "GET https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/" | Corrected client, docs, CLI, and tests to generate SDMX CSV URLs. |
| SDMX exchange-rate content field and representative filter use EXR and OF00. | ✓✓ | Bank of Israel API guide: "BOI.STATISTICS/EXR/1.0" and "DATA_TYPE=OF00" | Bank of Israel PDF: "קוד עבור עולם התוכן: EXR" and "DATA_TYPE=OF00" | Documented endpoint strategy in API reference. |
| SDMX date filters accept daily `YYYY-MM-DD` dates. | ✓✓ | Bank of Israel API guide: "startPeriod" and "YYYY-MM-DD" | Bank of Israel PDF: "יש להשתמש בפורמט תאריך זה בלבד עבור תצפיות יומיות" | Client now emits `startPeriod` and `endPeriod`. |
| SDMX output supports CSV. | ✓✓ | Bank of Israel API guide: "format=csv" | Bank of Israel PDF: "פורמט שליפת הנתונים" and "csv" | Added CSV parser and CSV tests. |
| JPY appears as 100 units in Bank of Israel rates. | ✓✓ | Bank of Israel English exchange-rate page: "100 Yen" and "100 units JPY" | Bank of Israel Hebrew exchange-rate page: "ין יפני" and "100 יחידות" | Kept unit-aware conversion guidance and tests. |
| Zero-rate and exempt VAT classifications are distinct; foreign currency alone is not enough. | ✓✓ | Israel Tax Authority tourism guidance, https://www.gov.il/en/pages/vat-tourists-zero-rate: "subject to zero VAT" | PwC Israel VAT summary: "Exports of goods and certain services... are zero-rated, and certain transactions are exempt" | Kept warnings and evidence notes for non-standard VAT categories. |
| Israel Invoices allocation-number requirement is separate from this calculation helper. | ✓✓ | Israel Invoices FAQ, https://www.gov.il/en/pages/faq_israel_invoice: "allocation number" | Israel Invoices govextra, https://govextra.gov.il/taxes/innovation/home/israel-invoices/: "מספר הקצאה" | Added operational reminder; no allocation API implemented. |
| Webhook event names. | ✓✓ | Package inspection found no webhook API or webhook claims. | Search and official source review found no webhook requirement for this helper. | Marked not applicable; no webhook names added. |

## Summary

| Total checks | ✓✓ count | ✗→✓ count | Final ✗ count |
|---:|---:|---:|---:|
| 13 | 12 | 1 | 0 |
