# API and Regulation Reference

This reference maps the scheduler to Israeli operational integrations and regulatory touchpoints. Verify current official documentation before production integration because endpoints, authentication rules, tax thresholds, and retention rules can change.

Access date for the v3 validation pass: 2026-06-04.

## Verified operational constants

| Topic | Verified value for this package | Use inside the scheduler | Source class |
|---|---:|---|---|
| Standard VAT rate | 18% from 01/01/2025 and still treated as current in 2026 | Display as an informational reference only | Israel Tax Authority, Knesset, current tax summaries |
| Israel Invoices allocation threshold | ₪20,000 in 2025; ₪10,000 from 01/01/2026; ₪5,000 from 01/06/2026, before VAT | Flag accounting review for commercial B2B invoices; do not issue official invoices | Israel Tax Authority |
| Bank of Israel representative-rate API base | `https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS` | Use only where a lease explicitly has a foreign-currency clause | Bank of Israel |
| Residential rent exemption ceiling | ₪5,654 per month for 2026 | Reference for accountant review only; do not choose a tax route | Israel Tax Authority and secondary legal-rights reference |
| Rental income 10% route deadline | Pay no later than 31/01 of the year after the rental year, subject to current rules | Month-end checklist item only | Israel Tax Authority |
| Privacy and data security | Tenant data can be a database or personal-information processing context | Minimize personal data, restrict access, and keep logs | Privacy Protection Authority |

## Integration categories

| Category | Israeli touchpoint | Typical use | Production note |
|---|---|---|---|
| Government open data | Data.gov.il CKAN Action API | Address, locality, and public dataset lookup | Validate dataset freshness before relying on it. |
| Bank of Israel reference data | Representative exchange rates and the series database API | Convert foreign-currency lease clauses if explicitly required | Store the original ₪ amount and conversion source. |
| Israel Tax Authority services | Israel Invoices, VAT, income tax, and bookkeeping workflows | Prepare accounting review packs | Let approved accounting software issue official documents. |
| Payment collection | Israeli bank transfer, standing order, card processor, or Masav workflow | Reconcile rent payments | Do not store full card or bank credentials. |
| Messaging | SMS provider, email service, or documented business messaging channel | Send reminders and repair updates | Log opt-out and route legal notices to manual review. |
| Municipal services | Arnona account portals or municipal forms | Track municipal account references | Treat portal automation as sensitive and permission-bound. |
| Privacy and security | Protection of Privacy Law and data-security regulations | Tenant data minimization and access control | Review database registration or notice obligations before scaling. |

## Government open data example

Data.gov.il exposes CKAN-style endpoints. The scheduler should use public data only for validation and enrichment, not as the sole source of a lease record.

Example request for a public dataset search:

```http
GET /api/3/action/package_search?q=addresses HTTP/1.1
Host: data.gov.il
Accept: application/json
```

Example response shape:

```json
{
  "success": true,
  "result": {
    "count": 2,
    "results": [
      {
        "name": "address-dataset",
        "title": "Address dataset",
        "metadata_modified": "2026-01-15T09:00:00"
      }
    ]
  }
}
```

Common errors:

| Status | Meaning | Handling |
|---|---|---|
| 400 | Invalid query | Simplify the search term. |
| 404 | Dataset not found | Fall back to manual address entry. |
| 429 | Rate limit | Back off and retry later. |
| 500 | Service failure | Queue validation for later. |

## Bank of Israel reference data

Use Bank of Israel representative-rate data only when the lease explicitly includes a foreign-currency clause. The representative rate is an indicator and is not a legally binding exchange rate unless the parties agreed to use it.

Example request shape for the official series database base path:

```http
GET /FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0?format=csvfile HTTP/1.1
Host: edge.boi.gov.il
Accept: text/csv, application/json
```

Example adapter response shape:

```json
{
  "currency": "USD",
  "date": "2026-01-05",
  "rate_ils": "3.6500",
  "source": "Bank of Israel representative exchange rates",
  "retrieved_at": "2026-01-05T10:30:00Z"
}
```

Errors:

| Code | Cause | Fix |
|---|---|---|
| `RATE_NOT_PUBLISHED` | No rate for date | Use the closest contractually permitted date only after manual review. |
| `CURRENCY_UNSUPPORTED` | Currency not available | Keep the lease clause for professional review. |
| `SOURCE_UNVERIFIED` | Endpoint or data source changed | Stop automatic conversion. |

## Israel Tax Authority API registration

Tax Authority API access requires registration of the software house and developers before entering the developer portal and viewing full documentation for each API. Keep sandbox and production credentials separate.

Checklist:

1. Register the software house and developer identities.
2. Obtain sandbox access before production access.
3. Use OAuth2 or the current official authentication method published in the developer portal.
4. Keep credentials outside JSON tenant stores.
5. Log request identifiers, not full personal or bank details.

## Israel Invoices allocation reference

Use this only as an accounting handoff reference. The scheduler must not issue tax invoices or decide whether a tenant may deduct input tax.

Current validated thresholds for allocation-number review:

| Effective date | Threshold before VAT | Operational action |
|---|---:|---|
| 01/01/2025 | ₪20,000 | Flag qualifying commercial B2B tax invoices for allocation-number workflow. |
| 01/01/2026 | ₪10,000 | Flag qualifying commercial B2B tax invoices above this amount before VAT. |
| 01/06/2026 | ₪5,000 | Flag qualifying commercial B2B tax invoices above this amount before VAT. |

Official endpoint path validated from the Israel Invoices API specification:

```http
POST /shaam/production/Invoices/v2/Approval HTTP/1.1
Host: ita-api.taxes.gov.il
Content-Type: application/json
Authorization: Bearer <token>
```

Sandbox path pattern:

```http
POST /shaam/tsandbox/Invoices/v2/Approval HTTP/1.1
Host: ita-api.taxes.gov.il
Content-Type: application/json
Authorization: Bearer <token>
```

Request example for an external accounting adapter:

```json
{
  "invoice_id": "INV-2026-00042",
  "invoice_date": "2026-06-15",
  "supplier_vat_id": "512345678",
  "customer_vat_id": "514444444",
  "amount_before_vat": "6000.00",
  "vat_amount": "1080.00",
  "currency": "ILS"
}
```

Response example shape:

```json
{
  "approved": true,
  "allocation_number": "123456789",
  "request_id": "ita-req-2026-00042",
  "message": "Allocation number returned by approved accounting integration"
}
```

Error table:

| Code | Cause | Handling |
|---|---|---|
| `AUTH_REQUIRED` | Missing or expired OAuth token | Refresh through the approved flow. |
| `INVALID_INVOICE_ID` | Invoice id is missing or not unique | Stop and correct the accounting record. |
| `THRESHOLD_NOT_REQUIRED` | Amount is below the current threshold | Document why allocation was not required. |
| `ALLOCATION_HELD` | Tax Authority held or did not return allocation | Present the official alternatives inside the accounting system. |
| `PRODUCTION_NOT_APPROVED` | Software house lacks production approval | Do not retry with tenant data; complete registration. |

## Tax and bookkeeping workflow

Regulatory touchpoints to review with a qualified professional:

| Topic | Israeli reference area | Scheduler behavior |
|---|---|---|
| VAT | Value Added Tax Law and Israel Tax Authority guidance | Store `vat_registered`; do not decide VAT liability. |
| Residential rental income | Income Tax Ordinance, exemption ceiling, 10% route, and full-rate route | Export rent totals; do not choose a tax track. |
| Bookkeeping | Instructions for managing books and approved accounting software | Prepare source data; do not issue official documents. |
| Invoice or receipt | Israel Invoices services and accounting software requirements | Keep payment references for transfer into approved systems. |
| Residential lease | Rental and Lending Law, contracts law, and consumer-protection context | Avoid legal notices and deposit deductions without review. |
| Privacy | Protection of Privacy Law and data-security obligations | Minimize tenant personal data and restrict access. |
| Arnona | Local authority property tax | Store account references only where useful for internal matching. |

Example accounting export produced by the client:

```json
{
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  },
  "currency": "ILS",
  "vat_registered": false,
  "paid_rent": [
    {
      "id": "rent_123",
      "due_date": "2026-01-05",
      "amount_ils": "5200.00",
      "status": "paid",
      "paid_date": "2026-01-03",
      "reference": "bank-2026-001"
    }
  ],
  "totals": {
    "paid_rent_ils": "5200.00"
  }
}
```

## Payment reconciliation adapter

Request example:

```json
{
  "charge_id": "rent_123",
  "expected_amount_ils": "5200.00",
  "tenant_name": "דנה כהן",
  "due_date": "2026-01-05",
  "bank_reference": "bank-2026-001"
}
```

Response example:

```json
{
  "matched": true,
  "paid_amount_ils": "5200.00",
  "paid_date": "2026-01-03",
  "match_score": 0.98,
  "manual_review": false
}
```

Errors:

| Code | Cause | Handling |
|---|---|---|
| `AMOUNT_MISMATCH` | Amount differs from charge | Mark partial or manual review. |
| `REFERENCE_MISSING` | Transfer reference not found | Ask tenant for proof of transfer. |
| `DUPLICATE_MATCH` | One transfer matches multiple charges | Stop and reconcile manually. |
| `CREDENTIAL_SCOPE` | Bank credentials lack permission | Do not request wider access than needed. |

## Messaging adapter

Tenant-facing messages are operational notices. Do not use automated messages for eviction, deposit deductions, entry without consent, waiver claims, or disputed debt threats.

Request example:

```json
{
  "tenant_id": "ten_123",
  "channel": "sms",
  "to": "0501234567",
  "subject": "תזכורת לתשלום שכר דירה",
  "body": "שלום דנה כהן, תזכורת לתשלום שכר דירה בסך ₪5200.00 עד 05/01/2026."
}
```

Response example:

```json
{
  "accepted": true,
  "provider_message_id": "msg-123",
  "queued_at": "2026-01-02T08:00:00Z"
}
```

Errors:

| Code | Cause | Handling |
|---|---|---|
| `INVALID_PHONE` | Phone is not in Israeli format | Correct contact details. |
| `OPT_OUT` | Tenant opted out of channel | Use another documented channel. |
| `TEMPLATE_REVIEW_REQUIRED` | Message contains sensitive legal wording | Route to manual approval. |
| `DELIVERY_FAILED` | Provider rejected or failed delivery | Log failure and retry through another allowed channel. |

## Webhook event names

No external webhook names are implemented or referenced by this local-first package. Use internal event labels only when adding an adapter:

| Internal event | Use |
|---|---|
| `rent.charge.created` | A rent charge was generated. |
| `rent.payment.recorded` | A payment was reconciled. |
| `maintenance.task.created` | A maintenance issue was opened. |
| `maintenance.task.completed` | A maintenance issue was closed. |
| `communication.logged` | A tenant communication was recorded. |

## Privacy and security controls

1. Minimize personal data.
2. Store only the last four digits of identity numbers unless a lawful need exists.
3. Restrict access to JSON stores and backups.
4. Keep an access log when moving to shared storage.
5. Avoid sending sensitive details through unsecured channels.
6. Delete stale tenant data according to retention policy.
7. Review data exports before sending them to accountants, contractors, or service providers.
8. Check whether database registration, notice, or security-level obligations apply before production use.

## Production integration checklist

1. Confirm official endpoint, authentication method, and terms of use.
2. Keep sandbox and production credentials separate.
3. Add timeouts, retries, and idempotency keys.
4. Validate Hebrew encoding with `ensure_ascii=False`.
5. Capture request id, response id, and failure reason.
6. Mask tenant contact details in logs.
7. Require manual approval for legal, deposit, or entry-related notices.
8. Run reconciliation reports before month-end close.
9. Re-check the verified thresholds in `references/verification-log.md` before enabling commercial invoice workflows.
