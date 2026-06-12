# Hebrew QA Log

Audit date: 04/06/2026.

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples, customer-facing teacher message output, and Hebrew terminology in references and scripts.

## Changes applied

| Area | Correction |
| --- | --- |
| Tone | Rewritten to neutral imperative voice suitable for office procedures. |
| Dates | Customer-facing dates use DD/MM/YYYY, for example 31/08/2026. |
| Currency | Fees and receipts refer to ₪ and separate official fee from private service fee. |
| Government terminology | Used משרד הרישוי, משרד התחבורה והבטיחות בדרכים, חידוש רישיון נהיגה, תור, הצהרה רפואית, אגרה, קבלה, מספר אישור. |
| Technical terminology | Used ממשק תכנות where needed and שורת פקודה for command-line instructions in prose. |
| Privacy wording | Used מידע אישי, הסכמת לקוח, תקופת שמירה, and צורך תפעולי. |
| Gendered verbs | Preferred neutral imperative forms such as בדוק, ודא, שמור, הכן, שלח. |
| Nikkud | Removed vowel marks from technical prose. |
| Anglicisms | Replaced unnecessary foreign terms with accepted Hebrew terms, except fixed command values such as `sandbox` and `production`. |

## Remaining intentional terms

- `sandbox` and `production` remain as command values because the CLI requires these exact options.
- License classes such as B, C1, A1 remain as official class notation.
- Python identifiers remain in English because they are executable code.


## v3 web-validation terminology changes

| Area | Change |
| --- | --- |
| Appointment host | Replaced deprecated appointment wording with GoVisit and שירות זימון תורים של משרד התחבורה. |
| Practical test | Clarified that a practical driving test is coordinated through מורה נהיגה or בית ספר לנהיגה, not directly booked by the local package. |
| Payment routes | Added רישיון נהיגה for `/voucherspa/input/209` and אגרת מבחן נהיגה for `/voucherspa/input/427`; removed any implication that a vehicle-license payment route is for driver-license renewal. |
| VAT | Added מע״מ guidance for private service fees with 18% as the rate validated on 04/06/2026. |
| Voice | Kept neutral imperative wording: השתמש, פעל, ודא, שמור, תאם, אל תציג. |
| Dates and currency | Kept customer-facing dates as DD/MM/YYYY and amounts in ₪. |
