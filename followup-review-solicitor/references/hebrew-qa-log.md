# Hebrew QA Log

## Scope

Reviewed `SKILL_HE.md`, Hebrew examples in public Markdown, and generated Hebrew templates in the Python client.

## Changes applied

- Converted public-facing dates from hyphen format to `DD/MM/YYYY`.
- Removed Hebrew diacritics from technical prose.
- Replaced avoidable English terms in Hebrew prose with professional Israeli terminology where suitable.
- Standardized financial wording around `חשבונית מס/קבלה`, `חשבוניות/קבלות`, `דו"ח מע"מ`, `אישור תשלום`, and `₪`.
- Kept channel and code values in code blocks where they are required machine inputs.
- Kept product names only where they identify an actual channel.
- Preserved neutral imperative style with concise customer-facing phrasing.
- Removed wording that asks for a specific rating or creates pressure.
- Kept sensitive-service reminders generic and suitable for manual approval.

## Localization decisions

| Item | Decision |
|---|---|
| Currency | Use `₪` before the amount, for example `₪1,250`. |
| Dates | Use `DD/MM/YYYY` in public docs and generated messages. |
| Customer greeting | Use `היי {שם},` or `היי,` when no name is available. |
| Review wording | Use `חוות דעת`; do not ask for a specific star rating. |
| Accounting wording | Use `חשבונית מס/קבלה`, `חשבוניות/קבלות`, and `דו"ח מע"מ`. |
| Sensitive contexts | Use generic reminders without diagnosis, treatment, legal, debt, or tax-investigation details. |

## Remaining intentional choices

- Technical enum values remain in English because they are machine-readable API and CLI inputs.
- Product channel names remain where they identify a real delivery channel.
- Compliance notes returned by the client remain in English because the machine-readable examples are intended for implementers.
