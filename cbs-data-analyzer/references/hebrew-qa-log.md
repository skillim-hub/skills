# יומן בקרת איכות עברית

## מטרת הבדיקה

לוודא שהמדריך העברי והקטעים העבריים בחומרי העזר כתובים בעברית מקצועית, טבעית ושימושית לעסקים קטנים, עצמאים וצרכנים בישראל.

## שינויים שבוצעו

| תחום | שינוי | סיבה |
|---|---|---|
| פורמט תאריך | עודכן ל-`DD/MM/YYYY` | התאמה לשימוש ישראלי נפוץ במסמכים כספיים וצרכניים. |
| מינוח טכני | הוחלף ניסוח כללי של ממשקים לניסוח "ממשק מדדי המחירים" או "ממשק הלמ״ס" | צמצום אנגליזמים ושמירה על ניסוח מקצועי. |
| מונחי מס | הוחלף ניסוח שגוי ל"מיסויי" או "ענייני מס" לפי ההקשר | דיוק מקצועי בתחום כספי וצרכני. |
| תשלומים לעצמאים | הוחלף שימוש עודף במונח לועזי בתיאור "תשלום חודשי קבוע" | ניסוח טבעי וברור לקהל ישראלי. |
| נתוני מקור | הוחלף מונח לועזי במונח עברי ברור | התאמה לשפה מקצועית במסמכי נתונים. |
| רשימת בדיקה | נמחק סעיף כפול על תקופות ייחוס | מניעת חזרתיות. |
| ניקוד | נבדק שאין ניקוד בטקסט הטכני | שמירה על כתיבה עסקית רגילה. |
| קול וסגנון | נשמר קול ניטרלי בציווי: זהה, בחר, שלוף, נרמל, חשב, ציין | התאמה להנחיות ההפעלה של המיומנות. |

## החלטות מינוח

| מונח מועדף | שימוש |
|---|---|
| הלשכה המרכזית לסטטיסטיקה | שם רשמי בהופעה ראשונה או בהקשר פורמלי. |
| הלמ״ס | קיצור מקובל לאחר ההופעה הראשונה. |
| מדד המחירים לצרכן | שם המדד לצרכים חוזיים וצרכניים. |
| הצמדה למדד | חישוב סכום לפי יחס בין מדד יעד למדד בסיס. |
| תקופת ייחוס | החודש, הרבעון או השנה שאליהם הנתון מתייחס. |
| ממשק נתונים | נקודת גישה ממוחשבת לנתונים. |
| נתוני מקור | מידע גולמי או תיאור מאגר שנדרש לאימות. |
| תשלום חודשי קבוע | תיאור ברור לתשלום שירות מתמשך. |

## תוצאת הבדיקה

הטקסט העברי עומד בדרישות: ללא ניקוד בטקסט הטכני, עם מונחים מקצועיים ישראליים, עם פורמט תאריך `DD/MM/YYYY`, עם סימון שקל `₪`, ובקול ניטרלי שאינו משתמש בגוף ראשון.

## v2.2.0 web-validated pass - 02/06/2026

| Area | Change | Reason |
|---|---|---|
| CBS API wording | Replaced default use of code `120010` with a requirement to verify it in the live catalog. | Avoid treating a documented example as a permanent uncontrolled assumption. |
| API headers | Added instruction to send a `User-Agent` header when using the CBS API. | CBS API guidance states that this header is mandatory. |
| VAT wording | Added a dated statement that the v3 verification log confirms `18%` VAT in 2026, with a requirement to recheck before tax guidance. | Keep the skill useful while avoiding stale tax conclusions. |
| Troubleshooting | Added `download=false` and `User-Agent` to JSON troubleshooting guidance. | Reflect the live CBS API documentation. |
| Hebrew terminology | Kept professional terms: הלשכה המרכזית לסטטיסטיקה, מדד המחירים לצרכן, הצמדה למדד, מע״מ, כותרת בקשה, תקופת ייחוס. | Use accepted Israeli professional language rather than informal transliteration. |
| Localization | Retained `₪` and `DD/MM/YYYY` guidance for Israeli-facing output. | Match Israeli consumer and small-business usage. |
