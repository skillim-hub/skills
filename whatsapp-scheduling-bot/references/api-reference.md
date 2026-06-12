# API and Regulation Reference

Use this reference when building a WhatsApp appointment scheduling bot for Israel. Verify exact provider versions, pricing, policy wording, and legal obligations before production.


## Web-Validated Facts

Access date: 03/06/2026.

| Check | Confirmed value | Operational use |
|---|---|---|
| Current Graph API default | `v25.0`, released 18/02/2026 | Set `WHATSAPP_API_VERSION=v25.0`; keep configurable |
| WhatsApp send endpoint | `POST /{PHONE_NUMBER_ID}/messages` | Send free-form service messages and approved templates |
| WhatsApp webhook field | `messages` | Receive incoming customer messages and message status updates |
| Status values | `sent`, `delivered`, `read`, `failed` | Reconcile reminders by provider message ID and timestamp |
| Pricing basis | Per delivered message, by market and category | Do not hard-code NIS rates; fetch the current rate card before cost projections |
| Template language | Hebrew template code is `he` | Create separate approved Hebrew templates |
| Israeli VAT | `18%` from `01/01/2025` and still reflected in 2026 official materials | Use only for tax-inclusive display or invoice guidance |
| Israeli phone country code | `+972` | Normalize local numbers to digits-only international format for API payloads |

See `references/verification-log.md` for the two-pass source audit.

## Official Source Index

| Area | Source | URL | Usage |
|---|---|---|---|
| WhatsApp Cloud API | Meta WhatsApp Business Platform Cloud API | https://developers.facebook.com/docs/whatsapp/cloud-api | Send messages and configure phone number operations |
| Graph API versions | Meta Graph API changelog | https://developers.facebook.com/docs/graph-api/changelog | Confirm the current stable API version before release |
| Message templates | WhatsApp Business Platform message templates | https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates | Create Hebrew utility templates |
| Webhooks | WhatsApp Cloud API webhooks | https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks | Receive incoming customer messages and delivery statuses |
| Pricing | WhatsApp Business pricing | https://developers.facebook.com/docs/whatsapp/pricing | Estimate delivered-message costs by market and category |
| Messaging policy | WhatsApp Business Messaging Policy | https://www.whatsapp.com/legal/business-policy | Check allowed and prohibited business messaging |
| Anti-spam | Communications Law (Telecommunications and Broadcasting), section 30A | https://www.nevo.co.il/law_html/law01/032_002.htm | Separate service reminders from promotional messages |
| Privacy | Protection of Privacy Law, 5741-1981 | https://www.nevo.co.il/law_html/law01/087_001.htm | Minimize personal data and apply security obligations |
| Privacy regulator | Israel Privacy Protection Authority | https://www.gov.il/he/departments/the_privacy_protection_authority/govil-landing-page | Check official privacy guidance |
| Consumer protection | Consumer Protection Authority | https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority/govil-landing-page | Review cancellation notices and customer-facing policies |
| Public data | data.gov.il | https://data.gov.il | Search official datasets when holiday or public calendar data is needed |

## Version Strategy

Use a configurable Graph API version.

```bash
export WHATSAPP_API_VERSION="v25.0"
```

Do not hard-code a future API version. Check the changelog before release and update tests when payloads change.

## Authentication

```http
Authorization: Bearer EAAB...
Content-Type: application/json
```

Operational rules:

- Store tokens in a secrets manager.
- Use least-privilege system users.
- Rotate tokens after staff changes or suspected exposure.
- Mask token values in logs and errors.
- Separate test and production phone numbers.

## Send Free-Form Text

Use free-form text inside an active customer-service window.

```http
POST https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

Request:

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "972541234567",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "שלום דנה, התור שלך נקבע ל-18/06/2026 בשעה 10:30."
  }
}
```

Success response:

```json
{
  "messaging_product": "whatsapp",
  "contacts": [{"input": "972541234567", "wa_id": "972541234567"}],
  "messages": [{"id": "wamid.HBgMOTcyNTQxMjM0NTY3FQIAERg..."}]
}
```

## Send Template

Use an approved template outside the customer-service window or whenever provider policy requires it.

```http
POST https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

Request:

```json
{
  "messaging_product": "whatsapp",
  "to": "972541234567",
  "type": "template",
  "template": {
    "name": "appointment_confirmation_he",
    "language": {"code": "he"},
    "components": [
      {
        "type": "body",
        "parameters": [
          {"type": "text", "text": "דנה"},
          {"type": "text", "text": "ייעוץ ראשוני"},
          {"type": "text", "text": "קליניקת הדוגמה"},
          {"type": "text", "text": "18/06/2026"},
          {"type": "text", "text": "10:30"},
          {"type": "text", "text": "45"},
          {"type": "text", "text": "מחיר: ₪250. כתובת: רחוב הרצל 10, תל אביב."}
        ]
      }
    ]
  }
}
```

Response:

```json
{
  "messaging_product": "whatsapp",
  "contacts": [{"input": "972541234567", "wa_id": "972541234567"}],
  "messages": [{"id": "wamid.HBgMOTcyNTQxMjM0NTY3FQIAERg..."}]
}
```

## Create Hebrew Utility Template

```http
POST https://graph.facebook.com/v25.0/{WABA_ID}/message_templates
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

Request:

```json
{
  "name": "appointment_reminder_he",
  "language": "he",
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "תזכורת: התור שלך ל{{1}} ב{{2}} נקבע למחר, {{3}}, בשעה {{4}}. כתובת: {{5}}. לאישור הגעה יש להשיב 1. לשינוי או ביטול יש להשיב 2.",
      "example": {
        "body_text": [
          ["ייעוץ ראשוני", "קליניקת הדוגמה", "18/06/2026", "10:30", "רחוב הרצל 10, תל אביב"]
        ]
      }
    }
  ]
}
```

Response:

```json
{
  "id": "123456789012345",
  "status": "PENDING",
  "category": "UTILITY"
}
```

Template checklist:

- Match category to operational appointment content.
- Keep promotional language out of reminders.
- Supply realistic Hebrew examples.
- Keep variables short.
- Create a separate Hebrew version for each required use case.

## Webhook Verification

Incoming query:

```http
GET /webhook?hub.mode=subscribe&hub.verify_token=secret&hub.challenge=123456
```

Expected response:

```text
123456
```

Behavior:

| Condition | HTTP | Body |
|---|---:|---|
| mode is `subscribe` and token matches | 200 | challenge |
| token missing or wrong | 403 | Forbidden |
| challenge missing | 403 | Forbidden |

## Incoming Message Webhook

Example payload:

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WABA_ID",
      "changes": [
        {
          "field": "messages",
          "value": {
            "metadata": {"phone_number_id": "PHONE_NUMBER_ID"},
            "contacts": [{"profile": {"name": "דנה"}, "wa_id": "972541234567"}],
            "messages": [
              {
                "from": "972541234567",
                "id": "wamid.ID",
                "timestamp": "1718700000",
                "text": {"body": "אפשר תור למחר בבוקר?"},
                "type": "text"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

Parsed event:

```json
{
  "from_phone": "972541234567",
  "customer_name": "דנה",
  "message_id": "wamid.ID",
  "message_type": "text",
  "text": "אפשר תור למחר בבוקר?"
}
```

## Status Webhook

Example:

```json
{
  "statuses": [
    {
      "id": "wamid.ID",
      "status": "delivered",
      "timestamp": "1718700123",
      "recipient_id": "972541234567",
      "conversation": {"id": "conversation-id", "origin": {"type": "utility"}},
      "pricing": {"billable": true, "pricing_model": "PMP", "category": "utility", "type": "regular"}
    }
  ]
}
```

For older webhook versions or free-entry contexts, Meta documentation and partner implementations may still expose `CBP` or omit pricing fields. Persist provider message ID, appointment ID, recipient, template name, status, timestamp, pricing category, pricing model when present, and any error details.

## Israeli Phone Rules

| Input | API output |
|---|---|
| `054-123-4567` | `972541234567` |
| `+972 54 123 4567` | `972541234567` |
| `972541234567` | `972541234567` |
| `03-123-4567` | `97231234567` |

Reject short fragments, letters, premium numbers, and numbers that cannot receive WhatsApp.

## data.gov.il

No single official Israeli private-business appointment API exists. Use a calendar/CRM API for appointment storage. Use `data.gov.il` only when a flow needs public datasets such as holiday information, and verify dataset IDs before relying on them.

Generic CKAN search:

```http
GET https://data.gov.il/api/3/action/package_search?q=חגים
```

Response shape:

```json
{
  "success": true,
  "result": {
    "count": 12,
    "results": [
      {"id": "dataset-id", "title": "Example dataset", "resources": [{"format": "CSV", "url": "https://..."}]}
    ]
  }
}
```

## Israeli VAT Display

Use `₪` for prices. If a workflow needs tax wording, use `18%` VAT for Israeli VAT examples dated 01/01/2025 or later. Do not calculate VAT for medical, exempt, zero-rated, mixed, or cross-border cases without explicit accounting rules from the business.

Example customer-facing phrase:

```text
המחיר כולל מע"מ כחוק: ₪250.
```

## Israeli Compliance Notes

This is operational guidance, not legal advice.

### Service vs. Promotional Messages

Appointment confirmations, reminders, location instructions, and reschedule notices are service-related when the customer requested the appointment. Discounts, upsells, loyalty campaigns, and cross-sell messages may be advertising. Check section 30A before sending promotional content.

Practical rule:

- Keep service reminders purely logistical.
- Get separate marketing consent for promotions.
- Store opt-out requests.
- Do not append coupons to reminders without a valid marketing basis.

### Privacy

Appointment data is personal data. Some services may include sensitive context such as health, therapy, minors, accessibility needs, or finances. Apply data minimization.

Store only what is needed: name, phone, appointment details, delivery state, consent/opt-out state, and minimal staff notes.

Avoid storing full WhatsApp bodies, health details, payment card data, ID numbers, and unnecessary family details.

### Consumer Protection

Align cancellation fees, deposits, refunds, and remote-service terms with the business policy and applicable consumer law. Show the policy before asking for payment or enforcing a fee.

Suggested text:

```text
ביטול עד 24 שעות לפני התור ללא חיוב. ביטול מאוחר מטופל לפי מדיניות העסק.
```

## Error Tables

### HTTP and Provider Errors

| HTTP | Symptom | Likely cause | Action |
|---:|---|---|---|
| 400 | Invalid parameter | Bad phone or payload | Validate phone and payload |
| 401 | OAuth error | Expired or wrong token | Rotate token |
| 403 | Permission denied | Missing permission or asset access | Check WABA, phone ID, permissions |
| 404 | Object not found | Wrong API version or ID | Verify IDs and version |
| 429 | Rate limit | Too many sends or quality issue | Back off and queue |
| 500 | Temporary provider issue | Provider outage | Retry with jitter |

### Template Errors

| Error | Meaning | Fix |
|---|---|---|
| Template does not exist | Wrong name or WABA | Check exact approved name |
| Template paused | Quality or policy issue | Resolve quality or replace |
| Language not supported | No Hebrew approval | Create `he` template |
| Parameter mismatch | Wrong placeholder count | Fix parameter builder |
| Parameter too long | Variable exceeds limits | Shorten text |

### Business Errors

| Error | Customer-facing behavior | Operator action |
|---|---|---|
| Phone invalid | Ask staff to correct | Clean CRM data |
| Calendar conflict | Offer alternatives | Lock slots |
| Opt-out | Acknowledge and stop | Persist flag |
| Sensitive request | Route to human | Mark escalation |
| Duplicate webhook | No duplicate reply | Deduplicate by message ID |
| Cancelled appointment | Skip reminder | Reconcile queue |
