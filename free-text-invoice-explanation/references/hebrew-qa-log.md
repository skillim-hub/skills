# Hebrew Quality Assurance Log

## Scope

Reviewed Hebrew public documentation, examples, generated text templates, and scenario descriptions.

## Localization changes

| Area | Change |
| --- | --- |
| Currency | Standardized amounts with `₪`, such as `₪472.00`. |
| Dates | Standardized client-facing dates as `DD/MM/YYYY`, such as `07/03/2026`. |
| VAT | Used `מע״מ` consistently. |
| Tax invoice | Used `חשבונית מס`. |
| Receipt | Used `קבלה`. |
| Invoice-receipt | Used `חשבונית מס/קבלה`. |
| Credit note | Used `חשבונית זיכוי`. |
| Exempt dealer | Used `עוסק פטור`. |
| Authorized dealer | Used `עוסק מורשה`. |
| Reimbursement | Used `החזר הוצאה`. |
| Bookkeeping | Used `ניהול ספרים`. |
| Input VAT | Used `מע״מ תשומות`. |
| Output VAT | Used `מע״מ עסקאות`. |

## Voice changes

| Previous risk | Correction |
| --- | --- |
| Direct personal wording | Replaced with neutral imperative or impersonal wording. |
| Overly technical wording | Replaced with client-facing explanations. |
| Tax certainty | Replaced with verification language. |
| Anglicisms | Replaced with accepted Israeli professional terms. |

## Nikkud review

No vowel marks are used in technical prose. Hebrew punctuation such as geresh and gershayim remains where required for standard terms.

## Examples checked

| Example | Result |
| --- | --- |
| Standard authorized dealer invoice | Natural and professional. |
| Exempt dealer receipt | Avoids VAT deductibility claims. |
| Reimbursement | Requests supporting documentation. |
| Credit note | Links wording to original document. |
| Subscription | Shows service period in Israeli date format. |

## Version 2.1.0 web-validation Hebrew changes

| Area | Change | Reason |
| --- | --- | --- |
| VAT rate wording | Added wording that 18% is a current validated example rate for 2026, not a permanent rule. | Avoid stale-rate assumptions. |
| Allocation number | Added מספר הקצאה, חשבוניות ישראל, תקרה לפני מע״מ, וניכוי מע״מ תשומות. | Use current Israeli professional terminology. |
| Dates | Kept DD/MM/YYYY examples, including 01/01/2026 and 01/06/2026. | Match local client-facing date format. |
| Currency | Kept ₪ before the amount. | Match Israeli invoice style used throughout the package. |
| Tone | Kept imperative and neutral instructions. | Avoid first-person voice and marketing phrasing. |
