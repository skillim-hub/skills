# Hebrew Quality Assurance Log

## Scope

Reviewed `SKILL_HE.md` for Israeli professional terminology, neutral imperative voice, date and currency localization, and absence of vowel marks in technical prose.

## Changes

- Replaced client-oriented wording with module-oriented Hebrew where it referred to local Python use.
- Preferred Hebrew professional terms for calculation flow, payroll checks, contribution base, taxable benefit, severance component, and training fund ceilings.
- Kept established product names in common Israeli usage: קרן פנסיה, ביטוח מנהלים, קרן השתלמות, רכיב פיצויים, שכר מבוטח, שכר קובע, סעיף 14.
- Preserved `₪` notation in monetary examples.
- Changed prose date examples to `DD/MM/YYYY` style where they were not inside machine-readable data.
- Removed import-loader examples and replaced them with direct import examples.
- Confirmed that no vowel marks appear in the Hebrew technical prose.

## Review notes

- Keep English identifiers inside code blocks when they are Python names or CLI flags.
- Keep `JSON` where it names the data format.
- Reconfirm statutory ceilings and tax-year values against official publications before production payroll use.


## v1.2.0 web-validation Hebrew QA

- Added Hebrew warning for new Bituach Menahalim policies opened from 01/09/2023.
- Used professional terms: ביטוח מנהלים, קרן פנסיה מקיפה, תקרת הפקדה, שכר ממוצע, ניתוב עודף, פוליסה קיימת.
- Kept neutral imperative wording with slash forms where needed, such as בדוק/י and השתמש/י.
- Kept date format as DD/MM/YYYY and currency with ₪.
- Rechecked public Hebrew Markdown for nikud; none intentionally used in technical prose.
