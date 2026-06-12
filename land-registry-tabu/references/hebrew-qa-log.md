# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples in fixtures, and Hebrew terminology appearing in references and tests.

## Changes applied

- Replaced mixed dash forms with `תת-חלקה` in Hebrew-facing prose.
- Updated Hebrew-facing dates to `DD/MM/YYYY`, for example `04/06/2026`.
- Kept monetary values in `₪`, for example `₪1,200,000`.
- Replaced unnecessary foreign wording in Hebrew prose with professional Israeli terminology where practical.
- Preserved accepted professional abbreviations such as `ח.פ.` and `ת"ז`.
- Used neutral imperative forms such as `השתמשו`, `בדקו`, `הפיקו`, `שמרו`, and `דרשו`.
- Avoided first-person plural narration.
- Removed niqqud from technical prose.
- Kept code identifiers such as `base_url`, `JSON`, and command names where they are technical syntax.
- Clarified that ownership facts, planning status, licensing, tax, and legal interpretation are separate review tracks.
- Updated examples to display dates such as `15/02/2022` and `20/03/2024`.

## Terminology decisions

| Term | Selected Hebrew usage | Reason |
|---|---|---|
| Subparcel | תת-חלקה | Common Israeli registry term |
| Caveat | הערת אזהרה | Correct registry term |
| Encumbrance | שעבוד / מגבלה רשומה | Context-dependent professional wording |
| Attachment | עיקול | Correct legal/registry term |
| Easement | זיקת הנאה | Correct land-law term |
| Long lease | חכירה לדורות | Accepted professional term |
| Right holder | בעל זכות | Accurate neutral term |
| Due diligence | בדיקת נאותות | Accepted professional term |
| Order status | מצב הזמנה | Clear service term |
| Idempotency key | מפתח אי כפילות | Practical Hebrew explanation for technical concept |

## Verification

- Hebrew technical prose contains no niqqud.
- Hebrew guide uses neutral imperative voice.
- Dates in Hebrew-facing guide use `DD/MM/YYYY`.
- Currency examples use `₪`.
