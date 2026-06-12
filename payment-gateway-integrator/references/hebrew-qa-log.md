# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew metadata for technical phrasing, local terminology, date and currency conventions, and neutral imperative voice.

## Changes

| Area | Change |
|---|---|
| Date localization | Replaced dash-based examples with `DD/MM/YYYY`. |
| Currency localization | Kept amounts in `₪` format and agorot as integer storage units. |
| Callback terminology | Replaced transliterated callback phrasing with `קריאה חוזרת` and `קריאות חוזרות`. |
| Token terminology | Replaced informal token phrasing with `אסימון` and `אסימונים` where the prose discusses stored payment references. |
| Idempotency wording | Replaced foreign-derived prose with `מניעת כפילות` and `הגן מפני כפילות`. |
| Timeout wording | Replaced English-derived phrasing with `חריגת זמן` and corrected gender agreement. |
| Back-office wording | Replaced foreign-derived prose with `תפעול אחורי`. |
| Production wording | Replaced foreign-derived prose with `סביבת אמת`. |
| CLI wording | Replaced foreign-derived prose with `כלי שורת פקודה`. |
| Voice | Kept instructions in neutral imperative form without first-person wording. |
| Nikud | No nikud was found in technical prose. |
| Gender agreement | Corrected phrasing such as `קריאה חוזרת חתומה` and `חריגת זמן מקומית`. |

## Final status

Hebrew prose uses natural Israeli professional terminology, neutral imperative wording, `₪` amounts, and `DD/MM/YYYY` date localization.


## 02/06/2026 final web validation pass

| Area | Change | Rationale |
|---|---|---|
| מעמ | הוסר גרשיים מיושנים והוגדר שיעור 18% לשנת 2026. | ניסוח מקצועי וללא ניקוד, בהתאם למקורות רשות המסים. |
| Grow/Meshulam | נוסח `Grow (לשעבר Meshulam)` במקום הצגת Meshulam כספק חי נפרד. | התאמה לתיעוד העדכני של Grow ולמסמך בנק ישראל. |
| קריאות חוזרות | הוחלף ניסוח של שמות אירוע אחידים בהנחיה לנרמול מצבים פנימיים. | ספקים שונים מתעדים שדות ותהליכים שונים. |
| מונחי תשלום | נשמרו `דף סליקה`, `אסימון תשלום`, `החזר`, `ביטול`, `התאמה`, `אשראית EMV`. | מונחים מקובלים בשוק הישראלי ללא תעתיק מיותר. |
| תאריכים וסכומים | נשמר פורמט `DD/MM/YYYY` וסימן `₪`. | התאמה מקומית לקוראים בישראל. |
