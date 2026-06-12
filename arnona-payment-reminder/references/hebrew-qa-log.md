# Hebrew Quality-Assurance Log

## Scope

Review Hebrew public guidance, Hebrew examples, Hebrew output strings, and localization rules for Israeli Arnona payment reminders.

## Corrections Applied

| Area | Change |
|---|---|
| Date format | Updated Hebrew user-facing guidance and helper output to DD/MM/YYYY. |
| Currency | Preserved `₪1,234.56` formatting for clear accounting use. |
| Technical language | Preferred `רשות מקומית`, `מספר משלם/חשבון`, `מספר שובר`, `תקופת חיוב`, `מועד לתשלום`, `אישור תשלום`, `הוראת קבע`, `השגה`, `הסדר תשלומים`, and `הוצאות גבייה`. |
| Neutral voice | Kept instructions in imperative or neutral professional form. |
| Privacy wording | Kept identifiers, receipts, account references, and addresses classified as sensitive information. |
| Niqqud | Removed vowel marks from technical prose. |
| File index | Updated the Hebrew file index to point to the installable package implementation and command-line wrapper. |

## Output Conventions

- Present Hebrew dates as `DD/MM/YYYY`.
- Present money as `₪1,234.56`.
- Keep JSON dates in ISO `YYYY-MM-DD`.
- Use `תשלום ארנונה`, `שובר`, `מספר משלם/חשבון`, and `אישור תשלום` in user-facing instructions.
- Avoid transliteration when a standard Hebrew professional term exists.

## Review Notes

The Hebrew guide focuses on operational payment reminders, safe payment execution, current-balance checks, receipt retention, and escalation to the local authority when a dispute, enforcement issue, discount, exemption, objection, or installment arrangement affects payment handling.


## Version 2.2.0 Web-Validated Hebrew Changes

| Area | Change |
|---|---|
| אימות מקורות | נוספה הפניה ל-`references/verification-log.md` עם בדיקה כפולה של מקורות רשמיים. |
| מע"מ | נוסחה הבהרה בעברית: אין להוסיף מע"מ לסכום הארנונה ואין לגזור סכום לתשלום משיעור המע"מ. |
| כתובות תשלום | עודכנו פרופילי ברירת המחדל לכתובות שירות רשמיות וממוקדות יותר. |
| מונחים | נשמרו המונחים `רשות מקומית`, `צו ארנונה`, `מספר משלם`, `מספר שובר`, `הוראת קבע`, `הנחה`, `השגה` ו-`הוצאות גבייה`. |
