# Verification Log

Access date: 2026-06-02

| Check | Status | Pass 1 source | Pass 2 source |
|---|---|---|---|
| Standard VAT rate is 18% from 01/01/2025 and still current for 2026 use |  | Israel Tax Authority glossary, https://www.gov.il/en/pages/taxes-glossary. Quote: "uniform rate of 18% starting from January 1, 2025" | Knesset press release, https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx. Quote: "VAT rate will be increased ... effective January 1, 2025" |
| Israel Invoice 2026 thresholds |  | Tax Authority service page, https://www.gov.il/he/service/request-assignment-number-for-tax-invoice. Quote: "10,000 החל מה-1 בינואר 2026 ו-5,000 ₪ החל מה-1 ביוני 2026" | Govextra Tax Authority page, https://govextra.gov.il/taxes/innovation/home/israel-invoices/. Quote: "החל מה-1.6.2026 התקרה היא 5,000 ₪" |
| Allocation number condition for input VAT deduction |  | Tax Authority service page, https://www.gov.il/he/service/request-assignment-number-for-tax-invoice. Quote: "יידרשו כתנאי לניכוי מס התשומות" | Tax Authority announcement, https://www.gov.il/he/pages/pa240525-1. Quote: "ללא מספר הקצאה לא תאפשר רשות המסים לנכות את מס התשומות" |
| Tax Authority API service exists for allocation numbers |  | Tax Authority API portal, https://govextra.gov.il/taxes/innovation/home/api/. Quote: "שירות זה מאפשר לפנות לקבלת מספר הקצאה" | API document, https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/vat_software-houses-180724.pdf. Quote: "INVOICE_ID" |
| Official webhook event names for this workflow | final  | Tax Authority API portal reviewed; no webhook event names found. Quote: "שירותי ה-API של רשות המסים" | API document reviewed; allocation API fields found, no webhook event names confirmed. Quote: "מודל חשבוניות ישראל" |
| VAT-exempt dealer ceiling for 2026 |  | Tax Authority exempt-dealer opening service, https://www.gov.il/he/service/request-open-exempt-dealer-via-internet. Quote: "בשנת 2026 – 122,833 ₪" | Tax Authority small-business page, https://www.gov.il/he/departments/topics/income-tax-small-business-owner-24. Quote: "כ-122,833 ₪ בשנת 2026" |
| Consumer cancellation fee |  | Consumer Protection Authority, https://www.gov.il/he/pages/returns. Quote: "5% מערך המוצר/שירות או 100 ₪ לפי הנמוך" | Knesset regulation text, https://fs.knesset.gov.il/18/Committees/18_cs_bg_332278.doc. Quote: "5% ממחיר הטובין או מערך השירות או 100 שקלים" |
| Cash-law review trigger for business transactions |  | Tax Authority cash guide, https://www.gov.il/he/pages/law-guide-to-reducing-cash-use. Quote: "החוק קובע הגבלות" | Tax Authority 2026 circular, https://www.gov.il/BlobFolder/policy/professional-directives-090226-1/he/IncomeTax_professional-directives-090226-1.pdf. Quote: "בעסקאות הגבוהות מ. 6,000. ש\"ח" |
| Computerized accounting software control |  | Tax Authority software registry service, https://www.gov.il/he/service/itc-software-registry-for-computerized-accounting-systems. Quote: "תוכנות מסוג זה חייבות" | Tax Authority computerized bookkeeping instructions, https://www.gov.il/BlobFolder/generalpage/hor-software-other/he/IncomeTax_IncomeTaxEmployersInfo_horaot_4_01.pdf. Quote: "ספרים ותיעוד כאמור מנוהלים באמצעות מחשב" |
| Tax invoice terminology and per-transaction document logic |  | Tax Authority Israel Invoice FAQ, https://www.gov.il/he/pages/faq_israel_invoice. Quote: "חשבונית מס תוצא לגבי עסקה חייבת במס" | Israel Invoice English topic page, https://www.gov.il/en/departments/topics/israel-invoice/govil-landing-page. Quote: "allocation numbers online for tax invoices" |
| Deposit/prepayment receipt practice | → | Broad official search did not locate a deposit-specific Tax Authority page for every case. Quote: "מקדמה" search result insufficient | Professional CPA article used only as secondary practice support, https://www.eddiecpa.com/articles/מועד-הוצאת-חשבונית-מס-הטעות-שתעלה-לכם-ב/. Quote: "על כל קבלת תשלום, כולל מקדמה, יש להוציא קבלה" |
| Refundable security deposit VAT treatment | final  | No official deposit-specific blanket rule found for all industries. Quote: "פיקדון" search result insufficient | No second official blanket rule found. Package keeps conditional wording and requires accountant review. Quote: "Verify current rules" |

## Corrections applied

| Finding | Applied change |
|---|---|
| 2026 Israel Invoice threshold changes are date-specific | Added verified threshold table to `SKILL.md`, `SKILL_HE.md`, `references/api-reference.md`, and workflow controls |
| 2026 VAT-exempt ceiling is ₪122,833 | Added 2026 ceiling to guide and reference |
| Consumer cancellation fee can be stated where statutory framework applies | Added conditional 5%/₪100 language |
| Cash-law guidance needed a concrete review trigger | Added business-transaction-above-₪6,000 review caution |
| No official webhook event names found | Added explicit non-applicability statement |

## Summary

| Total checks |  double-confirmed | → corrected in pass 2 | final  |
|---:|---:|---:|---:|
| 12 | 9 | 1 | 2 |
