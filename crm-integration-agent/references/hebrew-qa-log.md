# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples in public documentation, JSON examples, and user-facing CLI examples.

## Changes made

| Area | Correction |
|---|---|
| Voice | Rewrote guidance in neutral imperative form. |
| Professional terminology | Used `מערכת ניהול לקוחות`, `רשומת לקוח`, `רשומת מתעניין`, `דיוור שיווקי`, `הסכמה מפורשת`, `תיעוד פעולות`, `הרשאות`, `צמצום מידע`, `חשבונית מס`, and `קבלה`. |
| Dates | Standardized localized dates to DD/MM/YYYY, for example `18/02/2026`. |
| Currency | Used ₪ in examples, for example `₪2,500`. |
| Sensitive data | Used natural Israeli phrasing for תעודת זהות, כרטיס תשלום, קוד אימות, ומידע אישי. |
| Marketing consent | Distinguished between פנייה שירותית and הסכמה לדיוור שיווקי. |
| Opt-out | Included practical Israeli terms such as `הסר` and `בטל`. |
| Nikkud | Confirmed that technical prose contains no vowel marks. |
| Anglicisms | Replaced unnecessary loanwords with Hebrew terms where a standard term exists. |
| Gender | Used forms that avoid unnecessary gender marking where possible; examples include feminine and masculine consent phrases. |

## Final status

Hebrew text is suitable for Israeli professional users and uses localized dates, currency, and business terminology.


## 1.3.0 web-validation pass

| Area | Change |
|---|---|
| מע"מ | שמר ניסוח מקצועי: שיעור המע"מ 18% החל מ-01/01/2025; הבהר שאין לחשב מס מתוך המיומנות. |
| ממשקים | הוסיף בעברית נתיבי `2026-03` ו-`v67.0` בלי תעתיק מיותר. |
| פרטיות | שמר על המונחים מידע אישי, מאגר מידע, בעל שליטה במאגר, הסכמה, דיוור ישיר ומסרון. |
| תאריכים ומטבע | שמר פורמט DD/MM/YYYY וסימן ₪ בדוגמאות. |
| ניקוד | בדק שאין ניקוד בטקסט המקצועי. |
