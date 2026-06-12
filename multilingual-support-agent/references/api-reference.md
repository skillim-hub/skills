# API and Regulation Reference

This skill is not tied to one mandatory external API. Use it as a neutral integration layer for Israeli support workflows that involve order systems, payment providers, courier systems, accounting platforms, CRM tools, WhatsApp Business platforms, email, and privacy processes.

Verify official sources before production use. The tables below cite common Israeli legal and operational reference points by subject and explain how to use them safely in support flows.

## Israeli reference map

| Area | Israeli reference to verify | Operational use | Unsafe output |
|---|---|---|---|
| VAT and accounting documents | Value Added Tax Law, 1975; Income Tax bookkeeping instructions; Israel Tax Authority guidance | Phrase receipt, tax invoice, tax invoice/receipt, and VAT-related replies. | Do not decide VAT status or document correction without accountant review. |
| Consumer cancellation and returns | Consumer Protection Law, 1981; Consumer Protection Regulations on transaction cancellation; Consumer Protection and Fair Trade Authority guidance | Route cancellation, refund, and return questions. | Do not confirm eligibility before checking product type, sales channel, dates, use, and exceptions. |
| Privacy | Protection of Privacy Law, 1981; Protection of Privacy Regulations on Data Security, 2017; Israel Privacy Protection Authority guidance | Handle access, correction, deletion, breach, and minimization workflows. | Do not confirm deletion or disclosure before identity verification and procedure completion. |
| Accessibility | Equal Rights for Persons with Disabilities Law, 1998; service-accessibility regulations and guidance | Keep support channels accessible and offer workable alternatives. | Do not force only one inaccessible channel. |
| Marketing and spam | Communications Law, 1982, section 30A | Separate service messages from marketing consent. | Do not subscribe a support customer to marketing without valid consent. |
| Payments | Payment-provider terms; Bank of Israel and card-network guidance where applicable; PCI-DSS practices | Verify duplicate charges, refunds, and chargebacks. | Do not request full payment-card data in chat. |
| Shipping and delivery | Courier provider terms; postal and delivery provider tracking APIs | Translate delivery events into clear customer updates. | Do not promise delivery time without verified courier data. |
| Business identity | Israel Corporations Authority or business registry sources where applicable | Validate business details for B2B documents. | Do not expose registry data unrelated to the transaction. |
| Government data access | gov.il and government open-data interfaces where applicable | Validate public procedural references. | Do not rely on stale cached regulation snippets for production policy. |


## Web-validated official and regulatory sources

Access date: 03/06/2026. Treat this table as a dated reference snapshot. Re-check the linked source before production automation, public policy pages, tax/accounting behavior, or legal-facing answers.

| Area | Current validated source | Confirmed support relevance |
|---|---|---|
| VAT rate | Knesset VAT order press release and 2026 PwC Israel tax summary | Standard VAT rate context is 18%; do not provide tax advice or decide VAT classification in chat. |
| Israel Invoices allocation thresholds | Israel Tax Authority allocation-number service and VAT implementation instruction 01/2025 | Thresholds for input-tax deduction are ₪20,000 for 2025, ₪10,000 from 01/01/2026, and ₪5,000 from 01/06/2026, excluding VAT. |
| Israel Invoices API | Israel Tax Authority API description, version 2.0, July 2024 | API paths and hosts are beta/implementation details; verify against the current developer portal before integration. |
| Consumer complaints and cancellation | Consumer Protection and Fair Trade Authority complaint service and Hebrew complaint page | Support flows may collect transaction details, documents, invoices, overcharge context, warranty issues, and cancellation questions. |
| Privacy | Privacy Protection Authority and Data Security Regulations references | Access, correction, deletion, breach, minimization, and database handling must follow identity verification and internal privacy procedure. |
| Accessibility | Equal Rights for Persons with Disabilities Law and accessibility guidance | Offer accessible alternatives and do not force an inaccessible-only support channel. |
| Marketing and spam | Ministry of Communications spam FAQ about Communications Law section 30A | Keep support replies separate from marketing consent. |
| Payments | Bank of Israel Consumer Enquiries and Inspections | For bank or credit-card disputes, collect safe details and direct unresolved issues to the relevant provider process. |
| Business registry | Israeli Corporations Authority company extract service | Use registry lookup only when business identity is needed for the transaction or B2B document. |

### Israel Tax Authority API paths to verify before integration

The July 2024 Israel Invoices API documents list these implementation paths. They are included as integration references, not as hard-coded constants. Validate current hosts and paths in the Tax Authority developer portal before production use.

| Service | Sandbox path shown in official documents | Production path shown in official documents | Notes |
|---|---|---|---|
| Single invoice allocation | `https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval` | `https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval` | OAuth2 user-restricted authorization; version/status V2.0 beta in the July 2024 document. |
| Multi-invoice allocation | `https://ita-api.taxes.gov.il/shaam/tsandbox/Multi-invoices/v2/MultiApproval` | `https://ita-api.taxes.gov.il/shaam/production/Multi-invoices/v2/MultiApproval` | Confirm batch limits and schema in the current portal. |
| Invoice details lookup | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/details` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/details` | Used by invoice receiver workflows. |
| Allocation-number lookup | `https://ita-api.taxes.gov.il/shaam/tsandbox/invoice-information/v1/confirmationNumber` | `https://openapi.taxes.gov.il/shaam/production/invoice-information/v1/confirmationNumber` | Used to retrieve an allocation number from invoice details. |
| Invoice decision after hold | Hebrew and English July 2024 PDFs differ between `Invoice-decision` and `InvoiceDecisionApi` path naming | Verify in the developer portal before use | Do not implement this path from documentation alone. |

### Webhooks

No Israeli regulatory webhook event names are required by this skill. If a CRM, helpdesk, payment provider, courier, WhatsApp platform, or accounting system emits webhooks, document provider-specific event names in the integration project and test them separately.

## Core data contract

### Support request

```json
{
  "conversation_id": "conv_12345",
  "channel": "whatsapp",
  "environment": "sandbox",
  "customer_message": "המשלוח שלי עדיין לא הגיע",
  "customer_language_hint": "he",
  "context": {
    "order_id": "IL-1001",
    "customer_name": "דנה",
    "email": "dana@example.com",
    "phone": "0500000000",
    "last4": "1234",
    "amount": 249.9,
    "purchase_date": "05/06/2026"
  }
}
```

### Support analysis response

```json
{
  "case_id": "msa_7c12a63e7c1a",
  "language": "he",
  "intent": "delivery_status",
  "risk": "medium",
  "reply": "שלום דנה, כדי לבדוק את סטטוס המשלוח יש לשלוח מספר הזמנה. לאחר אימות הפרטים תישלח תשובה עם הצעד הבא.",
  "internal_note": "case_id=msa_7c12a63e7c1a; intent=delivery_status; risk=medium; channel=whatsapp",
  "missing_fields": [],
  "escalation": null
}
```

## Recommended API envelope

Use a consistent envelope when connecting this skill to a CRM or helpdesk.

### Create case

Request:

```http
POST /support-cases
Content-Type: application/json
Idempotency-Key: conv_12345_first_message
```

```json
{
  "message": "I was charged twice for order IL-1001",
  "context": {
    "order_id": "IL-1001",
    "last4": "1234"
  }
}
```

Response:

```json
{
  "case_id": "msa_2e4b23c9c1ac",
  "environment": "sandbox",
  "analysis": {
    "language": "en",
    "intent": "payment_issue",
    "risk": "medium",
    "missing_fields": [],
    "escalation": null
  }
}
```

### Add message

Request:

```http
POST /support-cases/msa_2e4b23c9c1ac/messages
Content-Type: application/json
```

```json
{
  "message": "Please send the update to dana@example.com",
  "context": {
    "email": "dana@example.com"
  }
}
```

Response:

```json
{
  "case_id": "msa_2e4b23c9c1ac",
  "analysis": {
    "language": "en",
    "intent": "general_support",
    "risk": "low",
    "reply": "Hello, thank you for contacting support. Send more details so the request can be handled accurately."
  }
}
```

## Integration examples

### Courier status lookup

Request to a courier abstraction:

```http
GET /shipments?order_id=IL-1001
Accept: application/json
```

Response:

```json
{
  "order_id": "IL-1001",
  "tracking_number": "TRK123",
  "status": "in_transit",
  "last_event_at": "03/06/2026T10:15:00+03:00",
  "estimated_delivery_date": "06/06/2026"
}
```

Customer wording:

```text
The delivery is currently in transit. The latest verified update was received on 03/06/2026. If there is no progress by 06/06/2026, the case should be checked again with the courier.
```

### Accounting document request

Request to an accounting abstraction:

```http
POST /accounting/documents/request
Content-Type: application/json
```

```json
{
  "order_id": "IL-1001",
  "document_type": "tax_invoice_receipt",
  "recipient_email": "customer@example.com",
  "business_details": {
    "name": "Customer Ltd",
    "registration_number": "515000000",
    "address": "Tel Aviv"
  }
}
```

Response:

```json
{
  "request_id": "doc_req_1001",
  "status": "pending_accounting_review",
  "reason": "existing_document_correction"
}
```

Customer wording:

```text
The accounting document request was received. Because this is a correction to an existing document, it requires a check in the accounting system before sending.
```

### Payment duplicate charge check

Request:

```http
POST /payments/lookup
Content-Type: application/json
```

```json
{
  "order_id": "IL-1001",
  "last4": "1234",
  "amount": 249.9
}
```

Response:

```json
{
  "matches": [
    {
      "transaction_id": "pay_1001_a",
      "status": "captured",
      "amount": 249.9,
      "currency": "ILS"
    },
    {
      "transaction_id": "pay_1001_b",
      "status": "voided",
      "amount": 249.9,
      "currency": "ILS"
    }
  ]
}
```

Customer wording:

```text
The payment record will be checked against the payment provider. Only the last four digits are needed; do not send a full card number.
```

## Error table

| Code | Meaning | Customer-safe response | Internal action |
|---|---|---|---|
| `LANGUAGE_UNCERTAIN` | Language cannot be detected with confidence. | Ask which language is preferred. | Store preferred language when confirmed. |
| `MISSING_ORDER_ID` | Order-dependent request lacks order identifier. | Ask for the order number. | Do not search by name alone unless policy permits. |
| `PAYMENT_DATA_UNSAFE` | Customer sent or was asked for too much card data. | Ask not to send full card data; request last four digits only. | Redact sensitive data and review template. |
| `REGULATORY_RISK` | Legal, privacy, safety, or discrimination trigger detected. | Send holding wording if appropriate. | Escalate to an authorized person. |
| `ACCOUNTING_REVIEW_REQUIRED` | Accounting correction or VAT question requires review. | Explain that accounting review is required. | Route to accountant or accounting operator. |
| `COURIER_UNAVAILABLE` | Courier system is down or stale. | Explain that status will be checked again after system availability. | Retry and log provider error. |
| `POLICY_CONFLICT` | Template conflicts with current business policy. | Use neutral verification wording. | Update template library. |
| `RTL_RENDERING_RISK` | Mixed scripts may render incorrectly. | Use line-separated identifiers. | Preview in channel before rollout. |

## Data minimization rules

- Collect order number only when order lookup is required.
- Collect last four payment digits only for payment lookup.
- Avoid national identity numbers unless a verified process requires them.
- Do not repeat sensitive identifiers in customer replies.
- Store internal notes with redaction when possible.
- Apply retention rules from the business privacy procedure.

## Production verification

Before enabling automated sending, verify current requirements with current official sources and responsible professionals. Keep human review for high-risk tickets and for any answer that interprets law, tax, accounting, eligibility, compensation, or safety.
