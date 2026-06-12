# Verification Log

Access date for all checks: 2026-06-03. Quotes are short excerpts from the source result or opened page and are kept under 140 characters.

| Check | Pass 1 source | Pass 2 source | Status | Package action |
|---|---|---|---|---|
| Israeli VAT rate | Israel Tax Authority VAT history, https://www.gov.il/he/pages/vat-history, quote: "1.1.25 עלה המע"מ ל-18%" | Prime Minister Office decision, https://www.gov.il/he/pages/dec1270-2024, quote: "18% במקום 17% החל מיום 1 בינואר 2025" | ✓✓ | Added VAT display guidance and kept examples tax-neutral unless explicitly needed |
| VAT still reflected in 2026 materials | gov.il accounting exam 2026, quote: "מע"מ 18% ... 31/12/2025" | Knesset material 2026, quote: "2026 ... מע"מ (18" | ✓✓ | Marked VAT as current for 2026 examples |
| Graph API latest version | Meta Graph API changelog, https://developers.facebook.com/docs/graph-api/changelog, quote: "v25.0. February 18, 2026" | Meta Graph API overview, https://developers.facebook.com/docs/graph-api/, quote: "The latest version is: v25.0" | ✗→✓ | Updated client, CLI, docs, examples, and tests from `v20.0` to `v25.0` |
| Cloud API official status | Meta Postman collection, https://www.postman.com/meta/whatsapp-business-platform/collection/wlk6lh4/whatsapp-cloud-api, quote: "hosted by Meta, is the official WhatsApp Business Platform API" | WhatsApp Developer Hub, https://whatsappbusiness.com/developers/developer-hub/, quote: "test, build and integrate the WhatsApp Business Platform" | ✓✓ | Kept Cloud API as official integration path |
| Send messages endpoint | Meta message API reference, https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/whatsapp-business-phone-number/message-api, quote: "POST /{Phone-Number-ID}/messages Send Message" | Postman Messages folder, https://www.postman.com/meta/whatsapp-business-platform/folder/13382743-6162ac5d-de2e-42aa-9ff9-f77a3dcbd3f8, quote: "Use the /{Phone-Number-ID}/messages endpoint" | ✓✓ | Kept endpoint path and updated examples to `v25.0` |
| Service window vs templates | Meta send messages docs, https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages, quote: "outside of a customer service window, use template messages" | Template guide source, https://mumble.co.il/information-center/whatsapp-api-templates-ultimate-guide, quote: "outside the 24-hour window" | ✓✓ | Kept template-vs-free-form decision tree |
| Webhook event field | Meta webhook overview, https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview/, quote: "Webhooks ... WhatsApp Business Platform" | n8n community operational report, quote: "webhook subscription needs to include the `messages` field" | ✓✓ | Kept `messages` field and webhook troubleshooting |
| Status webhook event names | Meta status webhook reference, quote: "Status messages webhook reference. Updated: May 21, 2026" | Hookdeck guide, quote: "sent, delivered, read, and potentially failed" | ✓✓ | Kept status parsing guidance and delivery reconciliation |
| Pricing model | WhatsApp Business pricing, https://whatsappbusiness.com/products/platform-pricing/, quote: "charged on a per-message basis for each message we deliver" | Meta pricing docs search result, quote: "Pricing on the WhatsApp Business Platform" | ✗→✓ | Reworded cost guidance from conversation costs to delivered-message costs and updated sample pricing model to `PMP` |
| Message categories | WhatsApp Business pricing, quote: "marketing, utility, authentication, and service" | Meta pricing page, quote: "four message categories" | ✓✓ | Kept appointment reminders under Utility when non-promotional |
| Hebrew template language code | Meta supported languages, quote: "Hebrew. he" | Telesign supported-language reference, quote: "Hebrew, he" | ✓✓ | Kept `language.code = he` |
| Israeli anti-spam terminology | Knesset Amendment 40 PDF, quote: "דבר פרסומת" | Ministry of Communications FAQ, quote: "סעיף 30א(ה) לחוק התקשורת" | ✓✓ | Kept legal terms `דבר פרסומת` and `הודעת סירוב`; no legal-advice claim |
| Anti-spam prior consent | Knesset Amendment 40 PDF, quote: "בלא קבלת הסכמה מפורשת מראש" | Privacy Protection Authority marketing page, quote: "לא ישגר מפרסם דבר פרסומת" | ✓✓ | Kept separate marketing-consent rule |
| Privacy information-security regulations | Privacy Protection Authority, quote: "דרישות אבטחת מידע ברורות" | Govextra Amendment 13 guide, quote: "נוהל אבטחה ארגוני כתוב" | ✓✓ | Kept data minimization and security checklist |
| Database notice/registration terminology | Privacy Authority notice service, quote: "להודיע לרשות, בתוך 30 ימים" | Privacy Authority registration service, quote: "פרטי בעל השליטה במאגר המידע" | ✓✓ | Kept `מאגר מידע` and owner/control terminology |
| Consumer cancellation period | Consumer Protection Authority, https://www.gov.il/he/pages/returns, quote: "ניתן לבטל את הרכישה תוך 14 ימים" | Knesset legislation page, quote: "עסקת מכר מרחוק" | ✓✓ | Kept consumer-law caution without hard-coding every vertical rule |
| data.gov.il API | data.gov.il docs, https://data.gov.il/docs, quote: "Servers. https://data.gov.il/api/3" | data.gov.il home, https://data.gov.il/, quote: "מרכז מאגרי נתונים מכלל משרדי הממשלה" | ✓✓ | Kept optional CKAN example for public datasets |
| Israeli phone prefix | ITU/MOC country code source, quote: "Israel (country code +972)" | Ministry of Communications department page, quote: "responsible for setting policy" | ✓✓ | Kept `+972` normalization |
| E.164 / WhatsApp phone-number format | Syniverse WhatsApp registration docs, quote: "E.164 formatted number" | Infobip E.164 reference, quote: "limited to 15 digits maximum" | ✓✓ | Kept digits-only API payload normalization and validation |
| Claim that WhatsApp is the standard Israeli business channel | Times of Israel blog, quote: "default communication layer" | Gov.il service pages show WhatsApp service channels, quote: "WhatsApp Service: 050-6255727" | ✗→✓ | Removed absolute "standard/main" wording; replaced with "common customer-service channel" |

## Summary

| Total checks | ✓✓ count | ✗→✓ count | Final ✗ count |
|---:|---:|---:|---:|
| 19 | 16 | 3 | 0 |
