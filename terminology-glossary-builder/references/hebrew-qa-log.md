# Hebrew QA log

## Review scope

Reviewed `SKILL_HE.md`, Hebrew fields in `metadata.json`, Hebrew definitions in `terminology_glossary_builder/client.py`, Hebrew examples, and public reference notes that include Hebrew terminology.

## Corrections applied

| Area | Change |
|---|---|
| Technical prose | Removed nikud from Hebrew prose and kept unpointed modern Hebrew. |
| Tone | Rewrote instructions in neutral imperative form. |
| Currency | Standardized shekel references to ₪. |
| Dates | Standardized user-facing date examples to DD/MM/YYYY. |
| Tax terminology | Used `מס ערך מוסף`, `חשבונית מס`, `ניכוי מס במקור`, `עוסק פטור`, and `עוסק מורשה`. |
| Accounting distinction | Kept `קבלה` separate from `חשבונית מס`. |
| Consumer terminology | Used `ביטול עסקה צרכנית`, `תעודת אחריות`, and `הרשות להגנת הצרכן ולסחר הוגן`. |
| Privacy terminology | Used `מדיניות פרטיות`, `מאגר מידע`, and `הרשות להגנת הפרטיות`. |
| Accessibility terminology | Used `הצהרת נגישות` and `נציבות שוויון זכויות לאנשים עם מוגבלות`. |
| Corporate terminology | Used `נסח חברה`, `חברה פרטית`, and `רשות התאגידים`. |
| Import and standards | Used `רשימון יבוא`, `תו תקן`, and `מכון התקנים הישראלי`. |
| Banking and finance | Used `חשבון מוגבל`, `תשקיף`, `בנק ישראל`, and `רשות ניירות ערך`. |

## Terms intentionally left in English

| Term | Reason |
|---|---|
| `GOV.IL` | Official service name. |
| `data.gov.il` | Official domain and source identifier. |
| File paths and command names | Required executable names and package paths. |
| `JSON`, `CSV`, `Markdown`, `UTF-8` | Standard technical format names used in commands and code. |

## Final Hebrew checks

- No nikud detected in Hebrew technical prose.
- No decorative emoji detected in public Markdown.
- No unnecessary transliteration detected where a common Hebrew term exists.
- Public Hebrew instructions use direct imperative phrasing.
- Examples use Israeli formatting for dates and currency.
