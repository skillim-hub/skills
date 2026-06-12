# Hebrew QA Log

Date: 2026-06-02

## Scope

Reviewed `SKILL_HE.md`, Hebrew strings in examples, Hebrew output in the client, and Hebrew metadata. Applied corrections for professional Israeli terminology, neutral imperative phrasing, currency display, date localization, and technical clarity.

## Changes

| Area | Change |
|---|---|
| Terminology | Used `העברה בנקאית מקומית`, `מס״ב`, `זה״ב`, `תאריך ערך`, `מוטב`, `אסמכתה`, `אצווה`, `הנהלת חשבונות`, `חשבי שכר`, `אישור יוצר-בודק`, and `התאמה מול אישור הבנק`. |
| Voice | Rewrote guidance in neutral plural imperative such as `השתמשו`, `בדקו`, `אמתו`, `בחרו`, `הימנעו`, and `שמרו`. |
| Currency | Standardized examples with `₪` and clear amounts such as `₪2,450.80`, `₪50,000`, and `₪1,000,000`. |
| Dates | Standardized operator-facing Hebrew examples to `DD/MM/YYYY`, such as `03/06/2026` and `09/06/2026`. |
| Technical phrasing | Replaced informal or ambiguous phrasing with professional payment-operation wording. |
| Privacy | Added guidance to reduce unnecessary personal data in references and logs. |
| Safety | Clarified that the helper does not submit, schedule, or approve money movement. |
| Workflow | Added Hebrew equivalents for supplier, payroll, refund, rent, and tax-payment scenarios. |
| Validation | Added precise explanations for branch padding, unknown bank code, value date, high-value transfer, and production approval warnings. |
| Formatting | Verified that Hebrew technical prose contains no Hebrew combining marks. |

## Review outcome

The Hebrew guide uses natural Israeli professional terminology, neutral imperative language, ₪ amounts, and `DD/MM/YYYY` localization. It avoids unnecessary transliteration where established Hebrew terminology exists.

## V3 web-validation Hebrew corrections

| Area | Change |
|---|---|
| קודי זיהוי | תוקן קוד `9` לד.י. דואר פיננסים וקוד `54` לבנק ירושלים לפי מקור רשמי. |
| תאריך ערך | הוחלפה אזהרת סוף שבוע כללית באזהרת לוח פעילות: יום שישי או ערב חג כיום עסקים קצר, שבת וחג כיום ללא פעילות. |
| ספים פנימיים | הובהר כי ₪50,000 ו-₪1,000,000 הם ספים פנימיים הניתנים לשינוי ולא מגבלה רשמית. |
| מע״מ | הובהר ששיעור 18% משמש רק בהקשר תיעוד מס או מטרת תשלום, ולא לבדיקת ההעברה. |
| ניסוח | נשמרו ציווי ניטרלי, מינוח ישראלי מקצועי ותאריכים בפורמט DD/MM/YYYY ללא ניקוד. |
