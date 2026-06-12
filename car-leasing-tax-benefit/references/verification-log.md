# Verification Log

Access date for all rows: 01/06/2026.

| Check | Pass 1 source | Pass 2 source | Status | Package action |
|---|---|---|---|---|
| VAT rate is 18% from 01/01/2025 and still the current public rate in 2026 | Israel Tax Authority VAT history, `https://www.gov.il/he/pages/vat-history`, snippet: `1.1.25 עלה המע"מ ל-18%` | Knesset press release, `https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx`, snippet: `effective January 1, 2025` |  | Added VAT reference only; no formula dependency. |
| Official Shovi Rechev service exists and gives monthly imputed amounts by vehicle model | Israel Tax Authority service, `https://www.gov.il/he/service/itc-mm_usecar10`, snippet: `סכומי הזקיפה החודשיים של הטבת שווי השימוש ברכב צמוד` | Malam payroll points to the Tax Authority/Shaham simulator, `https://www.malam-payroll.com/.../עדכון-שווי-שימוש-ברכב-2026/`, snippet: `אתר שע"מ שכתובתו` |  | Retained simulator reference and official terminology. |
| Linear method applies to vehicles first registered from 01/01/2010 | Israel Tax Authority service, `https://www.gov.il/he/service/itc-mm_usecar10`, snippet: `נרשמו החל מ-1 בינואר 2010` | Malam payroll, `https://www.malam-payroll.com/.../עדכון-שווי-שימוש-ברכב-2026/`, snippet: `נרשמו לראשונה מיום 01.01.2010` |  | Documentation now states current/passenger-car scope more explicitly. |
| Current linear rate is 2.48% | Israel Tax Authority service, `https://www.gov.il/he/service/itc-mm_usecar10`, snippet: `כיום, שיעור השווי הוא 2.48%` | Malam payroll 2026 update, `https://www.malam-payroll.com/.../עדכון-שווי-שימוש-ברכב-2026/`, snippet: `החל משנת 2011 השיעור, הינו 2.48%` |  | Kept `base_linear_rate = 0.0248`. |
| 2026 coordinated-price ceiling is ₪596,860 | 2026 monthly deductions booklet mirror, `https://www.capitax.co.il/Attachments/13012026.pdf`, snippet: `תקרת "מחיר מתואם לצרכן" 596,860` | Malam payroll 2026 update, `https://www.malam-payroll.com/.../עדכון-שווי-שימוש-ברכב-2026/`, snippet: `תקרת מחיר מחירון ... 596,860 ₪` | → | Added `price_ceiling_ils = 596860` and changed formula to cap price before applying 2.48%. |
| 2026 hybrid reduction is ₪580 | 2026 monthly deductions booklet mirror, `https://www.capitax.co.il/Attachments/13012026.pdf`, snippet: `הפחתה משווי שימוש לרכב hybrid *580` | Regulations text, `https://he.wikisource.org/wiki/תקנות_מס_הכנסה_(שווי_השימוש_ברכב)_(הוראת_שעה)`, snippet: `בשנת 2026, 580 ש"ח` | → | Changed 2026 hybrid reduction from ₪560 to ₪580. |
| 2026 plug-in hybrid reduction is ₪1,150 | 2026 monthly deductions booklet mirror, `https://www.capitax.co.il/Attachments/13012026.pdf`, snippet: `פלאג-אין* 1,150` | Regulations text, `https://he.wikisource.org/wiki/תקנות_מס_הכנסה_(שווי_השימוש_ברכב)_(הוראת_שעה)`, snippet: `בשנת 2026, 1,150 ש"ח` | → | Changed 2026 plug-in hybrid reduction from ₪1,120/₪1,130 to ₪1,150. |
| 2026 electric reduction is ₪1,380 | 2026 monthly deductions booklet mirror, `https://www.capitax.co.il/Attachments/13012026.pdf`, snippet: `רכב חשמלי* 1,380` | Regulations text, `https://he.wikisource.org/wiki/תקנות_מס_הכנסה_(שווי_השימוש_ברכב)_(הוראת_שעה)`, snippet: `בשנת 2026, 1,380 ש"ח` | → | Changed 2026 electric reduction from ₪1,350 to ₪1,380. |
| Reduction temporary order runs through 31/12/2028 | 2026 monthly deductions booklet mirror, `https://www.capitax.co.il/Attachments/13012026.pdf`, snippet: `*הוראת שעה עד ליום 31.12.2028` | Regulations text, `https://he.wikisource.org/wiki/תקנות_מס_הכנסה_(שווי_השימוש_ברכב)_(הוראת_שעה)`, snippet: `עד יום ... (31 בדצמבר 2028)` |  | Updated notes and docs. |
| 2025 coordinated-price ceiling is ₪583,100 | 2025 annual deductions booklet, `https://www.gov.il/...yearly-deductions-booklet-2025.pdf`, snippet: `תקרת "מחיר המתואם לצרכן" - 583,100` | ICPAS 2025 payroll-tax tables, snippet: `תקרת "מחיר המתואם לצרכן" - 583,100 ₪` |  | Added 2025 `price_ceiling_ils = 583100`. |
| 2025 reductions are ₪560 / ₪1,130 / ₪1,350 | Tax Authority 2025 individual guide, `https://www.gov.il/.../Guides_IncomeTax_da-2025.pdf`, snippet: `560 ש"ח ... 1,130 ש"ח ... 1,350 ש"ח` | ICPAS 2025 payroll-tax tables, snippet: `560 ... 1,130 ... 1,350` | → | Corrected 2025 plug-in value to ₪1,130 and kept hybrid/electric values. |
| 2024 coordinated-price ceiling is ₪563,790 | 2024 monthly deductions booklet, `https://www.gov.il/...monthly-deductions-booklet-2024.pdf`, snippet: `תקרת "מחיר מתואם לצרכן" 563,790` | Protocol 2026 explainer, `https://protocol.co.il/vehicle-usage-value/`, snippet: `2024 563,790 ₪` | → | Added 2024 `price_ceiling_ils = 563790`. |
| 2024 reductions are ₪540 / ₪1,090 / ₪1,310 | Tax Authority 2024 individual guide, `https://www.gov.il/.../Guides_IncomeTax_da-2024.pdf`, snippet: `540 ש"ח ... 1,090 ש"ח ... 1,310 ש"ח` | Oketz 2024 tables, `https://www.oketz.co.il/free_files/mas25.pdf`, snippet: `פלאג ... 090 ,1 ... רכב חשמלי` | → | Corrected 2024 hybrid, plug-in, and electric values. |
| Definitions for electric, hybrid, and plug-in vehicle categories | Regulations text, `https://he.wikisource.org/wiki/תקנות_מס_הכנסה_(שווי_השימוש_ברכב)_(הוראת_שעה)`, snippet: `רכב חשמלי`, `רכב משולב מנוע`, `רכב פלאג־אין` | Israel Tax Authority service category requirements, `https://www.gov.il/he/service/itc-mm_usecar10`, snippet: `סוג כלי הרכב` |  | Updated Hebrew labels to professional terminology. |
| API hosts and endpoints | Tax Authority service, `https://www.gov.il/he/service/itc-mm_usecar10`, snippet: `למעבר למחשבון` | Public simulator host cited by payroll sources, `https://www.misim.gov.il/mm_usecar10/UseCarScreen.aspx`, snippet: `UseCarScreen.aspx` |  | References clarify that the skill is local/offline and does not call the endpoint. |
| Webhook event names | No official webhook found; skill is local/offline | Second pass searched Tax Authority service and payroll sources; no webhook interface found | final  | `api-reference.md` states no webhooks apply. |

## Summary

| Metric | Count |
|---|---:|
| Total checks | 15 |
|  double-confirmed | 8 |
| → corrected in pass 2 or correction pass | 6 |
| final  could not be confirmed by either pass | 1 |
