# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew examples for professional Israeli terminology, neutral imperative wording, no Hebrew vowel marks, and local formatting.

## Changes completed

| Area | Change |
|---|---|
| Localization | Standardized dates to `DD/MM/YYYY` and monetary amounts to ₪ |
| Voice | Reworked guidance into imperative and neutral professional language |
| Terminology | Used `מחיר מזומן`, `סכום ממומן`, `לוח סילוקין`, `עלות אשראי`, `מקדמה`, `מעמ`, `סולק אשראי`, `הנהלת חשבונות` |
| Legal/accounting phrasing | Replaced casual phrasing with references to ביטול עסקה, החזר, חשבונית, קבלה, תיקון חשבונית והרשאת חיוב |
| Technical prose | Removed vowel marks and avoided unnecessary transliteration |
| Disclosure | Clarified that the tool supports calculation and review workflows and does not replace current legal verification |

## Result

The Hebrew guide uses natural Israeli professional wording, no vowel marks in technical prose, and consistent ₪ plus `DD/MM/YYYY` formatting.

## V3 QA additions

| Area | Change | Result |
|---|---|---|
| תאריכים | הוסף בסיס בדיקה בפורמט 02/06/2026 ו-01/01/2025 | נשמר פורמט ישראלי DD/MM/YYYY. |
| מונחי מס | הועדף מע"מ, מס תשומות, חשבונית מס ומספר הקצאה | נמנע תעתיק שאינו נחוץ. |
| צרכנות | הועדפו מחיר כולל, דמי ביטול, עסקת מכר מרחוק ואי התאמה | נשמר ניסוח מקצועי וניטרלי. |
| אשראי | הועדפו עלות האשראי, שיעור עלות ממשית וריבית פיגורים | נשמרה התאמה לשפה רגולטורית. |
| ניקוד | נסרק מסמך העברית | לא נוסף ניקוד טכני. |
