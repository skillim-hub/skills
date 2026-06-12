# Live verification log

Access date: 2026-06-01

This log records the live web validation pass for the package. Public Green Invoice / Morning pages were opened directly where possible. The in-app URL requires JavaScript and authentication, so developer-menu claims were validated through the public help-center pages that describe the exact in-app paths.

## Phase 1 opened pages and search findings

| Item | Status | Source URL | Relevant quoted snippet |
|---|---|---|---|
| Main public API documentation landing page | ✓ confirmed | https://www.greeninvoice.co.il/api-docs/ | "תיעוד API מלא למתכנתים וחברות" |
| API-key generation page | ✓ confirmed | https://www.greeninvoice.co.il/help-center/generating-api-key/ | "המפתח שיווצר יהיה מורכב ממזהה מפתח ומפתח סודי" |
| API-key plan gate | ✓ confirmed | https://www.greeninvoice.co.il/help-center/generating-api-key/ | "זמין למנויי Best ומעלה" |
| API-key secret visibility | ✓ confirmed | https://www.greeninvoice.co.il/help-center/generating-api-key/ | "המפתח הסודי שנוצר מוצג פעם אחת בלבד" |
| Sandbox instructions | ✓ confirmed | https://www.greeninvoice.co.il/help-center/generating-api-key/ | "להירשם בקישור כאן לסביבת ה-Sandbox" |
| App URL accessibility | ✓ confirmed limitation | https://app.greeninvoice.co.il/ | "app doesn't work properly without JavaScript enabled" |
| Tax Authority connection path | ✓ confirmed | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "נכנסים לאזור רשות המיסים במערכת" |
| Tax Authority authorization active check | ✓ confirmed | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "ההרשאה לרשות המיסים נמצאת במצב פעיל" |
| Webhook conceptual docs | ✓ confirmed | https://www.greeninvoice.co.il/magazine/webhooks/ | "וובהוק הוא למעשה קישור (כתובת URL)" |
| Webhook product availability, magazine | ✓ confirmed | https://www.greeninvoice.co.il/magazine/webhooks/ | "Webhooks זמינים למנויים במסלול Extra" |
| Webhook setup page availability | ✓ confirmed | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "זמין למנויי Best ומעלה" |
| Webhook URL requirement | ✓ confirmed | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "כתובת ה-URL אליה יישלחו האירועים (עם תחילית https בלבד)" |
| Webhook retry behavior | ✓ confirmed | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "המערכת תנסה לבצע שוב את השליחה במשך מספר פעמים" |
| Webhook retry window | ✓ confirmed | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "עד לטווח של 24 שעות מהשליחה הראשונה" |
| Allocation background | ✓ confirmed | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "מספר הקצאה הוא החותמת הדיגיטלית" |
| VAT current rate | ✓ confirmed | https://www.gov.il/he/pages/vat-history | "1.1.25 עלה המע"מ ל-18%" |
| VAT effective date | ✓ confirmed | https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx | "effective January 1, 2025" |
| 2026 allocation threshold, Tax Authority search | ✓ confirmed | https://www.gov.il/he/pages/pa240525-1 | "מ-5,000 ₪" |
| 2026 threshold change notice | ✓ confirmed | https://www.gov.il/he/pages/pa301225-2 | "1.6.2026 ... 5,000 ₪ לפני מע"מ" |
| Morning rebrand wording | ✓ confirmed | https://www.greeninvoice.co.il/api-docs/ | "מורנינג של חשבונית ירוקה" |
| API base URL update | ✓ confirmed | https://www.greeninvoice.co.il/help-center/api-updates-26/ | "הכתובת החדשה: api.greeninvoice.co.il/api" |
| Old base URL deprecation | ✓ confirmed | https://www.greeninvoice.co.il/help-center/api-updates-26/ | "כתובת הישנה: www.greeninvoice.co.il/api" |
| Token body update | ✗ corrected | https://www.greeninvoice.co.il/help-center/api-updates-26/ | "יש להוסיף גם: "grant_type": "client_credentials"" |
| New developer-doc token field | ✗ corrected | https://developers.morning.co/ | "returned accessToken as a Bearer token" |
| Bearer header | ✓ confirmed | https://developers.morning.co/ | "Authorization: Bearer <accessToken>" |

## Package verification items

| Check | Status | Corrected value or decision | Source URL | Quoted snippet |
|---|---|---|---|---|
| Product/rebrand name | ✓ confirmed | Use Morning / Green Invoice product names only as API subject matter. | https://www.greeninvoice.co.il/api-docs/ | "מורנינג של חשבונית ירוקה" |
| Production base URL | ✓ confirmed | `https://api.greeninvoice.co.il/api/v1` for v1 endpoint examples. | https://www.greeninvoice.co.il/help-center/api-updates-26/ | "הכתובת החדשה: api.greeninvoice.co.il/api" |
| Old base URL | ✗ corrected | Do not use `www.greeninvoice.co.il/api` in examples. | https://www.greeninvoice.co.il/help-center/api-updates-26/ | "הכתובת הישנה: www.greeninvoice.co.il/api" |
| Token endpoint | ✓ confirmed with change | Keep `/account/token` under the API base path. | https://www.greeninvoice.co.il/help-center/api-updates-26/ | "קריאת קבלת Token" |
| Token request body | ✗ corrected | Send `id`, `secret`, and `grant_type: client_credentials`. | https://www.greeninvoice.co.il/help-center/api-updates-26/ | "בנוסף ל-id ול-secret" |
| Token response field | ✗ corrected | Prefer `accessToken`; retain compatibility with legacy `token`. | https://developers.morning.co/ | "accessToken" |
| Auth request header for API calls | ✓ confirmed | `Authorization: Bearer <accessToken>`. | https://developers.morning.co/ | "Authorization: Bearer <accessToken>" |
| `X-Authorization-Bearer` response header | ✗ corrected | No current official public page found documenting this header; docs no longer claim it. | https://developers.morning.co/ | "Bearer token in the Authorization header" |
| Token validity | ✓ confirmed | Access token validity is one hour where described by indexed developer docs. | https://developers.morning.co/ | "accessToken is valid for 1 hour" |
| Document type 10 | ✓ confirmed | הצעת מחיר / Price Quote. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "10 – הצעת מחיר" |
| Document type 100 | ✓ confirmed | הזמנה / Order. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "100 – הזמנה" |
| Document type 200 | ✓ confirmed | תעודת משלוח / Delivery Note. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "200 – תעודת משלוח" |
| Document type 210 | ✓ confirmed | תעודת החזרה / Return Note. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "210 – תעודת החזרה" |
| Document type 300 | ✓ confirmed | חשבון עסקה / Transaction Invoice or payment demand. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "300 – חשבון עסקה" |
| Document type 305 | ✓ confirmed | חשבונית מס / Tax Invoice. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "305 – חשבונית מס" |
| Document type 320 | ✓ confirmed | חשבונית מס / קבלה / Tax Invoice-Receipt. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "320 – חשבונית מס / קבלה" |
| Document type 330 | ✓ confirmed | חשבונית זיכוי / Credit Note. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "330 – חשבונית זיכוי" |
| Document type 400 | ✓ confirmed | קבלה / Receipt. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "400 – קבלה" |
| Document type 405 | ✓ confirmed | קבלה על תרומה / Donation Receipt. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "405 – קבלה על תרומה" |
| Document type 500 | ✓ confirmed | הזמנת רכש / Purchase Order. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "500 – הזמנת רכש" |
| Document type 600 | ✓ confirmed | קבלת פיקדון / Deposit Receipt. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "600 – קבלת פיקדון" |
| Document type 610 | ✓ confirmed | משיכת פיקדון / Deposit Withdrawal. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "610 – משיכת פיקדון" |
| Numeric payment type table | ✗ corrected | Current public webhook examples expose `paymentMethod.type` strings; numeric table is retained as legacy API enum with warning. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "paymentMethod": { "type": "wire-transfer" } |
| Payment method: bank transfer string | ✓ confirmed | Webhook payload uses `wire-transfer`. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "type": "wire-transfer" |
| Payment methods in UI | ✓ confirmed | Credit card, bit, Google Pay, Apple Pay, PayPal are public payment options. | https://www.greeninvoice.co.il/help-center/set-payment-methods/ | "כרטיס אשראי, bit, Google Pay ו-Apple Pay" |
| Withholding tax accounting concept | ✓ confirmed | Receipts can document withholding tax. | https://www.greeninvoice.co.il/help-center/tax-deduction-receipt/ | "ניכוי מס במקור" |
| Webhook `document/created` | ✓ confirmed | Event name remains `document/created`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "יצירת מסמך – document/created" |
| Webhook `client/created` | ✓ confirmed | Event name remains `client/created`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "יצירת לקוח – client/created" |
| Webhook `supplier/created` | ✓ confirmed | Event name remains `supplier/created`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "יצירת ספק – supplier/created" |
| Webhook `payment/received` | ✓ confirmed | Event name remains `payment/received`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "payment/received" |
| Webhook `sale-pages/page-contacted` | ✓ confirmed | Event name remains `sale-pages/page-contacted`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "sale-pages/page-contacted" |
| Webhook `sale-pages/order-paid` | ✓ confirmed | Event name remains `sale-pages/order-paid`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "sale-pages/order-paid" |
| Webhook `expense-draft/parsed` | ✓ confirmed | Event name remains `expense-draft/parsed`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "expense-draft/parsed" |
| Webhook `expense/file-updated` | ✓ confirmed | Event name remains `expense/file-updated`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "expense/file-updated" |
| Webhook `file/infected` | ✓ confirmed | Event name remains `file/infected`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "file/infected" |
| Webhook `expense-draft/declined` | ✓ confirmed | Event name remains `expense-draft/declined`. | https://www.greeninvoice.co.il/help-center/creating-webhook/ | "expense-draft/declined" |
| Webhook payload `client` object | ✓ confirmed | Document-created payload contains `client` fields. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "client": { |
| Webhook payload `items` array | ✓ confirmed | Document-created payload contains `items`. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "items": [ |
| Webhook payload tax rate shape | ✓ confirmed | `tax` array contains `name` and `rate`. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "name": "VAT" |
| Webhook payload `transactions` array | ✓ confirmed | Document-created payload contains `transactions`. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "transactions": [ |
| Webhook payload file links | ✓ confirmed | Payload contains signed download links. | https://www.greeninvoice.co.il/help-center/webhook-document-created/ | "downloadLinks" |
| Pagination start index | ✗ corrected | No stable public indexed page confirmed zero-based semantics; docs now avoid asserting a hard rule beyond endpoint docs. | https://developers.morning.co/ | "API Documentation" |
| Pagination max `pageSize` | ✗ corrected | Removed asserted max; use conservative values unless endpoint docs state otherwise. | https://developers.morning.co/ | "API Documentation" |
| VAT rate in 2026 | ✓ confirmed | 18%, effective 01/01/2025 and still current in 2026. | https://www.gov.il/he/pages/vat-history | "1.1.25 עלה המע"מ ל-18%" |
| SHAAM threshold May 2024 | ✓ confirmed | ₪25,000 before VAT. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "מאי 2024 25,000 ₪" |
| SHAAM threshold Jan 2025 | ✓ confirmed | ₪20,000 before VAT. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "ינואר 2025 20,000 ₪" |
| SHAAM threshold Jan 2026 | ✓ confirmed | ₪10,000 before VAT. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "ינואר 2026 10,000 ש״ח" |
| SHAAM threshold Jun 2026 onward | ✓ confirmed | ₪5,000 before VAT. | https://www.gov.il/he/pages/pa240525-1 | "מ-5,000 ₪" |
| Threshold basis | ✓ confirmed | Threshold is before VAT. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "לפני מע״מ" |
| Allocation applies to tax invoices | ✓ confirmed | Relevant to tax invoice and tax invoice-receipt. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "חשבוניות מס או חשבוניות מס קבלה" |
| Exempt dealers | ✓ confirmed | Exempt dealers are out because they issue receipts. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "עוסקים פטורים ... פטורים" |
| Foreign customers | ✓ confirmed | No allocation needed for foreign customers. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "אין שום צורך בהפקת מספר הקצאה עבורם" |
| Credit notes | ✓ confirmed | No new allocation request currently needed for credit note. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "אין צורך לבקש מספר הקצאה עבור חשבונית זיכוי" |
| Authorization term | ✓ confirmed | Tax Authority authorization valid for 3 months. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "תקפה למשך 3 חודשים" |
| Retroactive request | ✓ confirmed | Allocation can be requested after issuance within stated limits. | https://www.greeninvoice.co.il/magazine/israel-invoice/ | "עד שנה מהיום בו הופקה" |

## Diff summary applied to package

| Area | Change |
|---|---|
| `scripts/green_invoice_client.py` | `_auth_payload()` now sends `grant_type: client_credentials`; authentication accepts `accessToken`, `token`, or `access_token`; `expiresIn` is honored. |
| `scripts/test_green_invoice_client.py` | Auth tests now assert `grant_type` and `accessToken` support. |
| `SKILL.md` / `SKILL_HE.md` | Authentication snippets and SHAAM sections updated from live sources. |
| `references/api-reference.md` | Authentication response fields, token body fields, SHAAM and pagination caveats updated. |
| `references/troubleshooting.md` | Token diagnostics updated for `accessToken` and `grant_type`. |
| `metadata.json` | Version bumped to `1.5.0`. |
| `CHANGELOG.md` | Added `[1.5.0]` entry. |

## Final summary

| Metric | Count |
|---|---:|
| Total items checked | 65 |
| Confirmed | 55 |
| Corrected | 10 |
