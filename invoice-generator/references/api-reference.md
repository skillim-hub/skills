# API and Regulation Reference

Use this reference to map helper output to official Israeli accounting and allocation-number workflows. Confirm credentials, live schemas, and authorization scopes in the Israel Tax Authority developer portal before production use.

## Web-validated facts as of 01/06/2026

| Topic | Current handling | Production note |
|---|---|---|
| VAT | Default standard VAT is 18% from 01/01/2025. Dates before 01/01/2025 use 17% in the helper. | Recheck the statutory rate before every production release. |
| Allocation threshold | The threshold is ₪20,000.00 for 2025, ₪10,000.00 from 01/01/2026, and ₪5,000.00 from 01/06/2026. | The test suite covers both 2026 dates because the threshold changes during the year. |
| Threshold comparison | Allocation logic uses amount before VAT that is greater than the active threshold, not equal to it. | Official Hebrew wording uses `עולה על`, so exactly ₪5,000.00 on 01/06/2026 is below the trigger. |
| Eligible document types | The helper checks `tax_invoice` and `tax_invoice_receipt` only. | Receipts and credit notes do not trigger allocation in this helper. |
| VAT component | Allocation requires a non-zero VAT component. | Zero-rate and exempt transactions do not trigger allocation in this helper. |
| Customer status | `customer_type: business` models an Israeli VAT-registered business customer. | Supply the customer's 9-digit VAT/dealer number for official requests. |
| Issuer status | `issuer.status: morshe` or `company` can trigger allocation. `patur` cannot issue tax invoices in the modeled workflow. | Keep the official registration effective date in the business file. |
| Webhooks | No official invoice-allocation webhook event names are modeled. | The referenced official material describes request/response API flows, not webhook events. |

## Allocation threshold schedule included in code

| Effective date | Threshold before VAT | Source status |
|---|---:|---|
| 05/05/2024 | ₪25,000.00 | Historical rollout threshold. |
| 01/01/2025 | ₪20,000.00 | Confirmed in current Gov.il service text. |
| 01/01/2026 | ₪10,000.00 | Corrected against older API PDFs that still show the previous ₪15,000.00 plan. |
| 01/06/2026 | ₪5,000.00 | Current threshold on 01/06/2026. |

The helper uses the latest configured effective-date threshold for later dates. Override `DEFAULT_SHAAM_THRESHOLDS` only after checking current official publications.

## Official API hosts and endpoint paths to verify during integration

| Purpose | Sandbox | Production | Notes |
|---|---|---|---|
| Single invoice allocation approval | `https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval` | `https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval` | Official API specification marks this service as `Approval` version V2.0 beta. |
| Batch allocation approval | `https://ita-api.taxes.gov.il/shaam/tsandbox/Multi-invoices/v2/MultiApproval` | `https://ita-api.taxes.gov.il/shaam/production/Multi-invoices/v2/MultiApproval` | Use only after validating the current production spelling and authorization. |
| Invoice-information by allocation number | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/details` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/details` | Customer-side verification flow. |
| Allocation-number lookup by details | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/confirmationNumber` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber` | Customer-side lookup flow. |
| Held-invoice decision update | `/InvoiceDecisionApi/v1/Cancel`, `/Continue`, `/FurtherObjection` under the SHAAM host | Same path pattern under production host | Use only when the Tax Authority decision flow returns a held invoice and the user chooses an allowed alternative. |

## Semantic allocation request payload emitted by the helper

The helper emits a semantic payload for validation, logging, and adapter development. Do not assume this JSON is a byte-for-byte official schema. Build a production adapter that maps it to the latest official schema, including official field names, OAuth2 headers, software registration number, user fields, and any current mandatory values.

### Semantic request example

```json
{
  "document": {
    "type": "tax_invoice",
    "number": "INV-2026-0042",
    "issue_date": "2026-06-15",
    "currency": "ILS"
  },
  "issuer": {
    "name": "יעל כהן ייעוץ",
    "tax_id": "123456789",
    "status": "morshe"
  },
  "customer": {
    "name": "חברת לקוח בע\"מ",
    "tax_id": "515555555",
    "customer_type": "business"
  },
  "totals": {
    "amount_before_vat": "18,000.00",
    "vat_rate_default": "0.18",
    "vat": "3,240.00",
    "total": "21,240.00"
  },
  "allocation": {
    "required": true,
    "threshold": "5,000.00",
    "allocation_number": ""
  },
  "lines": [
    {
      "description": "ייעוץ אסטרטגי",
      "quantity": "40",
      "unit": "שעה",
      "unit_price": "450.00",
      "net": "18,000.00",
      "vat_rate": "0.18"
    }
  ]
}
```

### Adapter mapping checklist

| Semantic helper field | Official-schema target to verify | Required action |
|---|---|---|
| `document.number` | `invoice_reference_number` | Preserve the official document reference. |
| `document.issue_date` | `invoice_date` | Send `YYYY-MM-DD`. |
| Internal document id | `invoice_id` | Generate one stable single-value id per official request. |
| `issuer.tax_id` | `vat_number` | Send the issuer's VAT/dealer number. |
| `customer.tax_id` | `customer_vat_number` | Required for B2B allocation requests. |
| `totals.amount_before_vat` | Official payment amount before VAT field | Validate the exact name in the current specification. |
| `totals.vat` | Official VAT amount field | Validate rounding and currency rules. |
| `totals.total` | Official total including VAT field | Validate against official schema. |
| Software registration | `accounting_software_number` | Add in the production adapter; the helper does not invent it. |
| Service operator | `user_id` or `user_name` | Add according to the authenticated user and current schema. |

## Response handling

### Allocation response example for the adapter layer

```json
{
  "allocation_number": "20260601061109183186068226",
  "status": "approved",
  "document_number": "INV-2026-0042",
  "issued_at": "2026-06-15T10:30:00+03:00"
}
```

Store the full allocation number, the 9 right-most digits when required for reporting, the request payload, the response payload, and the final issued document. Do not reuse an allocation number across unrelated documents.

## Sync client example

```python
from invoice_generator import (
    DocumentSpec,
    ShaamClient,
    SHAAM_SANDBOX_BASE_URL,
    sample_tax_invoice,
)

document = DocumentSpec.from_dict(sample_tax_invoice())
document.validate().raise_for_errors()
client = ShaamClient(base_url=SHAAM_SANDBOX_BASE_URL, access_token="token")
# response = client.request_allocation(document)
```

## Async client example

```python
import asyncio
from invoice_generator import DocumentSpec, ShaamClient, SHAAM_SANDBOX_BASE_URL, sample_tax_invoice

async def run():
    document = DocumentSpec.from_dict(sample_tax_invoice())
    client = ShaamClient(base_url=SHAAM_SANDBOX_BASE_URL, access_token="token")
    return await client.request_allocation_async(document)

# response = asyncio.run(run())
```

## Headers used by the helper client

| Header | Value |
|---|---|
| `Authorization` | `Bearer <token>` |
| `Content-Type` | `application/json` |
| `Idempotency-Key` | `<issuer tax id>:<document type>:<document number>:<issue date>` |

## Error table

| Error or status | Meaning | Corrective action |
|---|---|---|
| 400 invalid schema | Field mapping does not match the official schema. | Update the adapter and run fixture tests. |
| 401 unauthorized | Missing, expired, or invalid OAuth2 token. | Refresh credentials and retry only after authentication succeeds. |
| 403 forbidden | Token lacks permission for the issuer, action, or environment. | Confirm authorization, environment, and delegated authority. |
| 404 endpoint not found | Wrong base URL or endpoint path. | Confirm sandbox or production URL from the developer portal. |
| 406 not acceptable | Header, permission, or VAT number context is unacceptable. | Compare headers and issuer/customer identifiers against the current specification. |
| 422 unprocessable entity | JSON shape or business values fail schema validation. | Correct dates, identifiers, totals, and mandatory fields. |
| 429 rate limit | Too many requests. | Back off and retry according to official limits. |
| 500 or 503 service failure | Remote service issue. | Retry with idempotency and keep an audit log. |

## Local validation messages

| Message | Meaning | Action |
|---|---|---|
| `osek patur cannot issue חשבונית מס or חשבונית מס/קבלה` | Issuer status conflicts with document type. | Use receipt workflow or update status only from the official change date. |
| `payment details are required for receipt documents` | Receipt lacks payment records. | Add `payments`. |
| `credit_note requires original_document_number` | Credit note has no source document reference. | Add original document number. |
| `customer.tax_id is needed for an official allocation-number request` | A B2B allocation request needs the customer's VAT/dealer number. | Add the customer's 9-digit identifier. |
| `SHAAM allocation number is required before final B2B tax-invoice issuance` | Allocation check matched the active threshold logic. | Request and store allocation before final issuance. |
| `foreign-currency documents should include an exchange-rate note` | Currency is not ILS and no exchange note exists. | Add exchange-rate source and date. |
