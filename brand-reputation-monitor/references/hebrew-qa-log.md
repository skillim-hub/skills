# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew examples across public references for Israeli professional terminology, neutral imperative voice, date and currency localization, and unnecessary transliteration.

## Changes made

| Area | Change |
|---|---|
| Date localization | Replaced DD/MM/YYYY references and examples with DD/MM/YYYY. |
| Currency localization | Preserved ₪ in examples and metadata. |
| Neutral voice | Kept instructions in an imperative or impersonal professional form. |
| Technical prose | Removed niqqud from Hebrew technical prose where present. |
| Terminology | Preserved natural Israeli terms such as `חשבונית מס`, `קבלה`, `זיכוי`, `חיוב כפול`, `מע״מ`, `ביטול עסקה`, `הרשות להגנת הצרכן ולסחר הוגן`, `הסלמה`, `שירות לקוחות`, `דוח`, and `תקופת שמירה`. |
| Anglicisms | Preferred Hebrew terms in prose where a standard Hebrew term exists; retained platform names and code identifiers where needed. |
| Sensitive contexts | Preserved stronger wording around פרטיות, בטיחות, בריאות, הפליה, הטרדה, דין וחשבון, וייעוץ מוסמך. |

## Validation notes

- No niqqud was intentionally retained in Hebrew prose.
- DD/MM/YYYY is the documented local report format.
- Public-facing Hebrew instructions avoid first-person organizational claims.
- Code identifiers and platform names remain unchanged where required for execution or source naming.
