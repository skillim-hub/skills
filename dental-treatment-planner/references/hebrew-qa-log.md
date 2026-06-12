# Hebrew QA log

## Scope

Reviewed `SKILL_HE.md` and Hebrew-facing descriptions in metadata for Israeli professional usage, local currency display, date format, and neutral imperative wording.

## Changes made

| Area | Change |
|---|---|
| Currency | Replaced informal shekel wording with `₪` where the guide describes cost outputs. |
| Dates | Standardized local-facing examples to `DD/MM/YYYY`, such as `15/07/2026`. |
| Medical wording | Replaced loan wording for urgent intake with `מיון קליני ראשוני`. |
| Tone | Kept neutral imperative phrasing such as `הפיקו`, `בדקו`, `סמנו`, and `הימנעו`. |
| Technical prose | Confirmed no Hebrew niqqud marks are used. |
| Professional boundaries | Preserved clear separation between planning, clinical diagnosis, insurance eligibility, and tax/accounting review. |

## Terminology decisions

| Term | Preferred Hebrew usage |
|---|---|
| estimate | אומדן |
| treatment plan | תוכנית טיפולים |
| clinical triage | מיון קליני ראשוני |
| supplementary insurance | שב״ן |
| deductible or self pay balance | השתתפות עצמית / תשלום עצמי |
| annual cap | תקרה שנתית |
| waiting period | תקופת אכשרה |
| VAT | מע״מ |
| invoice and receipt | חשבונית וקבלה |
| licensed dentist | רופא שיניים מורשה |

## Remaining intentional English

Treatment codes, provider identifiers, CLI flags, JSON keys, and Python module names remain in English because they are machine-readable identifiers. Hebrew prose explains their meaning where relevant.

## Web-validation corrections

| Area | Change |
|---|---|
| מע״מ | עדכנו את נוסח ברירת המחדל ל־18% בעקבות אימות מקורות לשנים 2025-2026. |
| זכאות ילדים | ניסחו מחדש לפי מונחי משרד הבריאות: `טיפולי שיניים מונעים`, `טיפולים משמרים`, `השתתפות עצמית נמוכה`, `מרפאות השיניים של קופות החולים`. |
| בני 72 ומעלה | הוסיפו ניסוח זהיר על טיפולים מונעים, משמרים וחלק מהטיפולים המשקמים דרך הקופות. |
| מכבידנט וכללית סמייל | הדגישו שמחירי קופה הם לפי פריט, גיל ותוכנית, ולא אחוז אחיד. |
| API | החליפו רושם של נקודת קצה חיצונית בניסוח `חוזה מקומי` ו־`לא כנקודת קצה חיצונית`. |
| ניקוד | נבדק שאין ניקוד בטקסט הטכני. |
| קול ניטרלי | נשמרו פעלים בציווי רבים או ניסוח בלתי אישי, ללא גוף ראשון. |
