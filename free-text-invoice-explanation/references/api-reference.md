# Reference: Data Schema and Israeli Regulatory Sources

This skill is a local explanation helper. It does not call an external billing, tax, government, or webhook API. Treat this file as the equivalent of an API reference: it documents the request schema, response schema, error codes, and official Israeli sources that should be checked before production use.

## Web-validated regulatory anchors

Access date for the validation pass: 2026-06-02. See `references/verification-log.md` for source snippets, second-pass sources, and correction status.

| Topic | Current validated reference | Practical relevance |
| --- | --- | --- |
| VAT rate | Standard VAT is 18% from 01/01/2025 and confirmed current for 2026 by the Tax Authority and a 2026 PwC cross-check. | Use 18% for examples unless the source document supplies another lawful treatment. |
| VAT framework | Value Added Tax Law, 5736-1975, in the Knesset National Legislation Database. | Determines whether VAT wording is appropriate. |
| Bookkeeping records | Income Tax bookkeeping instructions and Tax Authority software-house guidance. | Determines recordkeeping and document classification practices. |
| Tax invoice and receipt handling | Tax Authority guidance for invoices, receipts, Israel Invoice allocation numbers, and supplier invoice verification. | Confirms document type, allocation-number cautions, and supporting-document references. |
| Exempt dealer status | Tax Authority guidance for עוסק פטור and Kol Zchut second-pass references. | Confirms that an exempt dealer does not charge VAT and does not issue tax invoices. |
| Authorized dealer status | Tax Authority Form 821 and invoice guidance. | Confirms ordinary VAT collection language and חשבונית מס wording. |
| 2026 exempt-dealer ceiling | ₪122,833 for 2026, verified in the web validation log. | Use only as a reference warning; do not hard-code eligibility decisions. |
| Israel Invoice allocation thresholds | ₪10,000 before VAT from 01/01/2026; ₪5,000 before VAT from 01/06/2026. | Add a caution for high-value B2B tax invoices when relevant. |
| Consumer-facing wording | Consumer Protection Law, 5741-1981, in the Knesset National Legislation Database. | Supports clear, non-misleading wording for consumers. |
| Privacy in customer records | Privacy Protection Law, 5741-1981, in the Knesset National Legislation Database. | Supports minimal use of personal data in explanations. |

## Official source links

Use these links for production review. The skill does not fetch them automatically.

| Source | URL |
| --- | --- |
| Israel Tax Authority | `https://www.gov.il/he/departments/israel_tax_authority` |
| VAT topic page | `https://www.gov.il/he/departments/topics/value_added_tax` |
| VAT history | `https://www.gov.il/he/pages/vat-history` |
| VAT rates and amounts | `https://www.gov.il/en/pages/vat-rate-amount-new` |
| New dealer VAT guide | `https://www.gov.il/he/pages/vat-to-the-new-dealer` |
| Open exempt-dealer file online | `https://www.gov.il/he/service/request-open-exempt-dealer-via-internet` |
| Open authorized-dealer file, Form 821 | `https://www.gov.il/he/service/vat-821` |
| Exempt dealer declaration | `https://www.gov.il/he/service/vat-declarationisexempt` |
| VAT dealer lookup | `https://www.gov.il/he/service/vat-apply-online` |
| Withholding tax and bookkeeping certificate lookup | `https://www.gov.il/he/service/itc-gmishurim` |
| Request tax-invoice allocation number | `https://www.gov.il/he/service/request-assignment-number-for-tax-invoice` |
| Verify supplier invoice by allocation number | `https://www.gov.il/he/service/verify-vendor-invoice-information` |
| Israel Invoice topic page | `https://www.gov.il/he/departments/topics/israel-invoice` |
| VAT Law, Knesset National Legislation Database | `https://main.knesset.gov.il/apps/legislation/main/laws/2001068` |
| Consumer Protection Law, Knesset National Legislation Database | `https://main.knesset.gov.il/Activity/Legislation/Laws/pages/lawprimary.aspx?lawitemid=2000237&st=lawlaws&t=lawlaws` |
| Privacy Protection Law, Knesset National Legislation Database | `https://main.knesset.gov.il/Activity/Legislation/Laws/pages/lawprimary.aspx?lawitemid=2000234` |

## External API, endpoint, and webhook status

| Item | Status |
| --- | --- |
| Government API host | Not used by this package. |
| Endpoint paths | Not applicable. The CLI reads local JSON and returns local JSON. |
| Webhook event names | Not applicable. The package does not receive callbacks. |
| Request authentication | Not applicable. No network request is made. |
| Production source verification | Required outside the package before relying on legal, accounting, or tax conclusions. |

## Request object

```json
{
  "context": {
    "language": "he",
    "business_type": "authorized_dealer",
    "document_type": "tax_invoice",
    "customer_type": "business",
    "document_date": "07/03/2026",
    "business_name": "שם העסק",
    "customer_name": "שם הלקוח",
    "include_legal_caveat": true,
    "environment": "sandbox"
  },
  "options": {
    "language": "he",
    "detail_level": "standard",
    "tone": "plain",
    "include_amount_breakdown": true,
    "include_next_action": true,
    "date_format": "DD/MM/YYYY"
  },
  "lines": [
    {
      "description": "תחזוקת אתר חודשית",
      "quantity": "1",
      "unit_price": "400",
      "vat_rate": "18",
      "currency": "ILS",
      "category": "שירותים",
      "service_period": "01/03/2026-31/03/2026",
      "note": "כולל גיבוי חודשי",
      "reimbursable": false,
      "reverse_charge": false,
      "exempt_from_vat": false
    }
  ]
}
```

## Context fields

| Field | Type | Required | Values | Notes |
| --- | --- | --- | --- | --- |
| `language` | string | No | `he`, `en` | Default is Hebrew. |
| `business_type` | string | No | `authorized_dealer`, `exempt_dealer`, `company`, `nonprofit`, `consumer` | Drives VAT wording. |
| `document_type` | string | No | `tax_invoice`, `invoice_receipt`, `receipt`, `credit_note`, `proforma`, `invoice` | Drives document-specific explanations. |
| `customer_type` | string | No | `business`, `consumer`, `accountant` | Drives tone and detail. |
| `document_date` | string | No | `DD/MM/YYYY` preferred | Use Israeli display format. |
| `business_name` | string | No | free text | Optional. |
| `customer_name` | string | No | free text | Optional. |
| `include_legal_caveat` | boolean | No | true, false | Adds verification caveat in detailed output. |
| `environment` | string | No | `sandbox`, `production` | Used by CLI and examples. |

## Line fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `description` | string | Yes | Client-facing description. |
| `quantity` | decimal string | No | Defaults to `1`. |
| `unit_price` | decimal string | No | Amount per unit before VAT unless the source system says otherwise. |
| `vat_rate` | decimal string | No | Example default is `18`, confirmed in the web validation log for 2026. Keep it configurable. |
| `currency` | string | No | `ILS` and `NIS` display as `₪`. |
| `category` | string | No | Optional grouping. |
| `service_period` | string | No | Prefer `DD/MM/YYYY-DD/MM/YYYY`. |
| `note` | string | No | Client-visible note. |
| `reimbursable` | boolean | No | Adds reimbursement wording. |
| `reverse_charge` | boolean | No | Adds reverse-charge caution and zero VAT calculation. |
| `exempt_from_vat` | boolean | No | Adds VAT-exempt wording and zero VAT calculation. |

## Response object

```json
{
  "context": {
    "business_type": "authorized_dealer",
    "document_type": "tax_invoice",
    "customer_type": "business",
    "language": "he",
    "document_date": "07/03/2026",
    "business_name": "שם העסק",
    "customer_name": null,
    "include_legal_caveat": true,
    "environment": "sandbox"
  },
  "line_count": 1,
  "explanations": [
    {
      "title": "הסבר עבור תחזוקת אתר חודשית",
      "plain_text": "השורה מתארת תחזוקת אתר חודשית...",
      "amount_before_vat": "400.00",
      "vat_amount": "72.00",
      "amount_after_vat": "472.00",
      "issues": [],
      "tags": ["service_period"]
    }
  ],
  "totals": {
    "amount_before_vat": "400.00",
    "vat_amount": "72.00",
    "amount_after_vat": "472.00"
  },
  "summary": "סיכום המסמך: 1 שורות..."
}
```

## Validation issues

| Code | Severity | Meaning | Recommended action |
| --- | --- | --- | --- |
| `missing_description` | error | Description is empty. | Add a client-facing line description. |
| `non_positive_quantity` | error | Quantity is zero or negative. | Correct quantity or use credit-note logic. |
| `negative_price` | warning | Negative amount appears outside credit note. | Use `credit_note` if it reverses a prior charge. |
| `invalid_vat_rate` | error | VAT rate is outside 0-100. | Correct the VAT rate. |
| `exempt_dealer_vat` | warning | Exempt dealer line charges VAT. | Set VAT to zero or review business type. |
| `receipt_vat_language` | warning | Receipt has VAT-like wording. | Use receipt language only, or change document type. |
| `reverse_charge_vat` | warning | Reverse charge line also charges VAT. | Review reverse-charge treatment. |
| `uncommon_currency` | info | Currency is uncommon for helper formatting. | Verify display and accounting amount. |

## Example: create local explanation response

```bash
invoice-explain explain --input invoice.json --env sandbox > response.json
```

## Example: reuse identifier from create response

```bash
EXPLANATION_ID="$(python - <<'PY'
import json
data = json.load(open("response.json", encoding="utf-8"))
print(data["explanations"][0]["title"])
PY
)"
```

Use the extracted identifier when selecting the explanation for follow-up display, translation, or manual review.

## Error table for CLI use

| Error text | Likely cause | Fix |
| --- | --- | --- |
| `Provide --input or pipe a JSON payload` | No input file and no standard input | Add `--input invoice.json`. |
| `JSON payload must include a lines list` | Payload schema is incomplete | Add a top-level `lines` array. |
| `Payload must be a JSON object` | Input is an array or scalar | Wrap data in a request object. |
| `vat_rate must be a decimal-compatible value` | VAT rate is not numeric | Use a decimal string such as `18`. |
| `Invalid value for --env` | Environment is not supported | Use `sandbox` or `production`. |
