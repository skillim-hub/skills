# Hebrew QA Log

## Scope

Review date: 02/06/2026

Reviewed Hebrew public content in `SKILL_HE.md`, Hebrew metadata strings, and Hebrew examples appearing in project documentation.

## Changes completed

| Area | Change |
|---|---|
| Technical prose | Removed vowel points and kept standard unpointed Hebrew. |
| Voice | Converted guidance to neutral imperative wording. |
| Localization | Set Hebrew dates to DD/MM/YYYY format. |
| Currency | Used ₪ for Israeli monetary examples. |
| Terminology | Replaced casual or English-heavy terms with professional Hebrew terms. |
| Production language | Replaced foreign phrasing with "סביבת ייצור". |
| Data language | Used "מידע", "מידע אישי", "מידע רגיש" and "נושאי מידע". |
| Processor language | Used "ספק עיבוד" and "ספקי משנה". |
| Controller language | Used "בעל שליטה" where context fits. |
| Security language | Used "אבטחת מידע", "תיעוד גישה", "הרשאות" and "סקר סיכונים". |
| Rights language | Used "זכויות עיון, תיקון, מחיקה, התנגדות והסרה מדיוור". |
| Transfer language | Used "העברה לחוץ לארץ" and "העברות המשך". |
| Cloud service language | Used "שירות תוכנה בענן" rather than casual foreign phrasing. |
| CLI description | Used "כלי שורת הפקודה" in prose. |

## Terminology decisions

| Concept | Preferred Hebrew |
|---|---|
| Compliance | ציות |
| Data | מידע |
| Personal data | מידע אישי |
| Sensitive data | מידע רגיש |
| Data subject | נושא מידע |
| Data controller | בעל שליטה |
| Processor | ספק עיבוד |
| Subprocessor | ספק משנה |
| Production | סביבת ייצור |
| Validation | בדיקה או אימות |
| Security | אבטחת מידע |
| Deployment | הפעלה או הטמעה |
| Direct marketing | דיוור ישיר |
| Retention | שמירה |
| Deletion | מחיקה |
| Cross-border transfer | העברה לחוץ לארץ |

## Remaining legal caution

Keep final legal determinations outside the tool when the matter involves רישום או הודעה לרשות, מידע רפואי, קטינים, מידע ביומטרי, נתוני אשראי, ניטור עובדים, גוף ציבורי, אירוע אבטחה משמעותי או העברה מורכבת לחוץ לארץ.

## Web-validated v3 QA update

- החליפו את הביטוי הכללי "מידע רגיש" במקומות מרכזיים ל"מידע בעל רגישות מיוחדת" כאשר ההקשר הוא תיקון 13 או תקנות אבטחת מידע.
- תיקנו את רמת האבטחה: 10,000 בני אדם ו-10 בעלי הרשאה אינם טריגר כללי לרמת אבטחה בינונית.
- תיקנו את סף רמת האבטחה הגבוהה ל-100,000 בני אדם ומעלה או יותר מ-100 בעלי הרשאה כאשר המאגר כבר ברמה בינונית.
- הוסיפו הבחנה מקצועית בין רמת אבטחה סטטוטורית לבין חומרה תפעולית בקליניקה פרטית.
- שמרו על לשון ציווי ניטרלית ועל תאריכים בפורמט DD/MM/YYYY בהנחיות בעברית.
