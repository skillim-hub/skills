# Hebrew QA Log

## Scope

Reviewed public Hebrew prose in `SKILL_HE.md` and Hebrew examples across references for professional Israeli terminology, neutral imperative voice, lack of Hebrew vowel marks, ₪ formatting, and DD/MM/YYYY date policy.

## Changes made

| Area | Change |
|---|---|
| Date localization | Replaced DD-MM-YYYY guidance with DD/MM/YYYY examples such as `03/06/2026`. |
| Currency | Standardized ₪ examples and kept amounts isolated with `bdi dir="ltr"`. |
| Voice | Rephrased guidance as neutral imperatives such as "להגדיר", "להשתמש", "להימנע", and "לבדוק". |
| Technical Hebrew | Replaced unnecessary loanwords with Israeli professional terms where a common Hebrew term exists. |
| Production wording | Replaced informal deployment wording with "סביבת ייצור". |
| Mobile wording | Replaced casual wording with "נייד", "מסכים צרים", and "מקלדות בנייד". |
| Desktop wording | Replaced casual wording with "מחשב שולחני". |
| Localization wording | Replaced broad loanword usage with "התאמה לישראל" or "מדיניות תאריך" where clearer. |
| Accessibility wording | Used "נגישות", "טכנולוגיות מסייעות", "קורא מסך", "מיקוד", and "הגדלת תצוגה". |
| Accounting terminology | Standardized "חשבונית מס", "קבלה", "עוסק פטור", "עוסק מורשה", "ח\"פ", "מע\"מ", and "מק\"ט". |
| Direction terms | Kept `LTR`, `RTL`, `dir`, `lang`, `bdi`, `HTML`, `CSS`, `React`, and `Tailwind` as technical identifiers. |
| Vowel marks | Confirmed that no Hebrew vowel marks are used in technical prose. |
| Public Markdown | Confirmed public Markdown contains no emoji characters. |

## Review notes

- Hebrew geresh and gershayim are retained where they are part of standard Israeli abbreviations, such as דוא"ל, ח"פ, מע"מ and מק"ט.
- Technology names remain in Latin script when they are product or standard names.
- Legal, tax, accessibility, and privacy language is framed as implementation guidance rather than binding legal advice.
