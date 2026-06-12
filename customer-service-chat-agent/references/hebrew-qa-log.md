# Hebrew QA Log

Audit date: 03/06/2026

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples in `SKILL.md`, reference files, CLI examples, and Python customer-facing strings.

## Changes applied

| Area | Change |
|---|---|
| Date localization | Replaced DD/MM/YYYY with DD/MM/YYYY across public documentation and tests |
| Example dates | Replaced dates such as 05/06/2026 with 05/06/2026 |
| Technical prose | Confirmed no nikud is used in Hebrew technical prose |
| Tone | Kept neutral imperative and service-oriented phrasing |
| Gender | Preferred neutral phrasing such as "אפשר לשלוח", "כדאי לצרף", "נבדוק" |
| Accounting terminology | Kept Israeli terms: חשבונית מס/קבלה, מע״מ, ח.פ., עוסק מורשה, עוסק פטור |
| Payment terminology | Kept Israeli terms: אשראי, ביט, העברה בנקאית, חיוב כפול |
| Delivery terminology | Kept משלוח, שליח, מספר מעקב, ימי עסקים, איסוף עצמי |
| Privacy terminology | Kept מחיקת מידע, ייצוא מידע, אחראי פרטיות |
| Accessibility terminology | Kept נגישות, קורא מסך, ערוץ שירות חלופי |
| Anglicisms | Replaced unnecessary imported phrasing where a Hebrew term exists; retained API, CLI, JSON, SLA, and pytest as technical identifiers |
| Currency | Confirmed use of ₪ in customer-facing price examples |

## Notes

- Hebrew customer-facing strings avoid final refund approval.
- Legal, tax, medical, payment dispute, privacy, and accessibility requests are routed to human review.
- CLI and examples keep JSON field names in English because they are machine-readable integration keys.
