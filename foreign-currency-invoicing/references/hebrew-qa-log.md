# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md` for Israeli professional terminology, neutral imperative voice, date localization, shekel display, and technical consistency with the English guide.

## Changes made

| Area | Change |
|---|---|
| Technical terminology | Used חשבונית מס, חשבונית מס/קבלה, חשבונית זיכוי, עוסק מורשה, עוסק פטור, שער יציג, בסיס מס, מע"מ פלט, חיוב עצמי and מחוץ לתחולה. |
| Localization | Standardized Israeli-facing dates to DD/MM/YYYY and shekel amounts to ₪. |
| Voice | Rephrased guidance as imperative instructions such as השתמש, קבע, שלוף, שמור and אמת. |
| Anglicisms | Preferred שורת פקודה, ממשק, לקוח Python, קובץ, מסלול ביקורת and הנהלת חשבונות over unnecessary transliteration. |
| Legal/accounting precision | Distinguished מע"מ בשיעור אפס from פטור and clarified that foreign currency alone does not determine VAT treatment. |
| Nikkud | Confirmed no vowel marks appear in technical prose. |
| Examples | Kept JSON keys in English because they are executable API fields; translated explanatory notes where appropriate. |

## Review result

The Hebrew guide uses natural Israeli business terminology, neutral operational phrasing, ₪ notation, and DD/MM/YYYY dates. Complex VAT determinations are directed to licensed professional review rather than overconfident automation.


## 2026-06-02 final web-validation pass

| Area | Change |
|---|---|
| Terminology | Added Hebrew wording for ממשק סדרות SDMX, שער יציג, מע"מ בשיעור אפס, חיוב עצמי and מספר הקצאה without nikud. |
| Date and currency localization | Preserved DD/MM/YYYY and ₪ in Hebrew-facing guidance. |
| Neutral imperative voice | Kept direct operational instructions and avoided first-person phrasing. |
| API correction | Clarified that date-specific Bank of Israel lookup should use the SDMX series interface, while the current public API is for current-rate checks. |
