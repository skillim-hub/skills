# Web Verification Log

Access date for all sources: 2026-06-02. Snippets are limited to 140 characters. Pass 2 used different queries and, where possible, different source families from Pass 1.

| Check | Status | Pass 1 source and snippet | Pass 2 source and snippet | Package action |
|---|---|---|---|---|
| Standard VAT rate in Israel for 2026 | ✓✓ | Israel Tax Authority glossary, https://www.gov.il/en/pages/taxes-glossary, "uniform rate of 18% starting from January 1, 2025" | VATCalc 2026 budget note, https://www.vatcalc.com/vat/israel-vat-rise-to-19-jan-2026-proposal/, "1% Vat rise from 17% to 18% from 1 January 2025" | Kept `0.18` defaults and added validation note. |
| VAT rate change effective date | ✓✓ | Israel Tax Authority VAT history, https://www.gov.il/he/pages/vat-history, "1.1.25 עלה המע"מ ל-18%" | Knesset press release, https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx, "effective January 1, 2025" | Kept date guidance and historical-rate warning. |
| Invoice Israel 2025 threshold | ✓✓ | Tax Authority business guide, https://govextra.gov.il/taxes/innovation/home/israel-invoices/, "בשנת 2025 התקרה היא 20,000 ₪" | Herzog 2026 VAT update, https://herzoglaw.co.il/en/news-and-insights/overview-of-vat-and-customs-updates-effective-in-2026/, "exceeding NIS 20,000 (before VAT)" | Added explicit threshold table. |
| Invoice Israel threshold from 01/01/2026 | ✓✓ | Tax Authority business guide, https://govextra.gov.il/taxes/innovation/home/israel-invoices/, "החל מה-1.1.2026 התקרה היא 10,000 ₪" | Herzog 2026 VAT update, same URL, "from January 1, 2026, the threshold amount was reduced to NIS 10,000" | Added explicit threshold table. |
| Invoice Israel threshold from 01/06/2026 | ✓✓ | Tax Authority business guide, https://govextra.gov.il/taxes/innovation/home/israel-invoices/, "החל מה-1.6.2026 התקרה היא 5,000 ₪" | Green Invoice 2026 guide, https://www.greeninvoice.co.il/magazine/israel-invoice/, "החל מיוני 2026 ... מ-5000 ש"ח" | Added explicit threshold table and threshold revalidation warning. |
| Invoice allocation service exists for manual/non-connected software | ✓✓ | Tax Authority service page, https://www.gov.il/he/service/request-assignment-number-for-tax-invoice, "לבקש באופן מקוון מספר הקצאה לחשבונית מס" | Tax Authority Invoice Israel topic, https://www.gov.il/he/departments/topics/israel-invoice, "בקשה למספר הקצאה לחשבונית מס" | Clarified request/response shapes are connector examples, not official endpoint contracts. |
| Tax Authority API program terminology | ✓✓ | Tax Authority API page, https://govextra.gov.il/taxes/innovation/home/api/, "שירותי ה-API יאפשרו דיווח אל רשות המסים" | Tax Authority Invoice Model API PDF, https://www.gov.il/BlobFolder/generalpage/israel-invoice-160723/he/IncomeTax_software-houses-en-040723.pdf, "THE INVOICE ISSUER'S API" | Kept generic API guidance and removed implication of stable public endpoint names. |
| Official webhook event names for this catalog skill | final ✗ | Tax Authority API searches did not confirm public webhook event names. | Invoice Israel and software-vendor searches did not confirm a public official webhook contract. | Added a Webhooks section stating no official public event-name contract was confirmed. |
| Computerized bookkeeping software registry requirement | ✓✓ | Tax Authority software registry, https://www.gov.il/he/service/itc-software-registry-for-computerized-accounting-systems, "תוכנות אלו חייבות ברישום על-פי חוק" | New dealer VAT guide, https://www.gov.il/he/departments/guides/vat-to-the-new-dealer?chapterIndex=5, "עליך לנהל פנקסי חשבונות" | Kept caution that production accounting/inventory systems may require registration. |
| New dealer bookkeeping terminology | ✓✓ | New dealer VAT guide, same URL, "ניהול ספרי העסק" | Tax Authority withholding/bookkeeping certificate service, https://www.gov.il/he/service/itc-gmishurim, "אישור ניהול ספרים" | Hebrew guide uses `ניהול ספרים`, `פנקסי חשבונות`, and `אישור ניהול ספרים`. |
| Consumer price display must be final/inclusive where applicable | ✓✓ | Consumer Protection Authority, https://www.gov.il/he/pages/cpfta_display_of_prices, "התשלום הנגבה ממנו בקופה זהה לזה המוצג" | Consumer Protection enforcement page, https://www.gov.il/he/pages/cpfta_ramilevi, "הצגת מחיר לא כולל מע"מ" | Kept consumer exports centered on final price with VAT. |
| Bank of Israel representative exchange-rate source | ✓✓ | Bank of Israel exchange rates, https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/, "publishes the representative exchange rate" | Hebrew BOI exchange page, https://www.boi.org.il/roles/markets/exchangerates/, "שערי חליפין יציגים" | Kept exchange-rate records but separated them from customer price exports. |
| Bank of Israel current series API host | ✗→✓ | Older BOI PDF mentioned `https://edge.boi.org.il/...` and older `Boi.org.il/PublicApi/GetExchangeRates?asXml=true`. | 2026 BOI API guide, https://www.boi.org.il/information/bank-paymnts/guide/api-guide/, "GET https://edge.boi.gov.il/FusionEdgeServer" | Corrected example endpoint from invented `/exchange-rates` to BOI SDMX host. |
| Customs currency-rate query service | ✓✓ | Tax Authority service, https://www.gov.il/he/service/exchange-rate, "שערי מטבע חוץ לצורכי מכס" | Tax Authority customs/import search results confirm customs-specific currency-rate service. | Added separate customs currency service section. |
| SKU, barcode, supplier SKU separation | ✓✓ | GS1/GTIN public terminology search confirmed GTIN/barcode as trade identifiers. | Inventory management software sources consistently separate product catalog, stock, vendors, and barcodes. | Kept separation guidance; no official Israeli tax API dependency. |
| Skill claim: manages SKUs, prices, VAT rates, stock levels for Israeli small businesses | ✓✓ | Exact-claim search found no conflicting source; inventory software listings confirm stock/catalog features. | Israel 2026 searches confirmed VAT and Invoice Israel obligations relevant to small businesses. | Kept claim as capability statement, not regulatory claim. |
| Hebrew official term for VAT | ✓✓ | Tax Authority glossary, https://www.gov.il/he/pages/taxes-glossary, "מס ערך מוסף" | VAT history page, https://www.gov.il/he/pages/vat-history, "שיעורי מס ערך מוסף" | Kept `מע״מ` and `מס ערך מוסף`. |
| Hebrew official term for allocation number | ✓✓ | Tax Authority service, https://www.gov.il/he/service/request-assignment-number-for-tax-invoice, "מספר הקצאה לחשבונית מס" | Invoice Israel topic, https://www.gov.il/he/departments/topics/israel-invoice, "בקשה למספר הקצאה" | Kept `מספר הקצאה` terminology. |

## Summary

| Metric | Count |
|---|---:|
| Total checks | 18 |
| Double-confirmed ✓✓ | 16 |
| Corrected in pass 2 ✗→✓ | 1 |
| Final unconfirmed ✗ | 1 |

## Search notes

The exact capability sentence `Manages item catalogs with SKUs, prices, VAT rates, and stock levels for Israeli small businesses.` was searched with `Israel 2026`. No official page describes this exact skill because it is a package capability statement. The underlying components were validated separately: inventory/catalog/stock as ordinary software capabilities, VAT rate and invoice thresholds against tax sources, and consumer price display against consumer-protection sources.
