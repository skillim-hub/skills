# Hebrew Quality Log

## Scope

`SKILL_HE.md`, Hebrew metadata fields, README Hebrew terms, and reference wording that names Israeli tax concepts were reviewed during the v2 correction pass.

## Changes applied

| Area | Change |
|---|---|
| Professional terminology | Preferred עצמאים, עוסק פטור, עוסק מורשה, מחזור, מס עסקאות, מס תשומות, מקדמות מס הכנסה, דמי ביטוח לאומי ודמי ביטוח בריאות. |
| Avoided unnecessary foreign wording | Replaced informal foreign wording in prose with Hebrew professional terms where a standard term exists. Code values such as `osek-patur`, `sandbox`, and `JSON` remain where they are interface values or file formats. |
| Voice | Rewrote guidance in neutral imperative or nominal style, such as יש להשתמש, להציג, להפריד, לאמת. |
| Date localization | Standardized Hebrew guidance to `DD/MM/YYYY`. |
| Currency localization | Kept ₪ formatting in examples and instructions. |
| Technical prose | Confirmed no nikud is used in Hebrew prose. |
| VAT terminology | Used מס עסקאות and מס תשומות instead of vague wording. |
| Threshold terminology | Used תקרת עוסק פטור and ניצול תקרה consistently. |
| Professional review | Referred to רואה חשבון and יועץ מס in appropriate contexts. |

## Remaining intentional interface terms

- `osek-patur` and `osek-murshe` remain as machine-readable values.
- `revenue` and `profit` remain as machine-readable options.
- `sandbox` and `production` remain as command-line environment values.
- `JSON` remains as a file format term.
