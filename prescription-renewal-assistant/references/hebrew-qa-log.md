# Hebrew QA Log

## Scope

Reviewed public Hebrew documentation for terminology, voice, localization, and formatting.

## Changes made

| Area | Change |
|---|---|
| Date localization | Replaced Hebrew-facing `DD-MM-YYYY` guidance with `DD/MM/YYYY`. |
| Currency | Kept amounts and references in ₪. |
| Voice | Rewrote instructions in neutral imperative form, such as `אסוף`, `בדוק`, `אמת`, `פעל`, `תעד`. |
| Terminology | Used professional Israeli wording such as `קופת חולים`, `מרשם`, `ניפוק`, `רוקח`, `מוקד`, `אישור`, `שרשרת קירור`, `מטפל`, `אפוטרופוס`. |
| Anglicisms | Replaced unnecessary foreign terms where Hebrew terms are natural, for example `יישומון` where appropriate and `צאט` only for common workplace messaging context. |
| Privacy language | Clarified `מידע רפואי רגיש`, `הסכמה`, `הרשאה רשמית`, and `פרטי תשלום`. |
| Safety | Preserved clear wording that the skill does not diagnose, prescribe, change dosage, or replace clinical advice. |
| Nikud | Removed vowel marks from technical prose. |
| Gender | Used neutral professional imperative phrasing where possible and avoided addressing a specific gendered user role. |
| Public Markdown | Confirmed no emoji were introduced. |

## Notes

The Python helper accepts both `DD-MM-YYYY` and `DD/MM/YYYY` input for dates. English documentation continues to use `DD-MM-YYYY`; Hebrew documentation uses `DD/MM/YYYY`.


## Final web-validation Hebrew terminology changes

| Area | Change |
|---|---|
| Be | Added Hebrew instruction to verify support in the current app, branch, or with a pharmacist. |
| ניו-פארם | Added Hebrew caveat that current Israeli prescription-delivery support was not confirmed. |
| מע״מ | Added 18% reference for 2026 as a financial note, not as an automatic calculation rule. |
| ממשקי תכנות | Added Hebrew wording that public API routes and webhook event names were not confirmed. |
