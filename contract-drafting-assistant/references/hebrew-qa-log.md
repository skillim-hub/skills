# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples in `README.md`, Hebrew examples in reference files, and generated Hebrew sample data in helper scripts.

## Changes applied

| Area | Change |
|---|---|
| Diacritics | Removed the remaining Hebrew vowel mark from technical prose. |
| Date localization | Standardized public guidance and sample dates to `DD/MM/YYYY`, including `15/07/2026` and `02/06/2026`. |
| Currency | Kept shekel formatting as `₪12,000` and `₪[סכום]`. |
| Voice | Kept guidance in imperative form: בדוק, נסח, ציין, הוסף, אל תנסח. |
| Terminology | Preserved professional Israeli terms: עוסק מורשה, חשבונית מס, קבלה, ניכוי מס במקור, מע״מ, קניין רוחני, הגנת הצרכן, תנאי מקפח, מאגר מידע, הגבלת אחריות. |
| Imports and examples | Replaced direct file loading with normal module imports. |
| Public Markdown | Confirmed no decorative icons, decorative visual references. |

## Hebrew terminology decisions

- Use `נותן השירותים` and `הלקוח` for service agreements.
- Use `מזמין השירות` when the commercial role is broader than a consumer.
- Use `צרכן` only when the customer is an individual purchasing primarily for personal, household, or family use.
- Use `תמורה` for consideration and contract price, not a casual payment label.
- Use `חשבונית מס` and `קבלה` according to the tax document context.
- Use `קניין רוחני`, `רישיון שימוש`, `המחאת זכויות`, and `זכות שימוש פנימית` instead of English loan terms.
- Use `ביטול עסקה`, `גילוי נאות`, and `הוראות צרכניות` for consumer workflows.

## Residual notes

- English terms remain only in code identifiers, command names, JSON keys, and English examples.
- Legal citations remain descriptive rather than advisory. Require professional review for regulated, high-value, privacy-heavy, employment-adjacent, real-estate, or litigation-related matters.


## v3 web-validation Hebrew changes

| Area | Change | Reason |
|---|---|---|
| פרשנות חוזה | נוסף ניסוח "מנגנון הפרשנות" ו"סדר העדיפות בין גוף ההסכם לנספחים" | התאמה לתיקון סעיף 25 לחוק החוזים משנת 2026 |
| מע״מ | נוסף "נכון ל-02/06/2026" ו"מע״מ כדין" | מניעת קיבוע שיעור מס בטקסט משפטי כאשר החוק משתנה |
| חשבוניות | נשמר "מסמך חשבונאי כדין" לצד "חשבונית מס כדין" | מתאים לסוגי עוסקים שונים ומונע דרישת מסמך שגוי |
| פרטיות | נשמרו "אבטחת מידע", "ספק משנה", "אירוע אבטחה" | מונחים מקצועיים המשמשים את הרשות להגנת הפרטיות |
| קול ניטרלי | נשמרו פעלים בציווי ניטרלי: בדוק, נסח, ציין, הוסף | שמירה על קול מקצועי ללא גוף ראשון |
