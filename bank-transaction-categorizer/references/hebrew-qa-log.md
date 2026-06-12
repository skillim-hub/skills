# Hebrew Quality-Assurance Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew-facing examples in public documentation.

## Changes made

| Area | Change |
|---|---|
| Date localization | Replaced DD-MM-YYYY examples with DD/MM/YYYY in Hebrew documentation and sample data. |
| Currency localization | Preserved ₪ usage in Hebrew guidance. |
| Voice | Reworked instructions toward neutral imperative wording such as `סווג`, `שמור`, `בדוק`, `אל תניח`. |
| Professional terminology | Used Israeli terms such as `רואה חשבון`, `יועץ מס`, `מנהל חשבונות`, `מע"מ`, `מקדמות מס הכנסה`, `ביטוח לאומי`, `אסמכתאות`, `ניכוי מס`, `הוצאה מוכרת`. |
| Anglicisms | Replaced avoidable foreign wording with Hebrew alternatives where a natural professional term exists, while preserving product names and code field names. |
| Niqqud | Confirmed no niqqud appears in technical prose. |
| Gender | Used neutral imperative phrasing that avoids gendered personal address where possible. |
| Mixed-use expenses | Clarified `הוצאה מעורבת`, `ייחוס חלקי`, and documentation review. |
| Card settlement terminology | Clarified `חיוב כרטיס אשראי מרוכז` and `פירוט כרטיס`. |
| Review terminology | Used `בדיקת אדם`, `בדיקה נדרשת`, and `סימון לאימות` consistently. |

## Remaining intentional English terms

The following remain intentionally because they are field names, command-line values, product names, or code-level constants:

- `CSV`
- `JSON`
- `BIT`
- `PayBox`
- `MAX`
- `CAL`
- `Google Cloud`
- `AWS`
- `Microsoft`
- `Adobe`
- `Zoom`
- `GitHub`
- `confidence`
- `needs-review`
- `possible-duplicate`
- `confirm-business-income`

## Final status

Hebrew documentation is suitable for Israeli professional use as procedural guidance. It remains a workflow and categorization aid, not legal, tax, accounting, or banking advice.


## V3 web-validation Hebrew changes

- Added a Hebrew note that the general VAT rate is 18% from 01/01/2025 and must be re-checked before reporting.
- Clarified that bank and acquirer names are examples from Bank of Israel supervised-entity pages and do not imply endorsement.
- Clarified that the package classifies local CSV-style exports and does not implement live account access, consent management, webhook events, or official API paths.
