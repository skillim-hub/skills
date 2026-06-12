# API and Regulation Reference

This reference maps the skill to common Israeli compliance duties and channel integrations. It is not legal advice. Verify current legislation, regulator guidance, and channel terms before production deployment.

## Regulatory map for Israel

Current VAT reference: the Israel Tax Authority lists VAT as a uniform 18% rate from 01/01/2025. This skill formats amounts in ₪ but does not calculate tax; when adding tax calculations, verify the current VAT rate before production use.

| Area | Source | Practical effect for this skill | Implementation control |
|---|---|---|---|
| Direct marketing and spam | Telecommunications Law (Bezeq and Broadcasts), 5742-1982, commonly section 30A | Promotional SMS, WhatsApp, email, and automated messages generally require prior consent and an opt-out path. | Track `consent_status`, add opt-out text, suppress opted-out contacts. |
| Privacy and databases | Protection of Privacy Law, 5741-1981 | Customer data must be collected, stored, and used for legitimate purposes. | Minimize fields, log purpose, delete stale records, restrict access. |
| Data security | Privacy Protection Regulations (Data Security), 5777-2017 | Databases holding personal data require security controls proportionate to risk. | Encrypt secrets, use role-based access, keep audit logs, review vendors. |
| Consumer rights | Consumer Protection Law, 5741-1981 | Follow-up messages must not mislead consumers or impair cancellation, refund, warranty, or other statutory rights. | Use factual wording, avoid pressure, keep terms outside review requests. |
| Electronic records | Electronic Signature Law, 5761-2001 and general evidentiary practice | Digital logs can support consent and delivery history when stored reliably. | Store immutable send logs and consent source metadata. |
| Accessibility and equal service | Equal Rights for Persons with Disabilities regulations and service accessibility duties where applicable | Customer communications should be readable and accessible. | Use plain text, avoid image-only messages, support alternate channels. |
| Review platform rules | Google, Meta, marketplace, and directory platform policies | Do not buy, fake, gate, or pressure reviews. | Ask neutrally and avoid incentives. |

Official sources commonly used for verification:

- Israel Ministry of Justice and Privacy Protection Authority portals: `https://www.gov.il/`
- Knesset or official law repositories for statutory text.
- Channel provider policy pages for WhatsApp, SMS, email, and review platforms.

## Data model

### Contact object

```json
{
  "contact_id": "cst_1029",
  "customer_name": "דנה",
  "phone_e164": "+972501234567",
  "email": "dana@example.co.il",
  "preferred_channel": "whatsapp",
  "consent_status": "transactional",
  "opted_out": false,
  "last_contact_at": "2026-06-01T11:20:00+03:00"
}
```

### Event object

```json
{
  "event_id": "svc_8891",
  "event_type": "service_completed",
  "event_date": "03/06/2026",
  "business_name": "אור חשמל",
  "business_type": "service",
  "sentiment": "unknown",
  "amount_ils": null,
  "review_url": "https://g.page/r/example/review"
}
```

### Send plan response

```json
{
  "should_send": true,
  "recommended_send_at": "2026-06-03T18:30:00+03:00",
  "timezone": "Asia/Jerusalem",
  "channel": "whatsapp",
  "message_he": "היי דנה, תודה שבחרת באור חשמל...",
  "compliance_notes": [
    "Transactional service follow-up.",
    "No promotional content.",
    "Review request not sent until satisfaction is confirmed."
  ],
  "idempotency_key": "svc_8891:cst_1029:service_completed:2026-06-03"
}
```

## WhatsApp Cloud API adapter

Use an approved WhatsApp Business account and templates where required by Meta policy. For customer-service window messages, respect the current WhatsApp policy and template requirements.

### Request example

```http
POST https://graph.facebook.com/<API_VERSION>/<WHATSAPP_BUSINESS_PHONE_NUMBER_ID>/messages
Authorization: Bearer {access_token}
Content-Type: application/json
```

```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "text",
  "text": {
    "preview_url": true,
    "body": "היי דנה, תודה שבחרת באור חשמל. רציתי לוודא שהכול תקין אחרי השירות מ-03/06/2026. אם יש משהו שדורש טיפול נוסף, אפשר לענות כאן."
  }
}
```

### Success response example

```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {
      "input": "972501234567",
      "wa_id": "972501234567"
    }
  ],
  "messages": [
    {
      "id": "wamid.HBgMOTcyNTAxMjM0NTY3FQIAERgS..."
    }
  ]
}
```

### Error table

| HTTP | Provider code | Meaning | Action |
|---:|---|---|---|
| 400 | `131026` | Recipient cannot receive message | Verify phone, channel eligibility, and opt-in. |
| 400 | `132000` | Template parameter mismatch | Fix template variables and locale. |
| 401 | `190` | Invalid or expired token | Rotate access token and retry once. |
| 429 | `4` or rate-limit code | Too many requests | Back off and retry with jitter. |
| 470 | policy-dependent | Outside customer-care window | Use approved template or wait for inbound response. |

## SMS gateway adapter

Many Israeli businesses use local SMS providers. The endpoint below is provider-neutral and illustrative; replace it with the selected vendor's documented API host.

### Request example

```http
POST https://sms-provider.example/api/v1/messages
Authorization: Bearer {api_key}
Content-Type: application/json
Idempotency-Key: svc_8891-cst_1029-checkin
```

```json
{
  "to": "+972501234567",
  "sender": "OR-HASHMAL",
  "body": "היי דנה, תודה שבחרת באור חשמל. רציתי לוודא שהכול תקין אחרי השירות מ-03/06/2026. להסרה: השיבי הסר",
  "encoding": "unicode",
  "scheduled_at": "2026-06-03T18:30:00+03:00"
}
```

### Response example

```json
{
  "message_id": "sms_71f4bb",
  "status": "queued",
  "segments": 2,
  "scheduled_at": "2026-06-03T18:30:00+03:00"
}
```

### Error table

| HTTP | Meaning | Action |
|---:|---|---|
| 400 | Invalid Israeli number format | Normalize to E.164 and reject landlines unless supported. |
| 402 | Insufficient balance | Stop batch, alert operator. |
| 409 | Duplicate idempotency key | Treat as already queued and do not send again. |
| 422 | Message too long or unsupported sender | Shorten text or change sender ID. |
| 429 | Rate limit | Retry later with backoff. |

## Email adapter

Use email for invoices, formal summaries, and longer explanations. Avoid sensitive data unless the mailbox and transport controls are appropriate.

### SMTP-style payload

```json
{
  "to": "dana@example.co.il",
  "subject": "בדיקת שביעות רצון אחרי השירות",
  "body_text": "היי דנה,\nתודה שבחרת באור חשמל. רציתי לוודא שהכול תקין אחרי השירות מ-03/06/2026.\nאם יש משהו שדורש טיפול נוסף, אפשר להשיב למייל הזה.\nתודה.",
  "headers": {
    "List-Unsubscribe": "<mailto:unsubscribe@example.co.il>"
  }
}
```

### Error table

| Error | Meaning | Action |
|---|---|---|
| `hard_bounce` | Address invalid | Suppress email channel and update contact. |
| `soft_bounce` | Temporary failure | Retry with capped attempts. |
| `complaint` | Recipient marked spam | Suppress and review consent source. |
| `blocked_content` | Link or text blocked | Remove suspicious shorteners and test domain reputation. |

## Google Business Profile review workflow

Google Business Profile APIs are primarily used to manage business location information and read or reply to reviews. A business typically sends a public review link to customers rather than creating reviews through an API. Do not submit reviews on behalf of customers.

### Store location reference

```json
{
  "location_name": "locations/123456789",
  "place_id": "ChIJexample",
  "review_url": "https://g.page/r/example/review",
  "business_name": "אור חשמל"
}
```

### Review reply request example

Use only for replying to an existing public review when the platform account has permission.

```http
PUT https://mybusiness.googleapis.com/v4/{name=accounts/*/locations/*/reviews/*}/reply
Authorization: Bearer {oauth_token}
Content-Type: application/json
```

```json
{
  "comment": "תודה על חוות הדעת. שמחנו לתת שירות."
}
```

### Error table

| HTTP | Meaning | Action |
|---:|---|---|
| 401 | OAuth token invalid | Re-authenticate account. |
| 403 | Missing location permission | Verify Business Profile role. |
| 404 | Review or location not found | Refresh location and review IDs. |
| 429 | Quota exceeded | Retry according to API quota guidance. |

## CRM webhook adapter

Use a CRM webhook when the skill only prepares messages and another system sends them. The endpoint below is illustrative; replace it with the selected CRM's documented webhook URL.

### Request example

```http
POST https://crm.example.co.il/hooks/followup-review
Content-Type: application/json
Authorization: Bearer {crm_token}
```

```json
{
  "contact_id": "cst_1029",
  "event_id": "svc_8891",
  "template_key": "service_checkin_v1",
  "message_he": "היי דנה, תודה שבחרת באור חשמל...",
  "scheduled_at": "2026-06-03T18:30:00+03:00",
  "channel": "whatsapp",
  "compliance_notes": [
    "Transactional follow-up",
    "No sensitive detail"
  ]
}
```

### Response example

```json
{
  "queued": true,
  "crm_task_id": "task_4421",
  "status": "pending_approval"
}
```

## Consent and opt-out records

### Create consent record

```json
{
  "contact_id": "cst_1029",
  "source": "checkout_checkbox",
  "scope": "marketing_sms",
  "captured_at": "2026-05-28T12:04:00+03:00",
  "ip": "203.0.113.5",
  "text_presented": "אני מסכים/ה לקבל עדכונים והטבות..."
}
```

### Opt-out record

```json
{
  "contact_id": "cst_1029",
  "channel": "sms",
  "received_text": "הסר",
  "received_at": "2026-06-03T18:44:00+03:00",
  "suppression_reason": "recipient_request"
}
```

## Idempotency

Use this format:

```text
{event_id}:{contact_id}:{event_type}:{event_date}
```

Store idempotency keys for at least the retry window. Treat duplicate keys as already sent or already queued.

## Security controls

- Store provider tokens in a secret manager, never in templates.
- Use HTTPS for every webhook.
- Store only the minimum personal data needed for follow-up.
- Hash or tokenize contact IDs in logs that do not need direct identifiers.
- Restrict export access.
- Delete stale CSV imports after migration.
- Keep audit logs for consent and opt-outs.
- Review vendor data-processing terms before sending production traffic.

## Compliance examples

### Transactional check-in without marketing

```text
היי דנה, רציתי לוודא שהכול תקין אחרי השירות מהיום. אם יש בעיה, אפשר לענות כאן.
```

### Promotional message requiring marketing consent

```text
היי דנה, תודה על חוות הדעת. לקוחות חוזרים מקבלים החודש 10% הנחה...
```

Control: require marketing consent and opt-out line, or remove the promotion.

### Review request without incentive

```text
אם השירות היה טוב עבורך, אפשר להשאיר חוות דעת קצרה כאן: {review_url}
```

Control: do not promise reward, discount, priority service, or refund for the review.


## Current Google review reply state fields

The Google Business Profile Reviews API now exposes `reviewReplyState` for review replies. Treat this as an API state field, not as proof that a public reply has appeared to customers.

| State | Meaning |
|---|---|
| `PENDING` | Reply is pending moderation. |
| `REJECTED` | Reply was rejected. |
| `APPROVED` | Reply was approved. |
