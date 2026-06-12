# Hebrew QA Log

Access date for terminology and regulatory checks: 2026-06-02

## QA scope

- Checked `SKILL_HE.md`, Hebrew descriptions in `metadata.json`, Hebrew category labels in code, and Hebrew terminology in reference files.
- Removed nikud from technical prose.
- Kept neutral imperative wording: use forms such as `השתמש`, `בדוק`, `שמור`, `העבר`, and avoid first-person phrasing.
- Localized examples with ₪ amounts and `DD/MM/YYYY` dates.

## Terminology decisions

| English concept | Hebrew term used | QA note |
|---|---|---|
| VAT | מע״מ | Standard Israeli professional term. |
| Input VAT | מס תשומות | Preferred over transliteration. |
| Tax invoice | חשבונית מס | Official business document term. |
| Allocation number | מספר הקצאה | Official Invoice Israel terminology. |
| Osek Patur | עוסק פטור | Official VAT registration term. |
| Osek Murshe | עוסק מורשה | Official VAT registration term. |
| Micro business owner | בעל עסק זעיר | Separate income-tax reform term, not a synonym for עוסק פטור. |
| Uniform structure file | קובץ במבנה אחיד | Official accounting-software terminology. |
| Computerized bookkeeping system | מערכת חשבונות ממוחשבת | Official registration terminology. |
| Accountant handoff package | חבילת מסירה לרואה חשבון | Natural professional phrasing. |

## Changes made in v2.2.0

- Corrected VAT examples to 18%: ₪117.00 gross equals ₪99.15 net and ₪17.85 VAT.
- Added a Hebrew 2026 defaults section explaining VAT, Osek Patur ceiling checks, and Invoice Israel allocation-number review.
- Reworded domestic hospitality guidance as a conservative default that requires accountant review.
- Reworded mixed-use vehicle VAT guidance as a configurable assumption, not a universal rule.
- Checked that public Hebrew Markdown contains no nikud in prose.
- Preserved `DD/MM/YYYY` examples, including `15/01/2026`.

## Items to recheck annually

- VAT rate and effective date.
- Osek Patur and בעל עסק זעיר ceiling.
- Invoice Israel allocation thresholds.
- Indexed caps for gifts, refreshments, travel, and other certain expenses.
- Bookkeeping software and uniform-file requirements.
