# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` and Hebrew-facing terminology in data and examples.

## Changes

- Replaced date-format guidance with `DD/MM/YYYY` and examples such as `01/08/2026`.
- Removed non-essential foreign wording where a Hebrew professional term exists.
- Used `עצמאים הפועלים באמצעות חברה` instead of a foreign professional label.
- Used `גיליון אלקטרוני` where the text referred to spreadsheet behavior.
- Preserved professional terms used in Israeli practice: `שווי שימוש`, `רכב צמוד`, `מחיר מקורי מתואם`, `שיעור מס שולי`, `ביטוח לאומי`, `מס בריאות`, `מע"מ`, `הוצאות מוכרות`, `חשבי שכר`, `רואי חשבון`.
- Kept code identifiers in English because they are executable field names and category keys.
- Verified that the technical prose contains no Hebrew vowel marks.
- Rephrased guidance into neutral imperative voice: `חשב`, `אמת`, `בדוק`, `הזן`, `שמור`, `קבל`.
- Kept the ₪ symbol for monetary examples.

## Style decisions

- Do not translate executable category keys such as `private_combustion` inside JSON examples.
- Use `היברידי נטען` instead of foreign phrasing for plug-in hybrid in prose.
- Use `רכב בנזין או דיזל` instead of informal vehicle labels.
- Use `תיק השכר` and `אסמכתאות` for payroll review context.

## Result

Hebrew documentation is natural, neutral, and suitable for Israeli payroll, bookkeeping, and tax-planning contexts.
