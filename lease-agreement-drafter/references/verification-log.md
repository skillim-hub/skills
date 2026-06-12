# Verification Log

Access date: 04/06/2026.

| Check | Pass 1 source | Pass 2 source | Status | Package action |
| --- | --- | --- | --- | --- |
| Israeli standard VAT rate is 18% from 01/01/2025 and still used for 2026 drafting. | Israel Tax Authority VAT history, https://www.gov.il/he/pages/vat-history, snippet: "1.1.25 עלה המע\"מ ל-18%" | Knesset Research and Information Center, 02/02/2026, snippet: "בישראל יש שני שיעורי מע\"מ, 18%" | ✓✓ | Added `CURRENT_ISRAEL_VAT_RATE = 0.18`; updated VAT wording in drafts. |
| VAT transition rule for payments from 01/01/2025. | Israel Tax Authority interpretation 5/01/2025, https://www.gov.il/.../vat_represent-info-051224-2.pdf, snippet: "החל מיום 01/01/2025 יחול מע\"מ בשיעור של 18%" | Chamber of Commerce tax update, snippet: "החל מיום 1 בינואר 2025... יעלה מ-17% ל-18%" | ✓✓ | Kept 18% as current standard rate; marked tax review for exceptions. |
| Residential lease VAT treatment: residential rental up to 25 years is generally VAT-exempt. | Supreme Court text, snippet: "השכרה למגורים לתקופה שאינה עולה על 25 שנים... פטורה ממס" | Kol Zchut VAT concept page, snippet: "השכרה למגורים לתקופה שאינה עולה על 25 שנים" | ✓✓ | Corrected `VAT_ON_APARTMENT` message from “usually” to the statutory exemption framing. |
| Fair Rent amendment exists and covers residential lease drafting content. | Ministry of Justice/Gov law page, snippet: "חוק השכירות והשאילה (תיקון) התשע\"ז-2017" | Knesset bill page, snippet: "הוראות לעניין חובת מסירת דירה ראויה למגורים, עריכת החוזה ותוכנו" | ✓✓ | Kept Fair Rent amendment checks and references. |
| Written residential contract, fit-for-residence, defects, payments, extension, cancellation topics are part of the amendment. | Knesset final approval release, snippet: "כללים לעריכת החוזה ותוכנו... תיקון פגמים" | Knesset bill page, snippet: "חובת מסירת דירה ראויה למגורים, עריכת החוזה ותוכנו" | ✓✓ | Kept workflow and troubleshooting sections for these topics. |
| Residential guarantee cap is the lower of one third of rent for the lease period and three months of rent. | Kol Zchut guarantee page, snippet: "שליש מהתקופה... הסכום המירבי" | Private law-firm explainer cross-check, snippet: "שלושה (3) חודשי שכירות או... שליש מתקופת השכירות" | ✓✓ | Kept cap formula and tests. |
| Covered residential rent threshold exclusion above ₪20,000 per month. | Knesset statutory text search result, snippet: "עולים על 20,000 שקלים חדשים" | Knesset committee draft, snippet: "דמי השכירות שלהן עולים על 20,000 ₪ בחודש" | ✓✓ | Kept ₪20,000 coverage warning. |
| Residential lease term screen: over three months and not over ten years should not be treated as automatically excluded. | Knesset statutory text, snippet: "תקופת השכירות לפי החוזה אינה עולה על עשר שנים" | Secondary current guide, snippet: "לפחות 3 חודשים ועד 10 שנים" | ✗→✓ | Corrected code from `< 120` months to `<= 120` months and added regression test. |
| Arnona is imposed on the actual holder of the property, including a tenant. | Ministry of Interior arnona page, snippet: "מס המוטל... על המחזיק למעשה בנכס" | Tel Aviv municipal arnona page, snippet: "המחזיק... בעל הנכס או שוכרו" | ✓✓ | Kept arnona allocation guidance. |
| Business licensing must be checked by business type and local authority. | Ministry of Interior business licensing topic, snippet: "אגף בכיר לרישוי עסקים" | Ministry of Interior online application page, snippet: "לעסקים שנדרשים להוציא רישיון עסק" | ✓✓ | Kept office permitted-use, signage, accessibility, and licensing checks. |
| Israel Invoice allocation-number thresholds for 2026. | Tax Authority FAQ, snippet: "החל מה-1 בינואר 2026 – 10,000 ₪ והחל מה-1 ביוני 2026 – 5,000 ₪" | Tax Authority 30/12/2025 release, snippet: "החל מיום 1.1.2026 יידרש מספר הקצאה ייחודי" | ✓✓ | Added `invoice_allocation_thresholds()` helper. |
| No network API hosts or webhook event names are required by this local skill. | Package API reference states local interface, snippet: "This is a non-network skill" | Source review found no webhook implementation or external endpoint dependency. | ✓✓ | Kept CLI/module interface and avoided fabricated webhook names. |

## Summary

| Total checks | ✓✓ double-confirmed | ✗→✓ corrected in pass 2 | Final ✗ |
| ---: | ---: | ---: | ---: |
| 12 | 11 | 1 | 0 |
