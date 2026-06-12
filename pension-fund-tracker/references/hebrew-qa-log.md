# Hebrew QA Log

## Scope

Reviewed Hebrew public Markdown for professional Israeli terminology, neutral imperative voice, no nikud, and localization with ₪ and DD/MM/YYYY.

## Changes applied

| Area | Change |
|---|---|
| Terminology | Used `קרן פנסיה`, `מסלול השקעה`, `חברה מנהלת`, `דמי ניהול מהפקדה`, `דמי ניהול מצבירה`, `תאריך דיווח`, `חשבי שכר`, and `בעל רישיון`. |
| Localization | Replaced date examples with DD/MM/YYYY, including `31/12/2025`. |
| Currency | Used `₪` for shekel examples and `נכסים במיליוני ₪` for asset fields. |
| Voice | Rephrased guidance toward neutral imperative forms such as `השווה`, `בדוק`, `סנן`, `שמור`, and `הצג`. |
| Advice boundary | Used `מידע בלבד` and avoided suitability language. |
| Anglicisms | Kept executable formats and names such as CSV, JSON, CKAN, and Data.gov.il; used Hebrew terms where established professional terms exist. |
| Nikud | Verified that technical prose contains no Hebrew vowel marks. |

## Preferred terminology

| Use | Avoid |
|---|---|
| דמי ניהול | פיז |
| תשואה | ריטרן |
| חברה מנהלת | פרוביידר כאשר מדובר בגוף מוסדי |
| מסלול השקעה | אינבסטמנט טראק |
| תאריך דיווח | ריפורט דייט |
| מידע בלבד | המלצה או ייעוץ |

## Final QA notes

- Preserve exact product names and official portal names when they appear as names.
- Keep command names and code identifiers in English because they are executable interface names.
- Keep all personal recommendation language outside the skill scope.


## V3 web-validation Hebrew corrections - 02/06/2026

| Area | Change |
|---|---|
| Source terminology | Replaced broad "מקורות רשמיים של משרד האוצר" with "רשות שוק ההון, ביטוח וחיסכון" plus a provenance note for legacy Ministry of Finance references. |
| VAT localization | Added "18%" and "02/06/2026" in Israeli date format and clarified that VAT is not part of pension-return calculations. |
| Technical wording | Kept `Data.gov.il`, `API`, `CSV`, `XLSX`, and `JSON` as technical names; used Hebrew terms for קרן פנסיה, מסלול השקעה, דמי ניהול מצבירה and דמי ניהול מהפקדה. |
| Voice | Kept neutral imperative phrasing and avoided first-person wording. |
