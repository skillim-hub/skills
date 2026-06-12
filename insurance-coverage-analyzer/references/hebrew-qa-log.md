# Hebrew QA log

## Scope

Reviewed `SKILL_HE.md`, Hebrew metadata strings, and Hebrew examples in reference files for technical terminology, neutral imperative style, date and currency localization, and niqqud.

## Changes

| Area | Change |
|---|---|
| Date format | Replaced Hebrew guide date guidance with DD/MM/YYYY. |
| Currency | Kept shekel amounts with `₪` before numeric values. |
| Voice | Kept imperative phrasing such as השווה, הפק, טשטש, בדוק, בקש, דרוש. |
| Professional terminology | Used ביטוח בריאות, ביטוח דירה, ביטוח חיים, שב״ן, תקופת אכשרה, חיתום, חריגים, השתתפות עצמית, חבות מעבידים, שעבוד לבנק, מוטבים, סכום ביטוח ותת-ביטוח. |
| Anglicisms | Replaced avoidable terms with Hebrew equivalents, including כללי ההשוואה and שיטת ניקוד. |
| Niqqud | Removed Hebrew combining marks from technical prose. |
| Privacy wording | Kept local Israeli privacy terms: תעודת זהות, קודים חד-פעמיים, פרטי תשלום ומסמכים רפואיים. |
| Legal and tax boundaries | Kept references to בעל רישיון, עורך דין ורואה חשבון without presenting legal, tax, or medical advice. |

## Remaining intentional terms

| Term | Reason |
|---|---|
| שב״ן | Standard Israeli term for supplementary health-plan cover. |
| פרמיה | Standard insurance term in Israel. |
| שירותים אמבולטוריים | Common professional term in health insurance documents. |
| חיתום | Standard insurance underwriting term. |
| ביטוח חיים למשכנתה | Standard consumer-facing term. |

## Validation

- No niqqud detected.
- Public Hebrew text uses neutral professional wording.
- Dates in the Hebrew guide use DD/MM/YYYY.
- Currency examples use `₪`.

## Web-validated final pass updates - 02/06/2026

| Area | Change |
|---|---|
| מונחי רגולציה | שמר שימוש ב״רשות שוק ההון, ביטוח וחיסכון״, ״הר הביטוח״, ״שב״ן״, ״סל שירותי הבריאות״, ״ביטוח חיים למשכנתה״ ו״מוטבים״ לפי מקורות רשמיים. |
| מע״מ | הוסף ניסוח זהיר: שיעור המע״מ הכללי אומת כ-18% החל מ-01/01/2025, אך אין להסיק ממנו טיפול מס בפרמיות ביטוח. |
| תקופת אכשרה | תוקן ניסוח כך ש-90 ימים הוא סף בדיקה בדוגמה ולא כלל סטטוטורי. |
| תאריכים | נשמר פורמט DD/MM/YYYY בהדרכה העברית. |
| ניסוח | תוקנו ״אי-התאמה״ ו״צד בצד״. |
| ניקוד | לא נוסף ניקוד לטקסט המקצועי. |
