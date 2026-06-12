# API and Israeli Compliance Reference

Use this reference when integrating a Hebrew WhatsApp lead qualification bot with WhatsApp, CRM systems, spreadsheets, consent logs, payment links, and human queues in Israel. This is operational guidance, not legal advice. Verify current requirements before production.

## Source map

| Area | Source to review | Why it matters |
|---|---|---|
| WhatsApp | WhatsApp Business Platform documentation and policies | Inbound/outbound rules, templates, delivery, quality |
| Privacy | Protection of Privacy Law, 5741-1981 | Transparency, purpose limitation, personal data handling |
| Security | Protection of Privacy Regulations (Data Security), 5777-2017 | Access control, audit logs, vendor controls, incidents |
| Marketing | Communications Law section 30A | Promotional consent and opt-out |
| Consumers | Consumer Protection Law | Pricing, cancellation, misleading claims, disclosure |
| Accessibility | Equal Rights for Persons with Disabilities framework | Accessible service alternatives |
| Tax | Israel Tax Authority guidance | Receipts, invoices, VAT, business entity terms |
| Payments | Payment provider/acquirer rules and related Bank of Israel expectations | Payment links, refunds, chargebacks |
| Vendors | CRM and processor terms | retention, subprocessors, deletion/export |

## WhatsApp inbound message

```json
{
  "source": "whatsapp",
  "wa_message_id": "wamid.HBgMOTcy...",
  "received_at": "2026-06-03T10:15:00+03:00",
  "from_phone": "+972501234567",
  "business_phone_id": "1234567890",
  "type": "text",
  "text": "צריך הצעת מחיר לתיקון נזילה היום בתל אביב, תקציב 500 שח",
  "profile_name": "דנה"
}
```

## Normalized bot response

```json
{
  "to": "+972501234567",
  "type": "text",
  "text": "הבנתי, מדובר בתיקון נזילה בתל אביב. באיזו שעה נוח שיחזרו אליך?"
}
```

## Template examples

Utility/service follow-up:

```json
{
  "name": "lead_followup_service_he",
  "language": "he",
  "category": "UTILITY",
  "components": [{"type": "BODY", "text": "שלום {{1}}, בהמשך לפנייה שלך מ-{{2}}, אפשר לחזור אליך היום בין {{3}}?"}]
}
```

Marketing after separate opt-in:

```json
{
  "name": "lead_marketing_opted_in_he",
  "language": "he",
  "category": "MARKETING",
  "components": [{"type": "BODY", "text": "שלום {{1}}, יש עדכון שעשוי לעניין אותך בנושא {{2}}. להסרה כתבו הסרה."}]
}
```

## WhatsApp error table

| Error | Cause | Action |
|---|---|---|
| 400 invalid recipient | Phone is not normalized or not available | Request alternate contact channel |
| 400 template mismatch | Missing parameter | Validate before send |
| 401/403 | Token or permission problem | Alert operator and stop retry storm |
| 429 | Rate limit | Back off with jitter |
| Customer service window closed | Free-form outbound blocked | Use approved template where allowed |
| Template rejected | Category/content mismatch | Rewrite with clear purpose and opt-out where needed |
| Media failed | Expired URL or missing permission | Ask user to resend if essential |
| Signature failed | Invalid webhook source | Reject and log security event |

## Consent records

Service follow-up:

```json
{
  "subject_phone_e164": "+972501234567",
  "purpose": "service_followup",
  "status": "accepted",
  "source": "whatsapp_inbound",
  "text_version": "privacy-lead-v1",
  "timestamp": "2026-06-03T10:16:12+03:00"
}
```

Marketing:

```json
{
  "subject_phone_e164": "+972501234567",
  "purpose": "marketing_whatsapp",
  "status": "declined",
  "source": "whatsapp_inbound",
  "text_version": "marketing-optin-v1",
  "timestamp": "2026-06-03T10:17:03+03:00"
}
```

## Marketing opt-out

Detect these examples: הסרה, להסיר, תסירו, די, בטל, לא לשלוח, STOP, stop, unsubscribe, remove.

Response:

```text
הבקשה התקבלה. לא יישלחו אליך הודעות שיווקיות נוספות. הודעות שירות לגבי פנייה קיימת עשויות להישלח לפי הצורך.
```

## Consumer pricing payload

```json
{
  "quote_type": "estimate",
  "currency": "ILS",
  "amount_min": 350,
  "amount_max": 600,
  "vat_included": true,
  "limitations": ["כפוף לבדיקה", "לא כולל חלקים מיוחדים"],
  "valid_until": "10/06/2026"
}
```

## Tax terminology

| English | Hebrew |
|---|---|
| VAT | מע״מ |
| Tax invoice | חשבונית מס |
| Receipt | קבלה |
| Tax invoice/receipt | חשבונית מס/קבלה |
| Exempt dealer | עוסק פטור |
| Authorized dealer | עוסק מורשה |
| Limited company | חברה בע״מ |
| Nonprofit | עמותה |
| Israel Tax Authority | רשות המסים |
| National Insurance Institute | ביטוח לאומי |

## CRM create-lead request

```json
{
  "external_id": "wa:+972501234567:20260603T101500",
  "source": "WhatsApp",
  "created_at": "2026-06-03T10:15:00+03:00",
  "name": "דנה כהן",
  "phone": "+972501234567",
  "city": "תל אביב",
  "service": "plumbing",
  "description": "נזילה מתחת לכיור",
  "urgency": "same_day",
  "budget_ils": 500,
  "score": 88,
  "tier": "hot",
  "consent_service": true,
  "consent_marketing": false
}
```

## CRM errors

| Status | Cause | Action |
|---|---|---|
| 400 | Required field missing | Ask missing field or queue retry |
| 401 | Invalid token | Alert admin |
| 409 | Duplicate lead | Merge notes |
| 422 | Invalid phone | Normalize to E.164 |
| 429 | Rate limit | Retry with backoff |
| 500 | CRM outage | Queue locally and replay |

## CSV fallback

Recommended columns:

```csv
received_at,phone_e164,name,city,service,description,urgency,budget_ils,score,tier,consent_service,consent_marketing,owner,next_action,status
```

Use UTF-8 with BOM when opening Hebrew CSV files in Excel.

## Webhook security

Validate signatures where available, use HTTPS, reject unexpected content types, dedupe by WhatsApp message ID, rotate tokens, log request IDs, avoid sensitive raw-body logs, and use exponential backoff.

## Component boundaries

1. `ingest_message(payload)` validates and normalizes input.
2. `update_session(session, message)` updates the conversation state.
3. `qualify(lead)` calculates score and tier.
4. `record_consent(lead, consent)` writes the consent record.
5. `route(lead)` assigns owner and SLA.
6. `respond(lead)` generates the next Hebrew message.
7. `export(lead)` sends to CRM, spreadsheet, or webhook.


### Current WhatsApp endpoint defaults

```text
API host: https://graph.facebook.com
Send message: POST /{PHONE_NUMBER_ID}/messages
Webhook subscription field: messages
Status object: statuses
Template status webhook: message_template_status_update
```

Keep the API version, phone number ID, access token, and webhook verify token in environment variables or a secret manager.
