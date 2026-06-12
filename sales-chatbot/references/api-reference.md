# API and Israeli Regulatory Reference

This reference lists integration points and regulatory touchpoints used by the Sales Chatbot skill. Treat examples as adapter patterns. Validate provider credentials, business-specific policy, and legal advice before production release.

## Validation status

The source-sensitive values below were web-validated on 03/06/2026 and are logged in `references/verification-log.md`.

| Item | Current package value | Operational note |
|---|---|---|
| Standard Israeli VAT rate | `0.18` | Verified as 18% from 01/01/2025; keep configurable. |
| Consumer price display | Full price in ₪ with VAT wording | Display the total price, including mandatory charges and taxes, before checkout. |
| Israel Tax Authority invoice allocation threshold | Above ₪5,000 before VAT as of 01/06/2026 | Fetch live minimum amount from the Tax Authority `MinimumAmount` service before deciding. |
| Israel Tax Authority allocation API | `Invoices/v2/Approval` | Use OAuth2 and delegated permissions through the approved accounting or tax adapter. |
| Bank of Israel exchange rates | SDMX API on `edge.boi.gov.il` | Use representative exchange-rate series and disclose the publication date. |
| WhatsApp Cloud API | Graph API `/{Phone-Number-ID}/messages` | Use templates where required and subscribe to the `messages` webhook field. |
| Webhook status events | `messages`, `statuses` inside the WhatsApp Business Account webhook payload | Treat status payloads as delivery telemetry, not payment confirmation. |

## Regulatory touchpoints cited

| Topic | Israeli source or framework | Chatbot impact | Safe implementation |
|---|---|---|---|
| Anti-spam and opt-out | Communications (Telecommunications and Broadcasting) Law, 1982, Section 30A | Promotional WhatsApp, SMS, email, or automated messages require consent and opt-out handling | Store consent timestamp, source, wording, and opt-out status. |
| Consumer cancellation and disclosure | Consumer Protection Law, 1981 and related cancellation regulations | Customer may ask about returns, cancellation, distance sale, or disclosure | Provide a neutral policy summary and escalate disputes. |
| Price display | Consumer Protection Law and Price Display rules | Consumer prices must be clear, total, and not misleading | Show the full price in ₪, VAT inclusion, recurring charges, and delivery fees. |
| VAT | Value Added Tax Law, 1975; standard rate verified as 18% on 03/06/2026 | Consumer prices usually need VAT-inclusive presentation | Use `כולל מע״מ` where applicable and keep `DEFAULT_VAT_RATE` configurable. |
| Tax invoices and receipts | Income Tax bookkeeping instructions, VAT invoicing rules, Israel Tax Authority requirements | Invoice requests, receipt issuance, allocation-number requirements for some B2B invoices | Integrate with accounting software; do not issue tax documents from free text. |
| Digital invoice allocation | Israel Tax Authority `חשבוניות ישראל` model | B2B invoices over the live legal threshold may require an allocation number for input VAT deduction | Check live threshold and call the accounting or Tax Authority adapter before issuing the final invoice. |
| Privacy | Protection of Privacy Law, 1981, Privacy Protection Regulations (Data Security), and Amendment 13 effective 14/08/2025 | Chat logs may include personal data | Minimize fields, publish notice, restrict access, log access, and apply retention limits. |
| Accessibility | Equal Rights for Persons with Disabilities Law and Service Accessibility Regulations | Digital service may require accessible alternative and readable responses | Keep responses short, support human alternative, and avoid putting critical information only in audio or image form. |
| Payment security | PCI DSS and local payment-provider terms | Card data must not be collected in chat | Send a secure payment link and store only transaction references. |
| Payment services | Payment Services Law, 2019 and provider terms | Customer may ask about charge, payment failure, refund, or authorization | Use approved provider status and handoff for disputes. |
| Warranty | Sale Law, Consumer Protection Law, and warranty regulations where applicable | Warranty questions must match product and business policy | State warranty months when known and escalate legal ambiguity. |
| Delivery | Consumer disclosures and courier terms | Delivery promises must be accurate | Use cautious estimates and confirm remote areas. |
| Marketing databases | Privacy and anti-spam requirements | Stored leads require purpose limitation and opt-out | Tag records by purpose and consent state. |

## General event model

Use a normalized event between inbound channel and chatbot logic. Store the raw inbound payload separately and pass only the minimum required fields to the sales decision layer.

### Request

```json
{
  "channel": "whatsapp",
  "external_conversation_id": "972501234567:2026-06-03",
  "message": "כמה עולה CRM לעסק קטן ואפשר בתשלומים?",
  "customer": {
    "name": "דנה",
    "city": "חיפה",
    "segment": "small_business",
    "has_marketing_consent": true,
    "preferred_installments": 3,
    "budget_ils": "600",
    "conversation_date": "03/06/2026"
  }
}
```

### Response

```json
{
  "intent": "price",
  "reply_he": "דנה, האפשרות המתאימה ביותר היא חבילת CRM בסיסית במחיר ₪249.00 כולל מע״מ...",
  "offers": [
    {
      "sku": "BASIC-CRM",
      "title": "חבילת CRM בסיסית",
      "price": "249.00",
      "relation": "base",
      "installment_line": "עד 3 תשלומים שווים של ₪83.00 כולל מע״מ; סך הכול ₪249.00 כולל מע״מ"
    }
  ],
  "handoff_required": false,
  "compliance_notes": [],
  "quote_id": "SC-03062026-1234ABCD"
}
```

## WhatsApp Cloud API adapter

Use WhatsApp service messages only during the customer service window. Use approved message templates where required by Meta policy, especially for business-initiated outreach or outreach outside the allowed service context. Keep Israeli anti-spam consent separate from platform opt-in because both may matter.

### Official host and send-message request pattern

```http
POST https://graph.facebook.com/{version}/{phone-number-id}/messages
Authorization: Bearer {access_token}
Content-Type: application/json
```

```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "המחיר הוא ₪249.00 כולל מע״מ. אפשר לשלם עד 3 תשלומים..."
  }
}
```

### Webhook fields and event names

Subscribe the app to the WhatsApp Business Account webhook field `messages`. The inbound payload can include `messages` for inbound messages and `statuses` for status updates about sent messages. Other webhook fields, such as `message_echoes`, `calls`, `consumer_profile`, and `messaging_handovers`, should be handled only if the integration explicitly uses them.

### Webhook inbound pattern

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "changes": [
        {
          "field": "messages",
          "value": {
            "messages": [
              {
                "from": "972501234567",
                "timestamp": "1780483200",
                "text": {"body": "כמה עולה?"}
              }
            ]
          }
        }
      ]
    }
  ]
}
```

### Status webhook pattern

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "changes": [
        {
          "field": "messages",
          "value": {
            "statuses": [
              {
                "id": "wamid.example",
                "status": "delivered",
                "timestamp": "1780483210",
                "recipient_id": "972501234567"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

### WhatsApp error table

| Error | Likely cause | Customer-safe response | Operator action |
|---|---|---|---|
| 400 bad request | Invalid payload or phone number | "לא הצלחתי לשלוח כרגע. נציג יחזור אליך." | Validate phone and message type. |
| 401 unauthorized | Token expired | No customer message if inbound failed | Rotate token. |
| 403 forbidden | Missing permission or template not approved | "ההודעה לא נשלחה. נציג יטפל בזה." | Check app permissions. |
| 429 rate limit | Too many messages | "יש עומס רגעי. נמשיך מיד כשאפשר." | Backoff and retry. |
| 470 or 131047 service window | Free-form message outside allowed window | Send an approved template only when consent and policy allow it | Check conversation window. |
| 5xx provider error | Provider outage | "יש תקלה זמנית בערוץ ההודעות." | Retry with idempotency. |

## Payment provider adapter

Use local providers such as Cardcom, Tranzila, Meshulam, PayBox for Business, Grow, or a bank-approved clearing provider according to the business setup. Do not hard-code provider-specific endpoints unless the account documentation confirms them. Do not ask for or store card numbers, CVV, or full card expiry in chat.

### Create payment link request

```json
{
  "amount_ils": "499.00",
  "currency": "ILS",
  "description": "חבילת CRM מקצועית",
  "customer": {
    "name": "דנה",
    "phone": "972501234567",
    "email": "dana@example.co.il"
  },
  "installments": {
    "requested": 6,
    "max_allowed": 6
  },
  "success_url": "https://example.co.il/pay/success",
  "cancel_url": "https://example.co.il/pay/cancel",
  "metadata": {
    "quote_id": "SC-03062026-1234ABCD",
    "sku": "PRO-CRM"
  }
}
```

### Create payment link response

```json
{
  "status": "created",
  "payment_url": "https://pay.example/secure/abc123",
  "transaction_reference": "TX-987654",
  "expires_at": "03/06/2026 23:59"
}
```

### Payment error table

| Error | Likely cause | Chatbot action |
|---|---|---|
| card_declined | Card issuer rejected payment | Offer secure retry or alternate method; do not ask for card details. |
| invalid_installments | Provider does not allow requested count | Recalculate with provider maximum and show the full total. |
| amount_mismatch | Catalog and payment amount differ | Stop checkout and alert operations. |
| expired_link | Customer used an old link | Generate a new quote and payment link. |
| duplicate_transaction | Retry sent twice | Show one confirmed transaction only. |
| refund_required | Refund request submitted | Handoff to billing. |

## Accounting and invoice adapter

Use the business accounting platform or bookkeeping provider to issue receipts, tax invoices, and credit documents. For applicable B2B invoices, the accounting system may need an allocation number from the Israel Tax Authority program.

### Invoice request

```json
{
  "document_type": "tax_invoice_receipt",
  "issue_date": "03/06/2026",
  "customer": {
    "name": "דנה כהן",
    "id_or_vat_number": "123456789",
    "email": "dana@example.co.il"
  },
  "lines": [
    {
      "sku": "PRO-CRM",
      "description": "חבילת CRM מקצועית",
      "quantity": 1,
      "unit_price_ils": "499.00",
      "vat_rate": "0.18"
    }
  ],
  "payment": {
    "method": "credit_card",
    "transaction_reference": "TX-987654"
  },
  "quote_id": "SC-03062026-1234ABCD"
}
```

### Invoice response

```json
{
  "status": "issued",
  "document_number": "INV-2026-000123",
  "allocation_number": "20260603123456789",
  "pdf_url": "https://accounting.example/documents/INV-2026-000123",
  "customer_email_sent": true
}
```

### Accounting error table

| Error | Cause | Action |
|---|---|---|
| missing_customer_id | Required for document type | Ask customer for official invoice details through a secure form. |
| vat_rate_invalid | Wrong VAT configuration | Stop issuing and notify finance. |
| allocation_required | Allocation number needed | Call ITA or accounting allocation flow before issue. |
| allocation_denied | ITA or accounting system rejected request | Handoff to bookkeeping. |
| document_already_issued | Duplicate request | Return existing document reference. |
| credit_document_required | Refund after invoice | Create credit document through accounting system. |

## Israel Tax Authority allocation adapter

Use this adapter only where the accounting provider or legal requirements indicate that allocation is required. As of the 03/06/2026 validation pass, the customer-facing Tax Authority service says the threshold is above ₪5,000 before VAT for 2026, following the 01/06/2026 change. Because the threshold changes by date, call the `MinimumAmount` service or accounting provider before issuing.

### Live threshold check request

```http
POST https://openapi.taxes.gov.il/shaam/production/general-information/v2/MinimumAmount
Authorization: Bearer {oauth2_token}
Content-Type: application/json
```

```json
{
  "date": "03-06-2026"
}
```

### Live threshold check response

```json
{
  "status": 200,
  "minimum_amount": 5000
}
```

### Allocation request endpoint

```http
POST https://ita-api.taxes.gov.il/shaam/production/Invoices/v2/Approval
Authorization: Bearer {oauth2_token}
Content-Type: application/json
```

Use sandbox during testing:

```http
POST https://ita-api.taxes.gov.il/shaam/tsandbox/Invoices/v2/Approval
```

### Allocation request pattern

```json
{
  "id_invoice": "DRAFT-2026-456",
  "type_invoice": 305,
  "number_vat": "512345678",
  "number_vat_customer": "515555555",
  "date_invoice": "2026-06-03",
  "amount_payment": "10000.00",
  "amount_vat": "1800.00",
  "payment_amount_including_vat": "11800.00"
}
```

### Allocation response pattern

```json
{
  "status": 200,
  "allocation_number": "20260603123456789",
  "valid_for_document_reference": "DRAFT-2026-456"
}
```

### Allocation errors

| Error | Cause | Action |
|---|---|---|
| 400 bad request | Logical or syntax problem in JSON | Validate schema and totals. |
| 401 unauthorized | OAuth2 failed or expired | Refresh token and retry once. |
| 403 forbidden | Missing service permission | Escalate to the accounting administrator. |
| 404 not found | Wrong service URI | Stop issuing and fix configuration. |
| 422 unprocessable entity | Field does not match schema | Recalculate and correct data. |
| 500 internal server error | Tax Authority service issue | Queue, retry, and notify finance. |
| threshold_not_required | Invoice is below live threshold | Continue normal invoice flow. |
| customer_number_invalid | Wrong customer VAT number | Request corrected business details. |
| amount_mismatch | Draft invoice totals changed | Recalculate and request again. |
| rejected | Rule or validation rejection | Handoff to accountant. |

## Bank of Israel rates adapter

Useful for businesses showing foreign-currency reference prices while charging in ₪. Do not settle in foreign currency unless the payment provider and invoicing system support it. The customer-facing sales reply should show ₪ by default.

### Representative exchange-rate request

```http
GET https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/?c%5BDATA_TYPE%5D=OF00&c%5BBASE_CURRENCY%5D=USD&c%5BCOUNTER_CURRENCY%5D=ILS&format=csv&startPeriod=2026-06-03&endPeriod=2026-06-03
```

### Representative exchange-rate response pattern

```csv
TIME_PERIOD,OBS_VALUE,BASE_CURRENCY,COUNTER_CURRENCY,DATA_TYPE
2026-06-03,3.7000,USD,ILS,OF00
```

### Rate errors

| Error | Cause | Action |
|---|---|---|
| rate_not_published | Weekend, holiday, or future date | Use the latest available rate and disclose its date. |
| unsupported_currency | Currency not supported | Ask for ₪ checkout. |
| stale_rate | Cached rate is too old | Refresh before quote. |
| api_hebrew_encoding | Hebrew metadata returned incorrectly | Use `locale=he&bom=include` when requesting Hebrew labels. |

## Shipping adapter

Common local providers include Israel Post, HFD, YDM, Gett Delivery, Cheetah, and courier aggregators. Actual fields vary by provider. Never promise delivery times that the provider has not confirmed.

### Create shipment request

```json
{
  "order_id": "ORDER-1001",
  "recipient": {
    "name": "דנה כהן",
    "phone": "972501234567",
    "city": "חיפה",
    "street": "הרצל",
    "house_number": "10"
  },
  "service_level": "standard",
  "items": [
    {"sku": "PRO-CRM", "quantity": 1}
  ]
}
```

### Shipment response

```json
{
  "status": "created",
  "tracking_number": "IL123456789",
  "estimated_delivery": "06/06/2026",
  "tracking_url": "https://delivery.example/track/IL123456789"
}
```

### Shipping error table

| Error | Cause | Action |
|---|---|---|
| unsupported_city | Provider cannot serve address | Offer pickup or human handoff. |
| invalid_phone | Phone format rejected | Request corrected phone. |
| address_incomplete | Missing street or number | Ask only for required address fields. |
| delivery_delay | SLA changed | Notify customer with updated date. |
| label_failed | Provider label service failed | Retry and alert operations. |

## Consent storage adapter

### Consent record

```json
{
  "customer_id": "CUST-1001",
  "phone": "972501234567",
  "channel": "whatsapp",
  "consent_type": "marketing",
  "status": "granted",
  "captured_at": "03/06/2026 10:20",
  "source": "checkout_checkbox",
  "wording_version": "marketing-consent-2026-01"
}
```

### Opt-out record

```json
{
  "customer_id": "CUST-1001",
  "channel": "whatsapp",
  "status": "revoked",
  "revoked_at": "03/06/2026 11:02",
  "raw_message": "נא להסיר אותי"
}
```

## Safe customer wording by failure type

| Failure | Hebrew wording |
|---|---|
| Payment provider down | "יש תקלה זמנית בתשלום. לא נגבו פרטים בצ׳אט. אפשר לנסות שוב עוד מעט או לקבל עזרה מנציג." |
| Invoice unavailable | "המסמך החשבונאי יישלח לאחר אישור הנהלת חשבונות." |
| Stock mismatch | "נדרש אישור מלאי לפני תשלום. נציג יבדוק ויחזור אליך." |
| Delivery uncertainty | "לכתובת הזו נדרש אישור זמינות משלוח. נציג יעדכן זמן ועלות סופיים." |
| Legal question | "אפשר לתת מידע כללי בלבד. נציג יבדוק את פרטי המקרה לפי תנאי העסק והדין החל." |
