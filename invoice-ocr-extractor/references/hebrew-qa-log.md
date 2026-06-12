# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew examples in public documentation for Israeli professional terminology, neutral imperative style, currency notation, and date localization.

## Changes applied

- Updated public Hebrew date notation to `DD/MM/YYYY`.
- Standardized currency examples on `₪`.
- Kept accounting terms such as `חשבונית מס`, `חשבונית מס/קבלה`, `קבלה`, `חשבונית זיכוי`, `עוסק מורשה`, `עוסק פטור`, `ח.פ.`, `ע.מ.`, `מע"מ`, `סכום לפני מע"מ`, `סכום כולל`, `תור בדיקה`, and `בדיקה ידנית`.
- Replaced casual phrasing with imperative professional wording where the text describes actions.
- Avoided unnecessary English transliteration where a common Hebrew accounting term exists.
- Preserved technical identifiers such as `record_id`, `JSON`, `CLI`, and module names because they are literal interface names.
- Confirmed no Hebrew vowel marks appear in technical prose.

## Manual checks

- `₪` appears in examples and explanations.
- Date examples use `21/05/2026` style.
- Instructions avoid first-person phrasing.
- Ambiguous accounting decisions are routed to manual review rather than stated as tax advice.


## 2.2.0 web-validated Hebrew QA updates

- Added natural Hebrew wording for `מספר הקצאה`, `מס תשומות`, `סכום לפני מע"מ`, and `חשבונית מס/קבלה`.
- Preserved neutral imperative voice and avoided promotional language.
- Kept technical prose without nikud.
- Localized dates as `DD/MM/YYYY` and examples as `21/05/2026`.
- Added 2026 allocation-threshold wording: מעל ₪10,000 לפני מע"מ עד 31/05/2026 ומעל ₪5,000 מ-01/06/2026.
- Avoided implying tax advice; phrased allocation handling as `הערת בדיקה`.
