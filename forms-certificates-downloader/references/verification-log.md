# Verification Log

Access date for all checks: 2026-06-02.

This log records live-source validation for the public portal registry and regulated facts referenced by the package. Quotes are short excerpts from source snippets or rendered pages.

| Check | Status | Pass 1 source | Pass 2 source | Package action |
|---|---|---|---|---|
| Current VAT rate | ✓✓ | https://www.gov.il/he/pages/vat-history — "1.1.25 עלה המע"מ ל-18%" | https://taxsummaries.pwc.com/israel/corporate/other-taxes — "The 2025 current rate of VAT is 18%." | Added VAT note to reference material. |
| VAT effective date | ✓✓ | https://www.gov.il/he/pages/vat-history — "1.1.25 עלה המע"מ ל-18%" | https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx — "effective January 1, 2025" | Confirmed 01/01/2025 wording. |
| Tax Authority department URL | ✗→✓ | https://www.gov.il/he/departments/israel_tax_authority — "רשות המסים בישראל מאחדת את אגפי המס השונים" | https://www.gov.il/en/departments/israel_tax_authority — "consolidates the various tax divisions" | Replaced older `govil-landing-page` URL. |
| Income-tax public topic URL | ✗→✓ | https://www.gov.il/he/departments/topics/income_tax_israel_tax_authority — "דו"ח מס שנתי ליחידים ובעלי עסקים" | https://www.gov.il/en/departments/topics/income_tax_israel_tax_authority — "Income tax is levied" | Replaced stale `income_tax_forms/govil-landing-page` URL. |
| Form 1301 public service naming | ✓✓ | https://www.gov.il/he/service/reporting-and-payment-2025-annual-tax-report-for-individuals — "טופס 1301" | https://www.gov.il/en/service/reporting-and-payment-2023-annual-tax-report-for-individuals — "annual tax report online" | Kept examples using focused query `1301`. |
| National Insurance forms URL | ✗→✓ | https://www.btl.gov.il/טפסים%20ואישורים/forms/Pages/default.aspx — "ניתן לקבל את הטפסים על ידי הורדה והדפסה" | https://www.btl.gov.il/English%20Homepage/About/Forms%20Authorization/Forms/Pages/default.aspx — "forms ... are available here" | Changed source to the dedicated forms page. |
| National Insurance certificates URL | ✓✓ | https://www.btl.gov.il/טפסים%20ואישורים/אישורים/Pages/default.aspx — "אישורים על זכאות לקצבאות" | https://www.btl.gov.il/טפסים%20ואישורים/Pages/default.aspx — "אישורים ניתן להדפיס בשירות אישי" | Added `bituach-leumi-certificates` source. |
| Bituach Leumi search page condition | ✓✓ | https://www.btl.gov.il/טפסים%20ואישורים/FormSearch/Pages/default.aspx — "זמנית החיפוש אינו פעיל" | https://www.btl.gov.il/טפסים%20ואישורים/forms/Pages/default.aspx — "חפש טופס ברשימה" | Documented use of category pages when search is inactive. |
| General gov.il services URL | ✗→✓ | https://www.gov.il/he/services — "שירותים ומידע" | https://www.gov.il/ — "שירותים לציבור" | Replaced singular `/he/service` with `/he/services`. |
| gov.il service count is dynamic | ✓✓ | https://www.gov.il/he/services — "שירותים ומידע. (2677)." | https://www.gov.il/he/services?subject=certificates_and_passports&subsubject=visas_for_tourist_student_volunteers — "לכל השירותים (2673)" | Avoided hard-coding service counts. |
| Corporations Authority gov.il URL | ✗→✓ | https://www.gov.il/he/departments/israeli_corporations_authority — "רשות התאגידים" | https://ica.justice.gov.il/IcaSite/ — "Israeli Corporations Authority" | Replaced older corporations landing-page URL. |
| Corporations online information boundary | ✓✓ | https://ica.justice.gov.il/ — "המידע כאמור, ניתן ללא עלות וכשירות לציבור" | https://www.gov.il/he/service/assocoations_online_information — "מידע אודות פעילות, מסמכים רשמיים" | Kept authenticated and paid filings manual. |
| Personal government area boundary | ✓✓ | https://my.gov.il/ — "הכניסה דורשת הזדהות" | https://www.btl.gov.il/טפסים%20ואישורים/tfassim-mekuvanim/Pages/default.aspx — "למלא טפסי בקשה ... ולשלוח" | Reinforced no-login and no-submission scope. |
| Hebrew official term for Tax Authority | ✓✓ | https://www.gov.il/he/departments/israel_tax_authority — "רשות המסים בישראל" | https://www.gov.il/en/departments/israel_tax_authority — "Israel Tax Authority" | Kept Hebrew as "רשות המסים". |
| Hebrew official term for National Insurance | ✓✓ | https://www.btl.gov.il/טפסים%20ואישורים/Pages/default.aspx — "הביטוח הלאומי" | https://www.btl.gov.il/English%20Homepage/Pages/default.aspx — "National Insurance Institute" | Kept English label as National Insurance Institute. |
| Webhook event names | ✓✓ | Local package grep — no webhook feature or event schema found. | Public portal model review — sources are document indexes, not webhook APIs. | Documented no webhook events apply. |

## Summary

| Total checks | ✓✓ count | ✗→✓ count | final ✗ count |
|---:|---:|---:|---:|
| 16 | 11 | 5 | 0 |
