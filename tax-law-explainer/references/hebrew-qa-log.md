# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples in the Python helper, and Hebrew-facing references for professional Israeli terminology, neutral imperative voice, no nikud in technical prose, and DD/MM/YYYY date localization.

## Changes made

- Replaced DD-MM-YYYY references with DD/MM/YYYY.
- Replaced example dates such as 02-06-2026 with 02/06/2026.
- Reduced unnecessary Anglicism by replacing standalone references to פרילנסר with עצמאי or עצמאי נותן שירותים.
- Kept accepted professional Israeli terms: עוסק פטור, עוסק מורשה, חשבונית מס, קבלה, ניכוי מס במקור, מקדמות, מס שבח, מס רכישה, היטל השבחה, הצהרת הון.
- Preserved neutral imperative forms such as בדוק, זהה, אשר, אסוף, שמור, סמן.
- Preserved currency formatting with ₪ in examples.

## Verification

- Nikud hits in `SKILL_HE.md`: 0.
- Date style checked: DD/MM/YYYY.
- Public Markdown emoji removal applied before bundling.
- Hebrew branding, author, logo, and banner statements were not retained.

## Notes

Thresholds, tax brackets, and form deadlines remain marked as current-data dependencies and must be verified against official publications before filing or signing.
