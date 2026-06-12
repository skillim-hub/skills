# Hebrew QA Log

## Scope

This log records Hebrew-language corrections and localization checks applied during the v2 correction pass.

## Corrections applied

| Area | Change | Reason |
|---|---|---|
| Technical prose | Removed Hebrew vowel marks from public technical prose. | Keep professional Israeli technical writing clean and searchable. |
| Voice and tone | Converted guidance to direct operational instructions. | Keep neutral, action-oriented language. |
| Dates | Standardized Hebrew examples to `DD/MM/YYYY`, such as `15/03/2026`. | Match Israeli usage. |
| Currency | Standardized shekel values with `₪`, such as `₪450` and `₪1,280`. | Match Israeli business documents. |
| Speaker labels | Preferred `לקוח`, `עסק`, `נציג`, `ספק`, `דובר 1`, `דובר 2`. | Improve usability for small businesses and freelancers. |
| Privacy terms | Used `טשטוש`, `ערכים רגישים`, `בסיס חוקי`, `מדיניות שמירה`, `גישה מבוקרת`. | Use clear professional terminology. |
| Command-line terminology | Used `ממשק שורת פקודה` in prose while keeping command names in code. | Avoid unnecessary English in Hebrew prose. |
| Timestamp terminology | Used `חותמת זמן` and `חותמות זמן`. | Prefer established Hebrew wording. |
| Diarization terminology | Used `זיהוי דוברים`. | Avoid unnecessary English in user-facing Hebrew guidance. |
| Sandbox terminology | Used `סביבת בדיקה` in prose and kept `sandbox` only in commands. | Preserve technical command correctness and Hebrew clarity. |
| Production terminology | Used `סביבת ייצור`. | Match Israeli professional usage. |
| Accounting context | Used `חשבונית`, `סכום`, `חיוב`, `החזר`, `מספר הזמנה`. | Match small-business workflows. |
| Legal and privacy context | Used `הסכמה`, `בסיס חוקי`, `הקלטת שיחה`, `צמצום שמירה`. | Keep privacy guidance precise. |

## QA checks completed

| Check | Result |
|---|---|
| No Hebrew vowel marks in public Markdown prose | Passed |
| No pictographic symbols in public Markdown | Passed |
| Currency examples use `₪` | Passed |
| Hebrew date examples use `DD/MM/YYYY` | Passed |
| Hebrew guide uses natural Israeli phrasing | Passed |
| Code blocks keep command names unchanged | Passed |
| Examples keep JSON output readable with Hebrew text | Passed |

## Terms approved for this package

| English concept | Hebrew term in prose |
|---|---|
| Transcription | תמלול |
| Transcript | תמלול או טקסט מתומלל, לפי ההקשר |
| Timestamp | חותמת זמן |
| Speaker labels | תוויות דוברים |
| Diarization | זיהוי דוברים |
| Redaction | טשטוש |
| Sensitive values | ערכים רגישים |
| Command line interface | ממשק שורת פקודה |
| Sandbox | סביבת בדיקה |
| Production | סביבת ייצור |
| Provider | ספק |
| Retention policy | מדיניות שמירה |

## Version 2.2.0 web-validation changes

| Area | Change | Reason |
|---|---|---|
| מע"מ | נוסף ניסוח שמורה לבדוק שיעור רשמי לפני חישוב, עם אימות 18% מ-01/01/2025. | מניעת חישוב מס שגוי מתוך תמלול לא מאומת. |
| וואטסאפ | נוסף ניסוח מקצועי על OGG בקידוד OPUS בהודעות קוליות יוצאות. | התאמה למונחי פלטפורמת וואטסאפ לעסקים ולמניעת המרות לא מתאימות. |
| פרטיות | הובהרו מונחי `בעל שליטה במאגר מידע`, `מחזיק`, `מנהל מאגר`, `מידע אישי` ו-`מידע בעל רגישות מיוחדת`. | התאמה לתיקון 13 ולשפה המקצועית בישראל. |
| נגישות | נשמר המונח `כתוביות` ונוספה הבחנה מול `תמלול` או `פרוטוקול` לפי הקשר השירות. | התאמה לשימוש מקצועי בישראל בלי אנגליזמים. |

בדיקות לשון חוזרות: לא נמצא ניקוד במדריכים הציבוריים; נשמר סגנון ציווי ניטרלי; נשמרו תאריכים בפורמט `DD/MM/YYYY` וסכומים עם `₪`.
