# API and Regulation Reference

Use this reference as an implementation checklist. Verify current official requirements before production because tax thresholds, API contracts, VAT rates, WhatsApp policies, and privacy guidance can change.

## External references to verify

| Topic | Official source to verify | Use in this skill |
|---|---|---|
| WhatsApp Cloud API | https://developers.facebook.com/docs/whatsapp/cloud-api | Webhook, media download, reply sending, rate limits. |
| WhatsApp Business policies | https://www.facebook.com/policies_center/commerce/ | Customer-service window, templates, allowed messaging. |
| Israel Tax Authority | https://www.gov.il/he/departments/israel_tax_authority | VAT rules, bookkeeping guidance, Invoice Israel/allocation-number guidance. |
| VAT Law, 5736-1975 | Official Israeli legal databases and Tax Authority publications | Tax invoice and VAT handling. |
| Income Tax bookkeeping instructions | Israel Tax Authority publications | Source-document retention and bookkeeping controls. |
| Privacy Protection Authority | https://www.gov.il/he/departments/the_privacy_protection_authority | Personal-data minimization, security, retention, log redaction. |
| Electronic Signature Law | Official Israeli legal databases | Preservation of signed digital originals. |


## Live validation notes, accessed 2026-06-03

Use the verification log for source-by-source details. The current Israeli VAT rate is 18% from 01/01/2025 unless an official later publication changes it. The current Invoice Israel allocation threshold on 03/06/2026 is ₪5,000 before VAT for qualifying tax invoices, after an accelerated change from the older 2024 API specification. Keep the threshold schedule configurable by effective date.

Official or primary implementation URLs to pin in production runbooks:

| Area | URL | Implementation note |
|---|---|---|
| VAT rate and terminology | `https://www.gov.il/en/pages/taxes-glossary` | Confirms the standard VAT terminology and 18% rate from 01/01/2025. |
| Invoice Israel allocation service | `https://www.gov.il/he/service/request-assignment-number-for-tax-invoice` | Confirms thresholds and online allocation-number request service. |
| Invoice Israel topic page | `https://www.gov.il/he/departments/topics/israel-invoice` | Confirms phased allocation-number thresholds and related services. |
| WhatsApp messages API | `https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages` | Confirms message sending through the Messages API and customer-service-window constraints. |
| WhatsApp media API | `https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/media/media-api` | Confirms media ID retrieval and media URL download flow. |
| WhatsApp webhooks | `https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/` | Confirms `whatsapp_business_account` message webhook payloads. |
| Webhook verification and signatures | `https://developers.facebook.com/docs/graph-api/webhooks/getting-started/` | Confirms `hub.verify_token`, `hub.challenge`, and `X-Hub-Signature-256`. |
| Israeli privacy authority | `https://www.gov.il/he/departments/the_privacy_protection_authority` | Confirms privacy authority scope for personal data in digital databases. |

## WhatsApp webhook verification

```http
GET /webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=expected-token&hub.challenge=12345
```

Return `12345` as text only when the token matches. Return 403 on mismatch.

## Incoming media event example

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "972501234567",
          "id": "wamid.example",
          "timestamp": "1770451200",
          "type": "image",
          "image": {"id": "MEDIA_ID", "mime_type": "image/jpeg", "sha256": "..."}
        }]
      }
    }]
  }]
}
```

Process by verifying signature, extracting message ID and media ID, downloading media immediately, storing the original privately, acknowledging quickly, and running OCR in a worker queue.

## Confirmation reply example

```http
POST /v{version}/{phone-number-id}/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "נקלטה חשבונית מס/קבלה מ״א.ב. שירותים״ על סך ₪117.00, כולל מע״מ ₪18.00, תאריך 14/02/2026. מספר מסמך: 8841. תודה."
  }
}
```

## WhatsApp error table

| Status | Cause | Retry | Action |
|---:|---|---:|---|
| 400 | Invalid payload or recipient | No | Validate schema and E.164 phone. |
| 401 | Expired/invalid token | No | Rotate token; alert operations. |
| 403 | Missing permission or policy block | No | Check business/app permissions and templates. |
| 404 | Expired media URL | No | Ask sender to resend if original download failed. |
| 429 | Rate limit | Yes | Back off and honor retry-after guidance. |
| 500/503 | Provider fault | Yes | Retry with idempotency key. |

## VAT-rate configuration

Configure VAT by effective date. Use current official Israeli publications as the source of truth.

```json
{
  "vat_rates": [
    {"from": "2025-01-01", "to": null, "rate": 0.18},
    {"from": "2015-10-01", "to": "2024-12-31", "rate": 0.17}
  ],
  "rounding_tolerance_ils": 0.02
}
```

Validation request:

```json
{
  "issue_date": "2026-02-14",
  "document_type": "חשבונית מס/קבלה",
  "amount_before_vat": 99.0,
  "vat_amount": 18.0,
  "total_amount": 117.0
}
```

Validation response:

```json
{"vat_rate": 0.18, "within_tolerance": true, "status": "accepted", "warnings": []}
```

## Invoice allocation-number policy

Israeli Invoice Israel rules can require an allocation number for qualifying tax invoices. Keep thresholds, effective dates, and credentials configurable.

```json
{
  "allocation_number_policy": {
    "enabled": true,
    "effective_from": "2024-05-05",
    "thresholds": [
      {"from": "2024-05-05", "to": "2024-12-31", "amount_before_vat_min": 25000.0},
      {"from": "2025-01-01", "to": "2025-12-31", "amount_before_vat_min": 20000.0},
      {"from": "2026-01-01", "to": "2026-05-31", "amount_before_vat_min": 10000.0},
      {"from": "2026-06-01", "to": null, "amount_before_vat_min": 5000.0}
    ],
    "document_types": ["חשבונית מס", "חשבונית מס/קבלה"]
  }
}
```

| Condition | Status | Export |
|---|---|---|
| Not required by policy | Keep normal status | Allowed if other checks pass. |
| Required and present | `accepted` if other checks pass | Allowed. |
| Required and missing | `needs_review` | Blocked. |
| OCR ambiguous | `needs_review` | Blocked until reviewed. |

## Internal extraction API

Request:

```http
POST /internal/invoices/extract
Idempotency-Key: whatsapp:wamid.example
Content-Type: application/json

{
  "tenant_id": "business-123",
  "source": "whatsapp",
  "message_id": "wamid.example",
  "sender_phone": "+972501234567",
  "media": {"storage_uri": "s3://private/raw/wamid.example.jpg", "mime_type": "image/jpeg", "sha256": "..."},
  "locale": "he-IL",
  "reply_language": "he"
}
```

Accepted response:

```json
{
  "status": "accepted",
  "confidence": 0.93,
  "document": {
    "document_type": "חשבונית מס/קבלה",
    "vendor_name": "א.ב. שירותים בע"מ",
    "vendor_tax_id": "516123456",
    "invoice_number": "8841",
    "issue_date": "2026-02-14",
    "currency": "ILS",
    "amount_before_vat": 99.0,
    "vat_amount": 18.0,
    "total_amount": 117.0
  },
  "chat_reply": "נקלטה חשבונית מס/קבלה מ״א.ב. שירותים בע״מ״ על סך ₪117.00, כולל מע״מ ₪18.00, תאריך 14/02/2026. מספר מסמך: 8841. תודה.",
  "warnings": []
}
```

Error table:

| Code | Meaning | HTTP | Retry | Action |
|---|---|---:|---:|---|
| `media_unavailable` | Media not downloadable | 422 | No | Ask sender to resend. |
| `unsupported_media_type` | Not JPG/PNG/PDF | 415 | No | Request supported file. |
| `ocr_timeout` | OCR timed out | 504 | Yes | Retry then review. |
| `ocr_unreadable` | Low OCR confidence | 200 | No | Request clearer image. |
| `validation_failed` | VAT/date/field mismatch | 200 | No | Block export and review. |
| `duplicate_detected` | Existing dedupe key | 200 | No | Link prior record. |
| `policy_config_missing` | VAT/allocation config missing | 500 | No | Fix tenant config. |

## Privacy controls

Store only required business data. Hash or mask phone numbers. Mask IDs, bank details, card suffixes, and private storage URLs in logs. Store full OCR text and original images in restricted audit storage, not application logs. Define retention and deletion handling for chat text unrelated to accounting.
