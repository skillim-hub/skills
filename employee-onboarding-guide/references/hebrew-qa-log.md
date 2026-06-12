# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew snippets in reference files, Hebrew CLI output, and Hebrew example behavior.

## Changes made

| Area | Change |
|---|---|
| Date localization | Replaced Hebrew technical prose date format with DD/MM/YYYY. |
| Example dates | Updated Hebrew examples to use values such as 01/09/2026 and 25/08/2026. |
| Currency | Kept ₪ for salary and hourly-rate examples. |
| Technical terminology | Used טופס 101, חשבות שכר, ביטוח לאומי, דמי ביטוח בריאות, תיאום מס, תיאום ביטוח לאומי, הסדר פנסיוני, קופת גמל, ביטוח מנהלים, הודעה לעובד, דיווח שעות, מניעת הטרדה מינית and אבטחת מידע. |
| Neutral voice | Reworked instructions to imperative forms such as בקש, אסוף, העבר, שמור, בדוק, הכן and סמן. |
| Anglicisms | Replaced unnecessary English loanwords where a standard Hebrew business term exists. |
| Nikud | Confirmed no Hebrew vowel marks in technical prose. |
| Gender | Used neutral operational phrasing and slash forms only in employee-facing message where necessary. |
| Professional caution | Preserved references to חשב שכר, רואה חשבון, עורך דין לדיני עבודה and בעל רישיון פנסיוני. |

## Notes

- Hebrew materials use DD/MM/YYYY, while English materials keep DD-MM-YYYY.
- CLI accepts both separators and normalizes employee-facing Hebrew output to DD/MM/YYYY.


## v2.2.0 web-validation update

| Area | Change |
|---|---|
| Form 101 | Added official 7-day submission timing and annual renewal wording. |
| Employment notice | Added 30-day timing for adult employees and 7-day timing for employees under 18. |
| Pension | Added 6-month waiting period and prior-coverage retroactive contribution timing. |
| ביטוח לאומי | Added 2026 reference amounts ₪7,703 and ₪51,910 with verification warning. |
| נוכחות | Added daily signature and manager approval rule when records are not electronic, digital, or mechanical. |
| עובדים זרים | Added ביטוח רפואי, חוזה עבודה, מגורים הולמים ומסלול פנסיה או פיקדון. |
| פרטיות | Added צמצום ניטור, אבטחת מידע והגבלת גישה. |
