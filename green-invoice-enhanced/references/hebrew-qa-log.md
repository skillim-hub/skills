# Hebrew QA log

The Hebrew guide and Hebrew-facing strings were reviewed for consistency, professional Israeli accounting terminology, absence of niqqud, neutral imperative style, currency/date localization, and consistent handling of technical terms.

## Style decisions

| Area | Decision |
|---|---|
| Nikkud | No niqqud is used in technical prose. |
| Audience | Neutral imperative or impersonal professional wording is preferred over gendered singular forms. |
| Webhook term | Use `וובהוק` and `וובהוקים` consistently in Hebrew prose; keep `webhook` only in code identifiers, URLs, or protocol names where required. |
| Tax Authority terminology | Use `שע״מ`, `רשות המסים`, `מספר הקצאה`, and `מספר הקצאה משע״מ` where appropriate. |
| VAT terminology | Use `מע״מ`, `חשבונית מס`, `חשבונית מס/קבלה`, `חשבונית זיכוי`, `קבלה`, and `ניכוי במקור`. |
| Dates and currency | Use `DD/MM/YYYY` examples and `₪` for shekel examples in Hebrew prose. |

## Changes made

| File | Before | After |
|---|---|---|
| `SKILL_HE.md` | `Webhooks` | `וובהוקים` |
| `SKILL_HE.md` | `Webhook` | `וובהוק` |
| `SKILL_HE.md` | `webhooks` | `וובהוקים` |
| `SKILL_HE.md` | `webhook` | `וובהוק` |
| `SKILL_HE.md` | `Sandbox` | `סביבת בדיקות` |
| `SKILL_HE.md` | `sandbox` | `סביבת בדיקות` |
| `SKILL_HE.md` | `Checklist` | `רשימת בדיקה` |
| `references/api-reference.md` | `Webhooks` | `וובהוקים` |
| `references/api-reference.md` | `webhooks` | `וובהוקים` |
| `references/api-reference.md` | `webhook` | `וובהוק` |
| `references/api-reference.md` | `Sandbox` | `סביבת בדיקות` |
| `references/api-reference.md` | `sandbox` | `סביבת בדיקות` |
| `references/document-workflows.md` | `Webhook` | `וובהוק` |
| `references/document-workflows.md` | `webhook` | `וובהוק` |
| `references/document-workflows.md` | `dashboard` | `לוח הבקרה` |

## Accounting terminology check

| Term | Preferred Hebrew wording used | Notes |
|---|---|---|
| Tax invoice-receipt | חשבונית מס/קבלה | Used for combined invoice and receipt when payment is received at issuance. |
| Tax invoice | חשבונית מס | Used for VAT invoice before payment receipt. |
| Receipt | קבלה | Used for payment acknowledgment. |
| Credit note | חשבונית זיכוי | Used for cancellation, credit, and refund workflows. |
| Allocation number | מספר הקצאה / מספר הקצאה משע״מ | Used for qualifying B2B tax documents. |
| VAT | מע״מ | Used consistently with 18 percent examples pending live regulatory verification. |
| Withholding tax | ניכוי במקור | Used as an accounting/payment-related concept. |

## Remaining live-review item

Live regulatory thresholds for מספר הקצאה and any current Tax Authority wording must be rechecked in a browser-enabled environment before production go-live.

## Correction after terminology replacement

Technical tokens were restored after the Hebrew terminology pass:

| Token type | Restored value | Reason |
|---|---|---|
| Sandbox host | `sandbox.d.greeninvoice.co.il` | Hostnames must remain ASCII and match the API base URL. |
| Webhook endpoint paths | `/webhooks` | API paths and method names must not be localized. |
| Python method names | `list_webhooks`, `register_webhook`, `delete_webhook` | Code identifiers must remain importable and match the client implementation. |
| Public article URL | `/magazine/webhooks/` | URLs must not be localized. |

## Additional Hebrew wording corrections

| File | Before | After |
|---|---|---|
| `SKILL_HE.md` | `גישת API ו-וובהוקים עשויה להיות תלויה` | `גישת API ושימוש בוובהוקים עשויים להיות תלויים` |
| `SKILL_HE.md` | `retries` | `ניסיונות חוזרים` |
| `SKILL_HE.md` | `retry ליצירת מסמך` | `ניסיון חוזר ליצירת מסמך` |
