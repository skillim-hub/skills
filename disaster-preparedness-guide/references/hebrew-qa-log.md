# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew references in public Markdown for technical prose quality, localization, neutral imperative voice, and Israel-specific terminology.

## Changes made

| Area | Change |
|---|---|
| Version | Updated Hebrew front matter to `2.0.1`. |
| Date format | Replaced hyphen-separated examples with `04/06/2026` and DD/MM/YYYY localization. |
| Currency | Kept ₪ for Hebrew financial examples and used `ב-₪` where a Hebrew sentence requires a prefix. |
| Technical prose | Removed nikud from Hebrew technical prose; retained standard punctuation such as geresh and gershayim in abbreviations. |
| Voice | Preserved neutral imperative phrasing such as `להיכנס`, `לסגור`, `להמתין`, `לתעד`, and avoided first-person language. |
| Terminology | Replaced unnecessary Anglicisms with Hebrew terms: `פרילנסרים` to `נותני שירות עצמאיים`, `קליניקה` to `מרפאה`, `Cell Broadcast` to `התרעת חירום סלולרית`, `מערכת POS` to `מערכת קופה ממוחשבת`, and `PTSD` to `פוסט טראומה`. |
| Emergency terms | Preserved accepted Israeli terms and abbreviations: ממ״ד, ממ״ק, מקלט, פיקוד העורף, מד״א, ער״ן, מוקד 106, כבאות והצלה. |
| Accounting/legal wording | Preserved professional terms: חשבונית מס, קבלה, דוחות מע״מ, מסמכי הנהלת חשבונות, פוליסת ביטוח, רישיון עסק, רואה חשבון. |
| Safety precision | Kept distinctions between ירי רקטות, רעידת אדמה, חומרים מסוכנים, אירוע רדיולוגי, צונאמי וחדירת מחבלים. |
| Accessibility | Preserved natural Israeli terminology: נגישות, מוגבלות בניידות, לקות שמיעה, לקות ראייה, כיסא גלגלים, מלווה נגישות. |

## QA checks

- No Hebrew nikud code points were found in public Markdown after correction.
- No first-person instructional voice was introduced.
- No Hebrew date examples use hyphen-separated DD-MM-YYYY after correction.
- No unnecessary transliteration remains where a standard Hebrew professional term was appropriate.
- Official-instructions override remains explicit.


## Version 2.1.0 web-validation corrections

| Area | Change |
|---|---|
| חדירת כלי טיס עוין | עודכן לנוסח מאומת: המתנה 10 דקות לפחות, אלא אם התקבלה התרעה נוספת או הנחיה מפורשת אחרת. |
| אירוע רדיולוגי | צומצמו הנחיות פעולה מפורטות שלא נמצאה להן אסמכתה ציבורית ישראלית כפולה; נשארה הנחיה לפעול לפי גורמי החירום והרפואה בלבד. |
| מע״מ | נשמר פורמט מקומי DD/MM/YYYY ונוספה הפניה ביומן האימות לכך ששיעור המע״מ הכללי אומת כ-18% החל מ-01/01/2025. |
