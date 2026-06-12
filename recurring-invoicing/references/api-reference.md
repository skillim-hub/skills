# API and Regulation Reference

This reference records the live-validated integration points for recurring invoice automation in Israel. Treat this file as an implementation aid, not legal or accounting advice. Verify the current law, the Tax Authority developer portal, and production credentials before issuing documents.

## Source validation status

See `references/verification-log.md` for two-pass validation with official snippets, URLs, access date, and corrections.

## Israeli VAT rate selection

| Issue date | Default VAT rate | Validation status |
|---|---:|---|
| Before 01/01/2025 | 17 percent | Confirmed from Tax Authority transition guidance |
| From 01/01/2025 onward | 18 percent | Confirmed from Tax Authority VAT history and 2026 professional tax summaries |

Use the invoice issue date as the default rate-selection key. Keep historical invoices immutable. When the taxable event differs from the issue date, require accountant review before final issue.

### VAT example

```json
{
  "issue_date": "2026-06-01",
  "subtotal": "200.00",
  "vat_rate": "0.18",
  "vat_amount": "36.00",
  "total": "236.00"
}
```

## Invoice allocation threshold reference

The 2026 threshold was corrected during the web-validated pass. Do not use a full-year ₪15,000 threshold for 2026.

| Effective date | Threshold before VAT | Notes |
|---|---:|---|
| 05/05/2024 | ₪25,000 | Pilot and first live stage |
| 01/01/2025 | ₪20,000 | Tax Authority service page |
| 01/01/2026 | ₪10,000 | Corrected from older API-document schedule |
| 01/06/2026 | ₪5,000 | Tax Authority service page, updated 01/06/2026 |

Request an allocation number before final issue when all operational conditions apply:

- Document is a tax invoice or tax invoice receipt.
- Subtotal before VAT reaches the effective threshold for the issue date.
- The invoice includes VAT and is issued to a customer registered as an authorized dealer.
- The customer needs the allocation number to deduct input VAT, or the business policy requests allocation for additional invoices.

## Manual allocation service

The Tax Authority manual service applies when the issuer uses invoice books or software not connected to the service. The service page states that the service is free of charge.

Minimum data to collect for a manual request:

```json
{
  "customer_authorized_dealer_number": "514324995",
  "invoice_number": "SUB-2026-000001",
  "amount_before_vat": "10000.00",
  "vat_amount": "1800.00",
  "transaction_description": "Monthly maintenance service"
}
```

## SHAAM API model

The package does not submit directly to the Tax Authority. It produces local workflow payloads and accepts sync or async transport callables. Direct SHAAM submission requires a registered software house, OAuth2 credentials, and a field mapper to the current official schema.

Public API documents confirm OAuth2 User Restricted authorization and v2 lowercase input fields. Map local camelCase helper fields to the current official lowercase schema before calling the real endpoint.

### Confirmed approval endpoints

| Service | Environment | Public path |
|---|---|---|
| Approval v2 | Sandbox | `https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval` |
| Approval v2 | Production | `https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval` |
| Multi Approval v2 | Sandbox | `https://ita-api.taxes.gov.il/shaam/tsandbox/Multi-invoices/v2/MultiApproval` |

Production Multi Approval and decision-service endpoints must be checked in the developer portal before use. Public English and Hebrew PDFs conflict on the held-invoice decision-service path.

### Official-style field examples

The public v2 approval table includes lowercase fields such as:

```json
{
  "invoice_id": "SUB-2026-000001",
  "invoice_type": 305,
  "vat_number": "000000018",
  "invoice_reference_number": "2026000001",
  "customer_vat_number": "514324995",
  "invoice_date": "2026-06-01",
  "payment_amount": 10000.0,
  "vat_amount": 1800.0
}
```

Do not copy this example into production without the current document-type code table and developer-portal schema.

### Local helper allocation request

```json
{
  "environment": "sandbox",
  "clientTransactionId": "TX-2026-0001",
  "softwareId": "registered-software-id",
  "business": {
    "taxId": "000000018"
  },
  "invoice": {
    "invoiceId": "SUB-2026-000001",
    "documentType": "tax_invoice",
    "issueDate": "2026-06-01",
    "currency": "ILS",
    "customer": {
      "name": "Acme Israel Ltd",
      "taxId": "514324995"
    },
    "amounts": {
      "subtotal": "10000.00",
      "vatAmount": "1800.00",
      "total": "11800.00"
    },
    "lines": [
      {
        "description": "Monthly maintenance service",
        "quantity": "1.00",
        "unitPrice": "10000.00",
        "vatRate": "0.18",
        "exempt": false
      }
    ]
  }
}
```

### Local helper allocation response

```json
{
  "allocationNumber": "202606010000000001",
  "status": "approved",
  "requestId": "REQ-123456"
}
```

### Official response patterns to support

The public API examples show successful responses that include `status`, `confirmation_number`, and `approved` for approval calls, and `Confirmation_Number` for retrieval calls. Support both normalized local keys and official-style keys when parsing responses.

```json
{
  "status": 200,
  "confirmation_number": "20240710181226272191063077",
  "approved": true
}
```

```json
{
  "Status": 200,
  "Confirmation_Number": "20240704061109183186068226"
}
```

## Error reference

| HTTP status | Meaning | Retry | Action |
|---:|---|---|---|
| 400 | Bad request or logical validation error | No | Correct payload and schema errors |
| 401 | Unauthorized or token failure | After credential refresh | Refresh OAuth2 token and retry once |
| 403 | Missing service permission | No | Check software-house, business, and user authorization |
| 404 | URI does not match a resource | No | Verify endpoint in developer portal |
| 406 | Permission or acceptability problem | No | Check VAT number and service permission |
| 422 | Schema mismatch | No | Validate every object against current schema |
| 429 | Gateway throttling, if returned by an intermediary | Yes | Back off with jitter and preserve idempotency |
| 500 | Internal server error | Yes | Retry through a queue; keep invoice unissued until resolved |

## Held-invoice alternatives

When an allocation number is not returned because of a substantive hold, present the four alternatives described by the public API documents:

1. Cancel or abandon the invoice.
2. Continue issuing without an allocation number and show the required notice that input VAT must not be deducted for the invoice.
3. Use reverse charge after customer consent and follow the special allocation flow.
4. Request a hearing and repeat the allocation request if approved.

## Idempotency and audit storage

Use a stable idempotency key before any external submission:

```text
{business_tax_id}:{invoice_id}:{issue_date}:{total}
```

Store these records before final issue:

- Original invoice candidate.
- Request body submitted to an adapter or official API.
- Raw response body.
- Allocation number or rejection details.
- Rightmost 9 digits when used for printing and PCN874 reporting.
- User choice for held-invoice alternatives.
- Timestamp, environment, credential profile, and retry count.

## Webhooks

No webhook event names are documented in the checked public SHAAM API files, and this package does not expose webhook handlers. Polling, queue workers, or gateway callbacks may be added by an external adapter, but must not invent SHAAM event names.
