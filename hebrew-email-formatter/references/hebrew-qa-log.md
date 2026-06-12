# Hebrew QA Log

## Localization changes

- Changed all public examples from dash-separated dates to `DD/MM/YYYY`.
- Updated metadata localization to `DD/MM/YYYY`.
- Kept Israeli currency formatting with `₪`.
- Replaced date examples with `31/12/2026`, `01/05/2026`, `31/05/2026`, and similar local forms.

## Language changes

- Removed dotted Hebrew characters from public technical prose.
- Replaced vague timing with `מועד יעד`, `תאריך פירעון`, and `יום עסקים`.
- Replaced awkward translated structures with natural Israeli business phrasing.
- Kept professional terms such as `חשבונית מס`, `חשבונית מס/קבלה`, `קבלה`, `דרישת תשלום`, `הזמנת עבודה`, `עוסק מורשה`, `עוסק פטור`, `ח.פ.`, and `שוטף + 30`.
- Avoided unnecessary English terms in Hebrew guidance where a Hebrew professional term exists.
- Kept product names, system names, and identifiers unchanged where examples require them.

## Tone changes

- Standardized instructions to neutral imperative voice.
- Removed first-person package language from public documentation.
- Emphasized user review before sending.
- Kept payment reminders factual and courteous.
- Added clearer warnings for tax, legal, privacy, and marketing-sensitive content.

## Gender and grammar changes

- Added neutral phrasing alternatives for unknown recipient gender.
- Reduced slash-heavy gender forms in guidance.
- Preserved correct masculine and feminine sender apology examples in code tests.
- Clarified plural use for teams and departments.

## Accounting and consumer wording

- Added explicit warnings for missing VAT status.
- Clarified when to use exact document types.
- Avoided invented tax, legal, business identifier, or bank details.
- Replaced legal conclusions in consumer complaints with review-friendly phrasing.


## v3 web-validated pass

Access date: 2026-06-03

- Added validated `חשבוניות ישראל` review wording using `מעל 5,000 ₪ לפני מע״מ`.
- Kept imperative and neutral technical wording.
- Preserved DD/MM/YYYY examples.
- Kept professional Israeli terminology and avoided tax conclusions.
