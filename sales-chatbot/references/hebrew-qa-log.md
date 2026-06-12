# Hebrew QA Log

## Scope

Review Hebrew public prose, chatbot replies, examples, and test phrases for Israeli business usage. Focus on neutral imperative phrasing, natural professional terminology, legal and accounting terms, price display, and date localization.

## Changes

| Area | Change | Reason |
|---|---|---|
| Date format | Changed user-facing Hebrew dates to DD/MM/YYYY, for example `03/06/2026`. | Match common Israeli date presentation and the v2 localization requirement. |
| Pricing | Kept `₪` before values and included `כולל מע״מ` when customer-facing totals are shown. | Present prices clearly for Israeli consumers and businesses. |
| Installments | Used `תשלומים`, `סך הכול`, and `תשלומים שווים` instead of transliterated payment terms. | Use natural Israeli commercial terminology. |
| Compliance wording | Used `הסכמה מפורשת`, `בקשת הסרה`, `חשבונית`, `קבלה`, `זיכוי`, and `ביטול עסקה`. | Use accurate professional terms for marketing consent, accounting, and consumer workflows. |
| Voice | Kept instructions in imperative or neutral operational wording. | Avoid first-person voice and keep operator guidance direct. |
| Technical prose | Checked for niqqud in Hebrew prose; none required for technical instructions. | Preserve professional business tone. |
| Handoff language | Used `יש להעביר לנציג שירות` and `לאסוף מספר הזמנה אם קיים`. | Keep escalation text practical and neutral. |
| Anglicisms | Retained only established product or channel names such as CRM and WhatsApp; used Hebrew terms where standard equivalents exist. | Avoid unnecessary transliteration. |

## Notes

Validate current statutory thresholds, VAT rate, provider requirements, and regulator instructions before production deployment. The package provides implementation scaffolding and operational wording, not legal advice.

## 03/06/2026 web validation pass

| Area | Change |
|---|---|
| תאריכים | נשמר פורמט ישראלי `DD/MM/YYYY`, למשל `03/06/2026` ו-`01/06/2026`. |
| מע"מ | אומת שיעור `18%` ונשמר הניסוח `כולל מע״מ` במקום תרגום מילולי. |
| חשבוניות ישראל | עודכן ניסוח מקצועי ל`מספר הקצאה`, `חשבונית מס`, `סכום העסקה לפני מע"מ`, ו`רשות המסים`. |
| מחירים לצרכן | הודגש `מחיר כולל`, `סך כל התשלומים`, `דמי משלוח`, ו`חיובים חובה`. |
| שיווק והסכמה | נשמרו המונחים `הסכמה`, `הסרה`, `הודעת סירוב`, ו`דיוור שיווקי`. |
| נגישות | נשמרה הנחיה לשפה קצרה, חלופה אנושית, ותוכן קריא. |
| קול | כל ההוראות נשמרות בלשון ציווי ניטרלית, ללא ניסוח בגוף ראשון. |
| ניקוד | לא נוסף ניקוד לטקסט הטכני; נשמרו גרשיים תקניים במע״מ בלבד. |
