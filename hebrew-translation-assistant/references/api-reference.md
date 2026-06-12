# Reference: validated official sources and local helper API

This skill is a Hebrew-English translation assistant. It is not an Israeli government API client and does not make legal, tax, accounting, privacy, accessibility, or consumer-protection decisions. Use the official sources below to verify terminology and source-sensitive values before publishing or filing documents.

Access date for the validated source table: 03/06/2026.

## Current source-sensitive reference facts

| Fact | Verified value for this release | Use in translation |
|---|---:|---|
| Standard Israeli VAT rate | 18% from 01/01/2025 | Preserve when the source states a VAT rate; do not invent calculations. |
| Israel Invoices allocation threshold | 5,000 ₪ before VAT from 01/06/2026 | Flag invoices above the threshold for accountant or Tax Authority review. |
| Date format | DD/MM/YYYY | Convert ISO dates such as `2026-03-05` to `05/03/2026`. |
| Currency presentation | `1,250 ₪` in Hebrew prose, `₪1,250` in compact UI labels | Keep amounts exact. |

## Official source map

| Area | Official source | URL | Verified terminology |
|---|---|---|---|
| VAT rate and terms | Israel Tax Authority tax terminology | https://www.gov.il/en/pages/taxes-glossary | VAT, 18%, value added tax |
| VAT history | Israel Tax Authority VAT history | https://www.gov.il/he/pages/vat-history | `1.1.25 עלה המע"מ ל-18%` |
| Israel Invoices manual allocation | Tax Authority service page | https://www.gov.il/he/service/request-assignment-number-for-tax-invoice | `מספר הקצאה`, `חשבונית מס`, 5,000 ₪ threshold |
| Israel Invoices English service | Tax Authority service page | https://www.gov.il/en/service/request-assignment-number-for-tax-invoice | allocation number for a tax invoice |
| Israel Invoices API | Tax Authority software-house API document | https://www.gov.il/BlobFolder/generalpage/israel-invoice-160723/he/vat_software-houses-180724-en.pdf | API hosts, request fields, error codes |
| Tax API services | Tax Authority API services portal | https://govextra.gov.il/taxes/innovation/home/api/ | API service connection context |
| Withholding tax | Tax Authority withholding certificate service | https://www.gov.il/he/service/itc-gmishurim | `ניכוי מס במקור`, `אישור ניכוי מס במקור` |
| Withholding tax 2026 instruction | Tax Authority instruction 02/2026 | https://www.gov.il/he/pages/inst-02-2026 | 2026 withholding certificates |
| Form 806/857 | Tax Authority annual withholding certificate service | https://www.gov.il/he/service/itc806 | annual withholding certificate |
| Form 847 | Tax Authority insurance commission withholding service | https://www.gov.il/he/service/itc-847 | withholding details form |
| Consumer cancellation | Consumer Protection and Fair Trade Authority | https://www.gov.il/he/pages/returns | `דמי ביטול`, `5%`, `100 ש"ח` |
| Privacy | Privacy Protection Authority | https://www.gov.il/he/pages/duty_to_notify | `מידע אישי`, notification duty |
| Accessibility statement | Equal Rights for Persons with Disabilities Commission | https://www.gov.il/he/pages/declaration_website_accessibility | `הצהרת נגישות`, `הסדרי נגישות` |
| Accessibility coordinator | Equal Rights for Persons with Disabilities Commission | https://www.gov.il/he/pages/accessibility_coordinators_explained | `רכז נגישות` |

## Reference-only Israel Invoices API paths

Do not call these paths from the helper. Include them only to preserve official terms when translating API documentation, support tickets, implementation instructions, or accounting-system copy.

| Service | Sandbox path | Production path | Notes |
|---|---|---|---|
| Invoice approval | `https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval` | `https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval` | Request allocation approval for an invoice. |
| Multi-invoice approval | `https://ita-api.taxes.gov.il/shaam/tsandbox/Multi-invoices/v2/MultiApproval` | `https://ita-api.taxes.gov.il/shaam/production/Multi-invoices/v2/MultiApproval` | Batch approval flow. |
| Invoice information by allocation number | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/details` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/details` | Retrieve invoice information. |
| Allocation number by invoice details | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/confirmationNumber` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber` | Retrieve allocation number from details. |
| Decision: cancel | `https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/Cancel` | `https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/Cancel` | Decision update for held invoice. |
| Decision: continue | `https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/Continue` | `https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/Continue` | Continue without allocation number where applicable. |
| Decision: further objection | `https://ita-api.taxes.gov.il/shaam/tsandbox/InvoiceDecisionApi/v1/FurtherObjection` | `https://ita-api.taxes.gov.il/shaam/production/InvoiceDecisionApi/v1/FurtherObjection` | Request further objection or hearing path. |

No webhook event names are implemented by this package. No official webhook event-name list is cited by this package.

## Reference-only API error table

| HTTP code | Official meaning in source snippets | Translation guidance |
|---:|---|---|
| 200 | OK | Translate as `תקין` or `הבקשה הצליחה`, depending on UI context. |
| 400 | Bad Request | Translate as `בקשה שגויה`; preserve JSON field names. |
| 401 | Unauthorized | Translate as `לא מורשה`; preserve OAuth2 terminology if used in API docs. |
| 403 | Forbidden | Translate as `אין הרשאה`; do not soften the permission issue. |

## Local helper API

### Python quick start

```python
from hebrew_translation_assistant import HebrewTranslationAssistant

client = HebrewTranslationAssistant()
result = client.translate_text(
    "Please issue a tax invoice/receipt for ₪1,250 plus VAT by 2026-03-05.",
    direction="en-to-he",
    register="accounting",
)
print(result.to_json())
```

### Request shape

```json
{
  "text": "Please issue a tax invoice/receipt for ₪1,250 plus VAT by 2026-03-05.",
  "direction": "en-to-he",
  "register": "accounting",
  "audience": "freelance client",
  "industry": "professional services",
  "preserve_terms": ["Starter Plus"]
}
```

### Response shape

```json
{
  "source_text": "Please issue a tax invoice/receipt for ₪1,250 plus VAT by 2026-03-05.",
  "translation": "נא issue a חשבונית מס/קבלה for ₪1,250 בתוספת מע״מ by 05/03/2026.",
  "direction": "en-to-he",
  "register": "accounting",
  "notes": ["Preserve accounting terms, amounts, dates, VAT references, and document type."],
  "detected_terms": {"tax invoice/receipt": "חשבונית מס/קבלה", "plus vat": "בתוספת מע״מ"},
  "warnings": ["Accounting-sensitive content: verify document type, VAT treatment, withholding tax, and totals."],
  "quality_checks": {"numbers_preserved": true, "urls_preserved": true, "emails_preserved": true, "has_hebrew_output": true, "has_english_output": true, "no_nikud": true}
}
```

The helper is terminology-assisted and deterministic. Polish mixed-language drafts before publication.

### Stored request workflow

```bash
CREATE_RESPONSE="$(hebrew-translation-assistant create "Please send the tax invoice." --env sandbox)"
REQUEST_ID="$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")"
hebrew-translation-assistant show "$REQUEST_ID"
```

### Reference facts command

```bash
hebrew-translation-assistant facts
```

Example output:

```json
{
  "access_date": "03/06/2026",
  "vat_rate_percent": "18",
  "vat_effective_date": "01/01/2025",
  "invoice_allocation_threshold_before_vat": "5,000 ₪",
  "invoice_allocation_threshold_effective_date": "01/06/2026"
}
```

## Helper error table

| Code | Meaning | Fix |
|---|---|---|
| `EMPTY_TEXT` | Source text is empty | Provide text to translate or review. |
| `INVALID_DIRECTION` | Direction is not supported | Use `auto`, `en-to-he`, or `he-to-en`. |
| `INVALID_REGISTER` | Register is not supported | Use `formal`, `business`, `casual`, `support`, `legal`, or `accounting`. |
| `INVALID_ENVIRONMENT` | Environment is not supported | Use `sandbox` or `production`. |
| `DATE_PARSE` | Date format is unsupported | Use `YYYY-MM-DD` or `DD/MM/YYYY`. |
| `TERM_NOT_FOUND` | Glossary term is unknown | Use a broader term or add manual context. |
| `NOT_FOUND` | Stored request id does not exist | Check the id and storage directory. |
| `JSON_ERROR` | Stored request file is invalid | Recreate the request or inspect the file. |

## Production review checklist

1. Verify every amount, date, percentage, account number, phone number, email address, URL, order number, and document number.
2. Confirm VAT, withholding tax, invoice allocation, and bookkeeping wording with a professional source when money or reporting is involved.
3. Confirm consumer cancellation and refund wording against current official guidance before publication.
4. Confirm privacy and accessibility notices against current official duties before publication.
5. Remove nikud from technical prose unless quoting a source.
6. Use human review for legal, tax, accounting, certified, privacy, accessibility, medical, immigration, or public-facing material.
