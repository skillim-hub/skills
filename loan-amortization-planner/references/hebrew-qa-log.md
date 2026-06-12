# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` for technical Hebrew quality, neutral imperative voice, Israeli finance terminology, date localization, and currency notation.

## Changes applied

- הוחלף ניסוח מטבע כללי בסימון ₪
- הוחלף ש"ח בסימון ₪
- הוחלף אנגליזם חלקי במונח מקצועי ברור
- הוחלף מונח לועזי במונח עברי מקצועי
- חודד מונח גרייס לניסוח מקצועי בעברית
- חודד שימוש חוזר במונח דחיית תשלומי קרן
- הוחלף מונח טכני בניסוח מוכר בישראל
- קוצר ניסוח טכני בעברית
- נשמר מונח קובץ תקני

## Checks

| Check | Result |
|---|---|
| Niqqud in technical prose | None found after cleanup |
| Date localization | `DD/MM/YYYY` used for Israeli-facing examples |
| Currency notation | ₪ used in Hebrew-facing prose and examples |
| Voice | Imperative and neutral instructions retained |
| Professional terminology | Financing, indexation, repayment, fee, and cash-flow terms reviewed |
| Avoidable Anglicisms | Replaced where a standard Hebrew term was available |
| Technical acronyms | JSON and CSV retained because they are file-format names |
