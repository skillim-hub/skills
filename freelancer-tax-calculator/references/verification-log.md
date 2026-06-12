# Web Verification Log

Access date: 2026-06-01

Status tags: `✓✓` means double-confirmed; `✗→✓` means corrected after validation; `final ✗` means not confirmed.

| Check | Status | Pass 1 source | Pass 2 source | Package action |
|---|---|---|---|---|
| Current Israeli VAT rate is 18% from 01/01/2025 and remains the package default for 2026. | ✓✓ | Israel Tax Authority glossary, https://www.gov.il/en/pages/taxes-glossary, snippet: "uniform rate of 18% starting from January 1, 2025" | OECD Economic Surveys Israel 2025, https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/04/oecd-economic-surveys-israel-2025_18e45b04/d6dd02bc-en.pdf, snippet: "After it increased to 18% in January 2025" | Kept `vat_rate = 0.18`; added explicit 2026 verification notes. |
| Israeli VAT history records the 01/01/2025 move to 18%. | ✓✓ | Tax Authority VAT history, https://www.gov.il/he/pages/vat-history, snippet: "1.1.25 עלה המע\"מ ל-18%" | Knesset press release, https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx, snippet: "effective January 1, 2025" | Kept VAT examples at 18%; no code correction needed. |
| Osek patur ceiling for 2026 is ₪122,833. | ✓✓ | Tax Authority online osek patur opening service, https://www.gov.il/he/service/request-open-exempt-dealer-via-internet, snippet: "בשנת 2026 – 122,833 ₪" | Tax Authority small-business topic page, https://www.gov.il/he/departments/topics/income-tax-small-business-owner-24, snippet: "כ-122,833 ₪ בשנת 2026" | Kept `osek_patur_threshold_annual = 122833`; added verification note. |
| Osek patur status is VAT-related and not available to all professions regardless of turnover. | ✓✓ | Tax Authority online osek patur opening service, https://www.gov.il/he/service/request-open-exempt-dealer-via-internet, snippet: "העסק אינו נמנה על העיסוקים המפורטים בתקנה 13" | VAT topic page, https://www.gov.il/he/departments/topics/value_added_tax, snippet: "מדריך לעוסק החדש - מע\"מ" | Added caution to verify registration status and occupation eligibility before relying on patur logic. |
| Small-business or micro-business route allows a 30% normative expense deduction. | ✓✓ | Tax Authority short annual report service, https://www.gov.il/he/service/report-and-payment-for-micro-business-owner, snippet: "ניכוי הוצאות של 30% מהמחזור" | Tax Authority small-business page, https://www.gov.il/he/pages/small-business-owner-income-tax, snippet: "30% מהמחזור במקום לדרוש הוצאות שהוצאו בפועל" | Kept `micro_business_normative_expense_rate = 0.30`; added verification notes. |
| Micro-business route can apply to eligible osek patur or osek murshe whose turnover is not above the patur ceiling. | ✗→✓ | Tax Authority small-business topic page, https://www.gov.il/he/departments/topics/income-tax-small-business-owner-24, snippet: "עוסק פטור או עוסק מורשה" | Tax Authority small-business page, https://www.gov.il/he/pages/small-business-owner-income-tax, snippet: "אינו עולה על 122,833 ₪" | Corrected code and tests to allow eligible low-turnover osek murshe scenarios. |
| National Insurance and health-insurance combined rates for a working-age self-employed person in 2026 are 7.70% and 18.00%. | ✗→✓ | BTL self-employed rates page, https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/rates.aspx, snippet: "סך הכול 7.7% 18%" | BTL 2026 circular, https://www.btl.gov.il/Insurance/HozrimBituah/Hozrim/_מקדמות_ודמי_ביטוח_לעצמאים_2026__.pdf, snippet: "סה\"כ 4.47% 12.83% ... דמי ביטוח בריאות ... 3.23% 5.17%" | Corrected defaults from 5.97% and 17.83% to 7.70% and 18.00%. |
| National Insurance reduced monthly base for 2026 is ₪7,703. | ✗→✓ | BTL self-employed rates page, https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/rates.aspx, snippet: "על הכנסה חודשית 7,703 ש\"ח" | BTL 2026 circular, same PDF, snippet: "בסיס לשיעור מופחת לחודש 7,703 ₪" | Corrected annual reduced threshold from ₪90,264 to ₪92,436. |
| National Insurance maximum monthly income for 2026 is ₪51,910 and annual maximum is ₪622,920. | ✗→✓ | BTL self-employed rates page, https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/rates.aspx, snippet: "עד ... 51,910 ש\"ח לחודש" | BTL 2026 circular, same PDF, snippet: "51,910 ₪ לחודש, 622,920 ₪ לשנה" | Corrected annual ceiling from ₪601,680 to ₪622,920. |
| BTL official calculation may adjust the insured base for deductible National Insurance amounts and other factors. | ✓✓ | BTL self-employed calculation example, https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/hishov.dmey.bituach.aspx, snippet: "52% מסכום דמי הביטוח הלאומי" | BTL 2026 circular, same PDF, snippet: "מטרת החוזר ... בחישוב המקדמות ובשיעורי דמי הביטוח" | Added stronger warnings that the local model is a reserve estimate, not an official assessment. |
| BTL definition of self-employed status includes hours and income tests. | ✓✓ | BTL self-employed status page, https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/default.aspx, snippet: "עוסק במשלח ידו 20 שעות בשבוע" | BTL self-employed status page, same URL, snippet: "12 שעות בשבוע ... 15% מהשכר הממוצע" | Added caution that status and mixed-income cases must be verified. |
| Income tax is collected through withholding and advances for self-employed people and companies. | ✓✓ | Tax Authority glossary, https://www.gov.il/he/pages/taxes-glossary, snippet: "תשלום מקדמות (לעצמאים ולחברות)" | Tax Authority online advance payment service, https://www.gov.il/he/service/itc-payment-online-incometax, snippet: "בעלי תיק במס הכנסה שנדרשו במקדמות" | Kept user-provided advance rate and base model; no official fixed percentage is hardcoded. |
| Micro-business advance/payment flow uses the tax coordination or short annual reporting systems rather than a public API. | ✓✓ | Tax Authority micro-business advance service, https://www.gov.il/he/service/request-down-payment-for-micro-business-owner, snippet: "להיכנס למערכת תיאומי המס" | Tax Authority short report service, https://www.gov.il/he/service/report-and-payment-for-micro-business-owner, snippet: "דיווח שנתי מקוצר" | Kept package local and deterministic; no endpoint or API client was added. |
| Official English terminology includes Value Added Tax and VAT. | ✓✓ | Tax Authority English glossary, https://www.gov.il/en/pages/taxes-glossary, snippet: "Value Added Tax" | OECD Economic Surveys Israel 2025, same PDF, snippet: "value-added tax (VAT)" | Kept English public terminology. |
| Official Hebrew terminology includes מס ערך מוסף, מע״מ, מס תשומות, and עובד עצמאי. | ✓✓ | Tax Authority Hebrew glossary, https://www.gov.il/he/pages/taxes-glossary, snippet: "מס ערך מוסף" | BTL self-employed pages, https://www.btl.gov.il/Insurance/National%20Insurance/type_list/Self_Employed/Pages/rates.aspx, snippet: "עובד עצמאי" | Kept Hebrew terminology and added BTL-specific wording. |
| Public API hosts, endpoint paths, and webhook event names. | final ✗ | No public Tax Authority or BTL API endpoint is referenced by the package. | No webhook functionality is referenced by the package or official sources used for this skill. | Recorded as not applicable. Local CLI and Python package only. |

## Summary

| Metric | Count |
|---|---:|
| Total checks | 16 |
| Double-confirmed `✓✓` | 11 |
| Corrected in pass 2 `✗→✓` | 4 |
| Final unconfirmed or not applicable `final ✗` | 1 |

## Correction details applied to v3

- Updated National Insurance and health-insurance defaults for 2026.
- Corrected the annual reduced threshold to ₪92,436.
- Corrected the annual ceiling to ₪622,920.
- Allowed eligible low-turnover osek murshe scenarios to use the 30% normative expense model.
- Strengthened documentation that the BTL calculation is an estimate and must be reconciled with official notices.
- Added source-backed defaults and caveats to English and Hebrew guides.
