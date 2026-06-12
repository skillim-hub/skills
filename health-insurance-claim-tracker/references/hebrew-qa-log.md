# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` for natural Israeli professional terminology, neutral imperative wording, date and currency localization, and removal of vocalization marks.

## Changes applied

| Area | Change |
|---|---|
| Terminology | Used ביטוח בריאות משלים, פוליסה פרטית, החזר, תביעה, דחייה, ערעור, השתתפות עצמית, תקופת אכשרה, תקרת כיסוי, ספק שבהסדר, חשבונית מס וקבלה. |
| Voice | Replaced personal phrasing with imperative plural forms such as פתחו, הוסיפו, רשמו, שמרו, בדקו, השחירו. |
| Localization | Used ₪ amounts and `DD/MM/YYYY` dates in examples. |
| Privacy language | Added השחרה, מזהה פנימי, ארבע ספרות אחרונות and access-limiting guidance. |
| Accounting language | Used הנהלת חשבונות, התאמה, חשבון בנק, עצמאי and עסק קטן. |
| Technical terms | Kept field names and command values in code formatting when they are part of the executable interface. |
| Vocalization | Confirmed that technical prose contains no Hebrew vocalization marks. |
| Anglicisms | Avoided unnecessary transliteration where Hebrew terms are common; retained command names and code identifiers only where required. |
| Gender neutrality | Used plural imperative and nouns that fit mixed audiences. |
| Consistency | Aligned status explanations with the English status model. |

## Review notes

- Command values remain in English because they are executable enum and field values.
- `portal` appears only in shell commands and examples where it represents an input value.
- Dates in Hebrew prose use `DD/MM/YYYY`.
- Currency examples use ₪.


## 1.2.0 QA updates

| Area | Change |
|---|---|
| Official terms | Added שירותי בריאות נוספים (שב"ן), הר הביטוח, חשבוניות ישראל, מספר הקצאה, מס תשומות and רשות המסים in natural Hebrew. |
| Localization | Kept ₪ and `DD/MM/YYYY`; used 01/01/2025 for verified VAT transition. |
| Voice | Maintained imperative plural voice: הפרידו, השתמשו, רשמו, שמרו, הגישו. |
| Technical clarity | Distinguished local `supplementary` and `webhook` terms from official Hebrew terminology. |
| Nikkud | Confirmed no nikkud is used in technical prose. |
