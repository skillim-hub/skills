# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew metadata fields, Hebrew README references, and Hebrew terms in examples.

## Changes made

| Area | Change |
|---|---|
| Technical prose | Removed nikud from Hebrew prose |
| Voice | Reworded guidance into neutral imperative phrasing |
| Currency | Standardized monetary references to ₪ |
| Date style | Standardized Hebrew-facing date guidance to DD/MM/YYYY |
| Tax terminology | Used מעמ, מס הכנסה, דמי ביטוח לאומי, מס רווח הון, מקדמות מס |
| Savings terminology | Used פיקדון בנקאי, קרן כספית, קרן השתלמות, קופת גמל להשקעה, קרן פנסיה |
| Risk terminology | Used תנודתיות, נזילות, אופק, זכאות, תקרות, דמי ניהול |
| Retirement terminology | Used פער פרישה, גיל פרישה, תוחלת חיים, תשואה ריאלית |
| Anglicisms | Avoided unnecessary transliteration where standard Hebrew terms exist |
| Command terms | Kept command names, Python identifiers, and JSON keys in English code blocks |

## Review notes

- Keep `JSON`, command names, package names, and code identifiers in English.
- Use `פרילנסרים` only when addressing the common Israeli business segment; use `עצמאים` when the legal or tax context matters.
- Use `ממשק שורת פקודה` in prose instead of `CLI`.
- Use `סביבה` for `environment`; keep `sandbox` and `production` as command values.
- Use `בדיקת רגישות` for stress testing in Hebrew prose.
- Use `תזרים` rather than cash-flow transliteration.

## Validation checks

| Check | Result |
|---|---|
| Nikud removed from technical prose | Passed |
| ₪ used for currency | Passed |
| DD/MM/YYYY used in Hebrew-facing date guidance | Passed |
| Neutral imperative style applied | Passed |
| Professional Israeli terms used | Passed |
| Code identifiers preserved | Passed |


## אימות אינטרנטי 02/06/2026

| תחום | שינוי |
|---|---|
| מעמ | הושאר המונח מעמ והוסף אימות שיעור 18% נכון ל-02/06/2026 |
| קצבה | הוחלף ניסוח מסוג state pension בניסוח הכנסה צפויה מקצבה או גמלה |
| קופת גמל להשקעה | תוקנה תקרת 2026 ל-₪83,641 במקום שימוש בתקרת 2025 |
| תאריכים | נשמר פורמט DD/MM/YYYY במסמכים בעברית |
| קול מקצועי | נשמר גוף ציווי ניטרלי ללא פנייה מגדרית מיותרת |
