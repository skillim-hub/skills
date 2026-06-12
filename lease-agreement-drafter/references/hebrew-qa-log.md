# Hebrew QA Log

## Scope

Reviewed Hebrew public prose in `SKILL_HE.md`, Hebrew examples, generated Hebrew draft text, and Hebrew-facing reference material.

## Changes applied

| Area | Change |
| --- | --- |
| Technical terminology | Replaced informal phrasing with professional Israeli terms such as דמי שכירות, בטוחות, ארנונה, דמי ניהול, מורשי חתימה, פרוטוקול מסירה, פגם דחוף ושכירות משנה |
| Voice | Normalized instructions to neutral imperative voice |
| Dates | Standardized examples to DD/MM/YYYY, including 01/08/2026 and 31/07/2027 |
| Currency | Standardized visible amounts to ₪ and numeric ILS fields in JSON |
| Tax | Used מע"מ and חשבונית מס instead of informal or transliterated wording |
| Legal concepts | Used חוק השכירות והשאילה, דיירות מוגנת, דמי מפתח, דין קוגנטי, גוש, חלקה ותת חלקה |
| Gender | Avoided unnecessary gendered verbs by using neutral commands and nouns |
| Nikkud | Removed vowel marks from technical prose |
| Anglicisms | Avoided transliteration when a standard Hebrew term exists |
| Consumer clarity | Added plain warnings for protected tenancy, home office use, and apartment security caps |

## Review notes

- Keep statutory statements cautious because coverage depends on current law and facts.
- Use `₪` in rendered Markdown and numeric values in JSON.
- Keep Hebrew JSON readable with `ensure_ascii=False`.
- Avoid mixing English terms into Hebrew prose unless referring to code identifiers.
