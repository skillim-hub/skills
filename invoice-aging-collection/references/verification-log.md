# Verification Log

Access date: 2026-06-02

This log records two independent validation passes. Each row includes a short source quote of 140 characters or fewer.

| Check | Status | Package action | Pass 1 source | Pass 2 source |
|---|---|---|---|---|
| VAT standard rate | ✓✓ | 18% standard VAT since 01/01/2025 and still used in 2026 examples. | https://www.gov.il/he/pages/vat-history<br>Quote: 1.1.25 עלה המע"מ ל-18% | https://www.gov.il/BlobFolder/dynamiccollectorresultitem/extended-practical-accounting-exam-11526/he/final-exams_extended-practical-accounting-exam-11526.pdf<br>Quote: מע"מ 18% 2,646.00 |
| Small-claims ceiling | ✓✓ | Current ceiling is ₪39,900 as of 01/01/2026. | https://www.gov.il/he/service/filing_a_small_claim<br>Quote: סכום תביעה קטנה יכול להיות עד 39,900 ₪ (נכון ל-1.1.2026). | https://www.kolzchut.org.il/he/הגשת_תביעה_קטנה<br>Quote: עד סכום של 39,900 ₪ (נכון לינואר 2026) |
| Small-claims filing fee | ✓✓ | Fee is 1% of claim amount with ₪50 minimum. | https://www.gov.il/he/service/filing_a_small_claim<br>Quote: האגרה על הגשת תביעה קטנה היא 1% מסכום התביעה, ולפחות 50 ₪. | https://www.gov.il/he/pages/fees_3<br>Quote: אגרה של 1% משווי התביעה |
| Fixed-amount enforcement claim ceiling | ✓✓ | Service supports fixed-amount claims up to ₪75,000. | https://www.gov.il/he/service/claim_for_a_specified_amount_opening_file<br>Quote: בסכום של עד 75,000 ש"ח | https://www.gov.il/he/pages/collection_enforcment<br>Quote: תביעה על סכום קצוב בסכום של עד 75,000 ₪ |
| Enforcement fee table | ✓✓ | 2026 fee table confirms regular and short-route opening fees. | https://www.gov.il/BlobFolder/policy/fees-table-eca/he/fees-table-eca.pdf<br>Quote: מסלול רגיל - תשלום אגרה בסך 1% מגובה החוב | https://www.gov.il/he/pages/fees-table-eca<br>Quote: טבלת אגרות הוצאה לפועל 2026 |
| Interest and linkage reform | ✓✓ | From 01/01/2025 the reformed mechanism affects debt interest handling. | https://www.gov.il/he/pages/news-2024-12-31-interest-law<br>Quote: החל מתאריך 01/01/2025, נכנס לתוקפו תיקון מס' 9 | https://www.gov.il/he/pages/psikat-ribit-magak-faq<br>Quote: ריבית שקלית בלבד אך לא יתווספו לחוב דמי פיגורים |
| Payment Ethics Law terminology | ✓✓ | Official sources use חוק מוסר תשלומים לספקים and payment timing language. | https://www.gov.il/he/pages/press_03062022_b<br>Quote: מטרתו להסדיר את מועדי התשלום לספקים | https://main.knesset.gov.il/apps/legislation/main/bills/576454<br>Quote: קובע מועדי תשלום מקסימאליים לספק |
| Privacy law relevance | ✓✓ | Client contact and debt data can be personal data and must be minimized and secured. | https://www.gov.il/he/departments/the_privacy_protection_authority<br>Quote: הגנת המידע האישי במאגרי מידע דיגיטליים | https://www.gov.il/BlobFolder/news/legat_terms/he/Legal%20Terms.pdf<br>Quote: לצמצם את הסיכונים לפרטיות הנובעים מאיסוף ועיבוד מידע אישי |
| Communications Law section 30A | ✓✓ | Advertising-message rules are distinct, but reminder workflows should avoid spam-like conduct. | https://fs.knesset.gov.il/17/law/17_lsr_299991.pdf<br>Quote: דבר פרסומת - מסר המופץ באופן מסחרי | https://www.gov.il/he/pages/17052018_7<br>Quote: הסכמה שניתנה באמצעות שיחה מוקלטת או הודעה אלקטרונית |
| Consumer-protection terminology | ✓✓ | Use restrained language for consumers and avoid misleading pressure. | https://www.gov.il/he/pages/cpfta_consumers_info_isur_hatayat_hatzarchan<br>Quote: הצרכן יקבל מידע מלא ואמיתי לפני ואחרי ביצוע עסקה | https://www.gov.il/he/pages/cpfta_asakimnov2020<br>Quote: לשימוש שעיקרו אישי, ביתי או משפחתי |
| Israel Invoice thresholds | ✓✓ | Allocation-number thresholds change in 2026: ₪10,000 then ₪5,000 before VAT. | https://www.gov.il/he/pages/sa311225-1<br>Quote: ירד הרף המינימלי שמעליו חלה החובה ל-10,000 ₪ | https://www.gov.il/BlobFolder/policy/professional-directives-090226-1/he/IncomeTax_professional-directives-090226-1.pdf<br>Quote: חשבוניות מס התשומות... אינו עולה על 5,000 ₪ |
| Israel Invoice API endpoints | ✓✓ | Current Tax Authority API reference confirms production and sandbox endpoint paths. | https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-180724.pdf<br>Quote: https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval | https://www.gov.il/BlobFolder/generalpage/israel-invoice-160723/he/vat_software-houses-140725.pdf<br>Quote: https://openapi.taxes.gov.il/shaam/production/MultiInvoiceInformationApi/v1/Details |
| WhatsApp messages endpoint | ✓✓ | Use the Cloud API Messages API and current Graph version, not a stale hardcoded version. | https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages<br>Quote: You send them using the Messages API (part of the Cloud API). | https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform<br>Quote: Cloud API enables you to programmatically message |
| WhatsApp Hebrew template language | ✓✓ | Meta lists Hebrew template language code as he. | https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/supported-languages/<br>Quote: Hebrew. he | https://mumble.co.il/information-center/whatsapp-templates-concept-guide<br>Quote: Every message template is defined for a single language |
| WhatsApp webhook field | ✓✓ | Subscribe to the WhatsApp webhook messages field for incoming messages/statuses. | https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview/<br>Quote: Webhooks are HTTP requests containing JSON payloads | https://developers.facebook.com/docs/graph-api/webhooks/<br>Quote: receive real-time HTTP notifications |
| Email authentication | ✓✓ | SPF/DKIM/DMARC remains the correct delivery-control guidance. | https://support.google.com/a/answer/81126?hl=en<br>Quote: All senders: SPF or DKIM; Bulk senders: SPF, DKIM, and DMARC. | https://datatracker.ietf.org/doc/html/rfc7489<br>Quote: DMARC is a scalable mechanism |

## Summary

| Total checks | ✓✓ count | ✗→✓ count | final ✗ count |
|---:|---:|---:|---:|
| 16 | 16 | 0 | 0 |

## Corrections applied

- Replaced the hardcoded WhatsApp Graph API version with `{GRAPH_API_VERSION}` in public documentation.
- Added verified 2026 small-claims, enforcement, VAT, and Israel Invoice figures to `references/api-reference.md`.
- Added tax and filing boundary rules to both operating guides.
- Kept statutory interest language conditional and review-gated.
- Corrected a Hebrew typo in the due-date rules.
