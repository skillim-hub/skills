# API and Israeli Regulation Reference

This reference lists common Israeli integration and regulatory touchpoints for a Hebrew customer-service chat agent. It is not legal, tax, accounting, medical, or regulatory advice. Verify current requirements with official sources and professional advisers before production.

## Israeli regulatory map

| Area | Source to verify | Why it matters | Agent rule |
|---|---|---|---|
| Consumer protection | Consumer Protection Law, 5741-1981; transaction cancellation regulations | Cancellation periods, disclosure, returns, distance selling | Explain only approved business policy; escalate disputed rights |
| Privacy | Protection of Privacy Law, 5741-1981; Privacy Protection Regulations (Data Security), 5777-2017 | personal data, deletion/export, security | collect minimum data; escalate privacy requests |
| Accessibility | Equal Rights for Persons with Disabilities Law and service accessibility regulations | accessible digital service and alternate channels | offer alternate route and escalate accessibility complaints |
| VAT/accounting | VAT Law and Israel Tax Authority bookkeeping/invoicing rules | חשבונית מס/קבלה, עוסק מורשה, עוסק פטור, VAT | use accounting system; no tax advice |
| Marketing messages | Communications Law anti-spam provisions | opt-in for SMS/email/WhatsApp marketing | do not subscribe without approved consent |
| Payments | payment provider contracts, Bank of Israel context, PCI DSS where cards are handled | card data, secure links, disputes | never collect full card data in chat |
| Regulated sectors | health, finance, insurance, law, food, education | professional advice or safety duties | hand off to qualified owner |

## Normalized API wrapper

```json
{
  "ok": true,
  "data": {},
  "customer_safe_message": null,
  "internal_error": null,
  "retryable": false,
  "risk_flags": []
}
```

Failure example:

```json
{
  "ok": false,
  "data": null,
  "customer_safe_message": "כרגע לא הצלחתי לבדוק את זה במערכת. אעביר לנציג לבדיקה.",
  "internal_error": "ORDER_API_TIMEOUT",
  "retryable": true,
  "risk_flags": ["tool_failure"]
}
```

## Live-source validation notes

The examples below use internal placeholder endpoints such as `/api/orders`, `/api/tracking`, `/api/payments/link`,
`/api/accounting/documents`, and `/api/support/tickets`. Treat them as implementation scaffolding, not official Israeli
government, carrier, payment-provider, accounting-system, or helpdesk endpoints.

Verified production notes as of 03/06/2026:

- The general Israeli VAT rate is 18% from 01/01/2025. Keep VAT values in the accounting system as `system_default`; do not hard-code tax decisions in chat logic.
- Official WhatsApp Business Platform delivery uses Meta/Graph endpoints such as `POST /{Version}/{Phone-Number-ID}/messages`; the package's chat event shape is an internal normalized event.
- Official WhatsApp webhook terminology includes the `messages` webhook and status-related payloads; package error names such as `TEMPLATE_REQUIRED` are internal normalized errors.
- Israel Post exposes public tracking pages; the package's `/api/tracking` path is an internal adapter placeholder.
- PCI DSS is the correct term for payment-card data security. Do not write `PCDSS`.

## Order status API

```http
GET /api/orders/10493
Authorization: Bearer <server-token>
Accept: application/json
```

```json
{
  "order_id": "10493",
  "status": "shipped",
  "status_he": "נשלחה",
  "created_at": "2026-05-28T10:22:00+03:00",
  "estimated_delivery_date": "05/06/2026",
  "tracking_number": "IL123456789",
  "carrier": "Israel Post",
  "late": false
}
```

Customer-safe wording:

```text
ההזמנה נשלחה. מספר המעקב הוא IL123456789, והערכת המסירה היא 05/06/2026.
```

| HTTP status | Meaning | Agent action |
|---|---|---|
| 400 | invalid order ID | ask for order number again |
| 401/403 | authorization failure | hand off internal issue |
| 404 | order not found | ask for phone/email or hand off |
| 409 | identity mismatch | verify approved field; do not reveal details |
| 429 | rate limited | retry later or hand off |
| 500 | internal error | hand off with safe apology |

## Shipping/tracking API

```http
GET /api/tracking/IL123456789
Authorization: Bearer <server-token>
Accept: application/json
```

```json
{
  "tracking_number": "IL123456789",
  "carrier": "Israel Post",
  "events": [
    {"date": "03/06/2026", "status": "in_transit", "status_he": "בדרך ליעד", "location": "מרכז מיון"}
  ],
  "estimated_delivery_date": "06/06/2026"
}
```

| Error | Meaning | Agent action |
|---|---|---|
| TRACKING_NOT_FOUND | carrier has no record | escalate if order is older than SLA |
| CARRIER_TIMEOUT | carrier unavailable | offer human follow-up if urgent |
| DELIVERED_DISPUTED | customer says not received | escalate high urgency |
| ADDRESS_ISSUE | address problem | collect safe contact details and hand off |

## Payment API

Use server-side providers only. Never request full card numbers, CVV, passwords, or one-time codes.

```http
POST /api/payments/link
Authorization: Bearer <server-token>
Content-Type: application/json
```

```json
{
  "customer_id": "cust_123",
  "amount_ils_agorot": 35000,
  "description": "שיחת ייעוץ",
  "expires_at": "10/06/2026T23:59:00+03:00"
}
```

```json
{
  "payment_link_id": "pl_789",
  "url": "https://pay.example.co.il/pl_789",
  "amount": "₪350.00",
  "expires_at": "10/06/2026 23:59"
}
```

| Error | Meaning | Agent action |
|---|---|---|
| PAYMENT_DECLINED | issuer declined | suggest another approved method; do not diagnose |
| DUPLICATE_CHARGE_CLAIM | customer reports double charge | escalate to billing |
| UNAUTHORIZED_CHARGE | customer denies charge | escalate high urgency |
| LINK_EXPIRED | payment link expired | create new link only if allowed |
| REFUND_REQUIRED | refund flow needed | human approval |

## Invoice/receipt API

Use the accounting system as source of truth for VAT and document type.

```http
POST /api/accounting/documents
Authorization: Bearer <server-token>
Content-Type: application/json
```

```json
{
  "order_id": "10493",
  "document_type": "tax_invoice_receipt",
  "customer": {
    "legal_name": "דנה לוי בע״מ",
    "company_id": "516123456",
    "email": "billing@example.co.il"
  },
  "lines": [
    {"description": "שירות ייעוץ", "quantity": 1, "unit_price_ils": 250, "vat_rate": "system_default"}
  ]
}
```

```json
{
  "document_id": "INV-2026-0091",
  "document_type_he": "חשבונית מס/קבלה",
  "issued_date": "03/06/2026",
  "total": "₪292.50",
  "pdf_url": "https://accounting.example.co.il/doc/INV-2026-0091.pdf"
}
```

| Error | Meaning | Agent action |
|---|---|---|
| MISSING_BILLING_DETAILS | required field missing | ask only for missing fields |
| INVALID_COMPANY_ID | invalid ח.פ./ע.מ. | ask customer to recheck |
| VAT_STATUS_UNKNOWN | tax status missing | escalate to accounting |
| DOCUMENT_ALREADY_ISSUED | duplicate document exists | send existing if allowed |
| CREDIT_NOTE_REQUIRED | refund/credit note needed | escalate to accounting |

## Handoff/helpdesk API

```http
POST /api/support/tickets
Authorization: Bearer <server-token>
Content-Type: application/json
```

```json
{
  "customer_language": "he",
  "intent": "late_delivery",
  "priority": "high",
  "customer": {"name": "דנה לוי", "phone": "+972501234567"},
  "summary": "הזמנה 10493 איחרה מעבר ל-SLA.",
  "risk_flags": ["late_delivery", "angry_customer"]
}
```

```json
{"ticket_id": "SUP-4551", "status": "open", "assigned_team": "Operations", "sla_reply_by": "03/06/2026 17:00"}
```

| Error | Meaning | Agent action |
|---|---|---|
| QUEUE_UNAVAILABLE | ticket system down | use backup email or retry queue |
| MISSING_CONTACT | cannot contact customer | ask preferred contact channel |
| PRIORITY_INVALID | bad routing value | use default priority and log |
| ATTACHMENT_TOO_LARGE | upload failed | ask for smaller file or alternate channel |

## WhatsApp or chat channel event

Incoming normalized event:

```json
{"channel": "whatsapp", "from": "+972501234567", "timestamp": "2026-06-03T10:00:00+03:00", "text": "איפה ההזמנה שלי?"}
```

Outgoing message:

```json
{"to": "+972501234567", "type": "text", "text": {"body": "כדי לבדוק סטטוס הזמנה צריך מספר הזמנה או טלפון ששויך להזמנה."}}
```

| Error | Meaning | Agent action |
|---|---|---|
| TEMPLATE_REQUIRED | session window closed | use approved template or human route |
| USER_OPTED_OUT | customer opted out | do not send outbound message |
| MEDIA_UNSUPPORTED | unsupported attachment | ask for supported format |
| RATE_LIMITED | channel limit | queue retry and log |

## Security requirements

- Store tokens only in server-side secret storage.
- Use TLS for every API call.
- Redact card-like strings, ID numbers, OTPs, health details, and passwords.
- Enforce least privilege for each tool.
- Audit refund, invoice, deletion, and export requests.
- Validate all tool inputs with schemas.
- Treat customer text and uploaded files as untrusted.
- Return only customer-safe errors.
