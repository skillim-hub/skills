# Hebrew QA Log

QA date: 2026-06-01

## Scope

Reviewed `SKILL_HE.md` and Hebrew-facing terminology in references, metadata, field labels, and examples.

## Terminology decisions

| Concept | Preferred Hebrew | Notes |
|---|---|---|
| Israel Tax Authority | רשות המסים | Use the official Hebrew term. |
| Annual return | דוח שנתי | Avoid transliteration. |
| Short salaried refund return | דוח שנתי מקוצר | Use in Form 135 guidance. |
| Withholding at source | ניכוי במקור | Use consistently for Form 856 and payroll withholding. |
| Tax credits | נקודות זיכוי | Use where personal credits are discussed. |
| Trial balance | מאזן בוחן | Use in Form 6111 workflows. |
| Ledger card | כרטסת | Use in supplier and bookkeeping workflows. |
| Authorized representative | מייצג | Use for CPA or tax representative workflow extensions. |
| Standardized financial statement | דוח כספי אחיד | Use for Form 6111. |
| National Insurance | ביטוח לאומי | Use the accepted institutional term. |

## Localization changes

- Kept all currency examples in ₪ format, for example `₪12,345`.
- Updated Hebrew date examples to `DD/MM/YYYY`.
- Replaced hyphenated date examples with slash-separated Israeli date examples.
- Kept technical examples free of nikud.

## Voice and style changes

- Kept imperative professional wording.
- Avoided first-person phrasing.
- Avoided unnecessary English terms when a standard Hebrew professional term exists.
- Kept cautionary language practical: verify official instructions, reconcile records, redact personal data.

## Validation notes

- No nikud marks were found in Hebrew technical prose.
- Hebrew field labels in the Python helper match professional usage for the covered forms.
- Mixed Hebrew-English usage remains only where form numbers, code identifiers, or command names require it.

## Final web-validation QA update - 01/06/2026

- עדכנו את מועד טופס 1301 לשנת המס 2025: 29/05/2026 להגשה שאינה מקוונת ו-30/06/2026 להגשה מקוונת.
- עדכנו את מועד טפסים 126 ו-856 לשנת המס 2025 ל-31/05/2026, עם הערה לאימות תנאי אישור מקוון.
- החלפנו ניסוח כללי על ארכות מייצגים בניסוח זהיר שמחייב לוח ארכות רשמי ומאומת.
- חיזקנו מונחים מקצועיים: `דוח ליחיד`, `דין וחשבון מקוצר`, `ניכויים מתשלומים שאינם משכורת או שכר עבודה`, `נספח לדוח השנתי`.
- שמרנו על כתיב טכני ללא ניקוד, לשון ציווי נייטרלית, סימון ₪ ותאריכים בפורמט DD/MM/YYYY.
