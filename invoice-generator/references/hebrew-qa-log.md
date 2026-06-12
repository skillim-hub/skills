# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples, rendered document terminology, and Hebrew field labels. Focused on natural Israeli professional phrasing, accounting terminology, neutral imperative voice, and localization.

## Changes applied

| Area | Change |
|---|---|
| Dates | Standardized Hebrew-facing dates to `DD/MM/YYYY`. |
| Currency | Used ₪ for shekel examples and totals. |
| Document names | Used חשבונית מס, קבלה, חשבונית מס/קבלה וחשבונית זיכוי. |
| Issuer status | Used עוסק מורשה, עוסק פטור וחברה בע״מ in rendered output. |
| Allocation terminology | Used מספר הקצאה consistently. |
| VAT terminology | Used מע״מ and סכום לפני מע״מ consistently. |
| Credit workflow | Used חשבונית זיכוי, מסמך מקור וסיבת הזיכוי. |
| Payment terminology | Used אמצעי תשלום, אסמכתה, העברה בנקאית, כרטיס אשראי, שיק, ביט ופייבוקס. |
| Voice | Rewrote guidance as direct instructions without first-person phrasing. |
| Nikkud | Confirmed technical prose does not use nikkud. |
| Anglicisms | Replaced unnecessary English accounting terms with Hebrew terms where practical; kept code identifiers and CLI commands as code. |

## Remaining intentional English

- JSON field names remain in English because they are the package interface.
- CLI commands and Python imports remain in English because they are executable identifiers.
- Currency codes such as `ILS` and `USD` remain standard machine-readable values.

## [2.2.0] - Web validation pass on 01/06/2026

- הוחלף הניסוח "מגיע לסף" ב-"עולה על הסף" כדי להתאים ללשון המקורות הרשמיים.
- עודכן הסף לשנת 2026: ₪10,000.00 מ-01/01/2026 עד 31/05/2026, ו-₪5,000.00 מ-01/06/2026 ואילך.
- נוסף הסבר שהסף חל לפי תאריך המסמך ולא לפי השנה בלבד.
- נוסף הסבר שעסקה בשיעור אפס או עסקה פטורה אינה מפעילה בדיקת מספר הקצאה בכלי זה.
- נשמרו מונחים מקצועיים בעברית: חשבונית מס, חשבונית מס/קבלה, חשבונית זיכוי, קבלה, עוסק מורשה, עוסק פטור, מספר הקצאה, מס תשומות.
- נשמר פורמט סכומים בשקלים עם סימן ₪ ופורמט תאריכים `DD/MM/YYYY` בכל הדוגמאות הציבוריות.
- לא נוסף ניקוד לטקסט הטכני.
- נשמרה לשון ציווי ניטרלית בלי פנייה מגדרית ישירה.
