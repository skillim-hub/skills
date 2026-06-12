# Hebrew QA Log

## Scope

Review `SKILL_HE.md`, Hebrew examples in public documentation, metadata Hebrew fields, and Hebrew strings in examples. Apply natural Israeli professional terminology, neutral imperative wording, DD/MM/YYYY dates, and ₪ currency formatting.

## Changes logged

| Area | Change |
|---|---|
| Voice | Replaced conversational phrasing with neutral imperative forms such as אתר, בדוק, יצא, אמת, תעד |
| Terminology | Used מאגר מידע, משאב, מטא-נתונים, שאילתה, מסנן, רשומה, מפרסם, קידוד, גיליון אלקטרוני |
| Avoided Anglicisms | Preferred תבנית קובץ, מחסן נתונים, ייצוא, שליפה, בדיקה, סביבת הרצה where appropriate |
| Technical names | Kept CKAN, data.gov.il, CSV, JSON and UTF-8 because they are product, protocol, or file format names |
| Dates | Updated examples and guidance to DD/MM/YYYY, for example 02/06/2026 |
| Currency | Confirmed user-facing money examples use ₪, for example ₪12,345.50 |
| Nikkud | Verified no nikkud appears in technical prose |
| Privacy wording | Clarified that unnecessary personal data should not be collected or stored |
| Spreadsheet wording | Used גיליון אלקטרוני rather than transliterated spreadsheet terms |
| Error wording | Used שגיאה, הודעת שגיאה, קצב בקשות, ניסיונות חוזרים, רשומות ריקות |

## Terms used consistently

| English concept | Hebrew term used |
|---|---|
| Dataset | מאגר מידע |
| Resource | משאב |
| Metadata | מטא-נתונים |
| Query | שאילתה |
| Filter | מסנן |
| Record | רשומה |
| Publisher | מפרסם |
| Encoding | קידוד |
| Export | ייצוא |
| Data store | מחסן נתונים |
| Spreadsheet | גיליון אלקטרוני |

## Verification notes

- No nikkud was found in Hebrew technical prose.
- No decorative symbols or emoji were added.
- Command names and API actions remain in English because they are executable identifiers.
- Hebrew examples preserve exact field-name behavior expected by CKAN filters.

## Final web-validated pass - 02/06/2026

| Area | Change | Reason |
|---|---|---|
| Technical prose | Replaced `שאיל` with `בצע שאילתות` | Use natural professional Hebrew rather than a forced verb form |
| Official source validation | Added instruction to verify statutory facts such as שיעור מע"מ and ספי דיווח מול הרשות המוסמכת | Keep data analysis separate from current tax and regulatory advice |
| Environment terminology | Clarified that `sandbox` is a user-provided test endpoint | Avoid implying an official סביבת בדיקות for data.gov.il |
| Date localization | Kept DD/MM/YYYY in Hebrew guidance and used 02/06/2026 in logs | Match Israeli professional convention |
| Loanwords | Kept CKAN, data.gov.il, package_search and datastore_search only where they are executable identifiers or official names | Avoid unnecessary transliteration while preserving exact commands |
| Nikud | Verified no niqqud in public Hebrew prose | Maintain standard technical writing style |
