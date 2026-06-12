# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` for natural Israeli professional terminology, neutral imperative style, date and currency localization, and absence of nikud in technical prose.

## Changes applied

| Area | Change |
|---|---|
| Terminology | Used `חיוב מחזורי`, `חשבונית מס`, `חשבונית מס קבלה`, `חשבונית זיכוי`, `מספר הקצאה`, `שע״מ`, `רשות המסים`, `מנהל חשבונות`, `רואה חשבון` |
| Dates | Standardized visible examples to `DD/MM/YYYY`, such as `31/01/2026` |
| Currency | Used `שקלים` and `₪` where relevant instead of transliterated currency labels |
| Voice | Rewrote guidance as imperative instructions: `הגדר`, `בדוק`, `שמור`, `אל תמחק` |
| Anglicisms | Replaced avoidable transliterations with Hebrew terms such as `סביבת בדיקות`, `ייצור`, `ממשק`, `פיוס`, `מסמך תיקון` |
| Technical identifiers | Kept code identifiers in English where required by Python and JSON |
| Nikud | Removed vowel marks from Hebrew prose |
| Legal caution | Added instruction to verify rules with רשות המסים or a licensed professional before production |

## Remaining intentional English

| Term | Reason |
|---|---|
| Python identifiers | Required by code examples |
| JSON keys | Required by payload examples |
| File paths | Required for navigation |
| `sandbox` and `production` inside code | Required enum values for the package |

## 2026-06-02 v1.2.0 final QA

- עודכנו ספי ההקצאה לשנת 2026: ₪10,000 מ-01/01/2026 ו-₪5,000 מ-01/06/2026.
- הוסר ניסוח שמציג סף שנתי יחיד לשנת 2026.
- נשמרה לשון ציווי ניטרלית ללא פנייה בגוף ראשון.
- נשמרו מונחים מקצועיים: רשות המסים, מע"מ, מספר הקצאה, עוסק מורשה, מס תשומות, חשבונית מס/קבלה.
- נשמר פורמט תאריך ישראלי `DD/MM/YYYY` בתיעוד למפעילים.
- לא נוסף ניקוד לטקסט הטכני.
