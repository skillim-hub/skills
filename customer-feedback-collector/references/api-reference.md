# API and Israeli Regulation Reference

This reference lists the APIs, URL patterns, legal sources, operational constraints, request examples, response examples, and common errors relevant to a customer-feedback collector in Israel.

Verify current statutes, regulator guidance, and platform terms before production use.

## Channel APIs

### Meta WhatsApp Cloud API

Primary reference: <https://developers.facebook.com/docs/whatsapp/cloud-api/>

Use for WhatsApp Business messages after Meta Business verification and template approval. Outbound review requests outside the 24-hour customer-service window usually require an approved message template.

#### Send template message

```http
POST https://graph.facebook.com/v25.0/{phone-number-id}/messages
Authorization: Bearer {access-token}
Content-Type: application/json
```

Pin a supported Graph API version at implementation time. The 2026 validation pass found Meta documentation listing v25.0 as an available current Graph version, so examples use v25.0 and avoid older pinned versions.

```json
{
  "messaging_product": "whatsapp",
  "to": "972501234567",
  "type": "template",
  "template": {
    "name": "review_request_he",
    "language": { "code": "he" },
    "components": [
      {
        "type": "body",
        "parameters": [
          { "type": "text", "text": "דנה" },
          { "type": "text", "text": "קליניקת הדר" },
          { "type": "text", "text": "https://www.google.com/maps/search/?api=1&query={BUSINESS_NAME}&query_place_id=ChIJ..." }
        ]
      }
    ]
  }
}
```

#### Example response

```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    { "input": "972501234567", "wa_id": "972501234567" }
  ],
  "messages": [
    { "id": "wamid.HBgMOTcyNTAxMjM0NTY3FQIAERgS..." }
  ]
}
```

#### Common errors

| HTTP | Code | Meaning | Action |
|---:|---|---|---|
| 400 | `100` | Invalid parameter | Validate E.164 phone, template name, language code. |
| 401 | `190` | Invalid or expired token | Refresh access token and check app permissions. |
| 403 | `10` | Permission denied | Confirm WhatsApp Business Account permissions. |
| 404 | `803` | Phone number ID not found | Verify account and phone number ID. |
| 429 | `4` | Rate limit | Back off and queue messages. |

### SMS provider API

No single Israeli SMS API standard exists. Providers usually expose HTTPS endpoints with API key authentication. Twilio is common for programmable SMS and supports Israeli recipients subject to sender, content, and compliance rules.

Twilio Messaging API reference: <https://www.twilio.com/docs/messaging/api/message-resource>

SMS may be segmented and charged per segment. Treat Hebrew SMS as Unicode/UCS-2 and keep messages short. Status callbacks can include states such as `queued`, `sent`, `delivered`, `undelivered`, and `failed`.

#### Generic SMS request

```http
POST https://api.sms-provider.example/messages
Authorization: Bearer {api-key}
Content-Type: application/json
```


```json
{
  "to": "+972501234567",
  "from": "ClinicHadar",
  "text": "דנה, תודה שבחרת בקליניקת הדר. חוות דעת קצרה תעזור ללקוחות באזור: https://x.co/rev להסרה: הסר",
  "encoding": "unicode"
}
```

#### Example response

```json
{
  "message_id": "sms_7fc0b29",
  "status": "queued",
  "segments": 2,
  "encoding": "unicode"
}
```

#### Common errors

| HTTP | Meaning | Action |
|---:|---|---|
| 400 | Invalid phone number | Normalize to `+972` and reject landlines for SMS when needed. |
| 400 | Text too long | Shorten or accept multi-segment cost. |
| 401 | Invalid API key | Rotate key and verify environment variables. |
| 403 | Sender ID blocked | Register sender or use provider-approved sender. |
| 429 | Throughput exceeded | Queue and retry with exponential backoff. |

### Email provider API

Use any reputable email provider with suppression-list support. SendGrid is a common example.

SendGrid Mail Send API reference: <https://docs.sendgrid.com/api-reference/mail-send/mail-send>

EU subusers can use `https://api.eu.sendgrid.com` according to the Mail Send reference.

#### Send email request

```http
POST https://api.sendgrid.com/v3/mail/send
Authorization: Bearer {api-key}
Content-Type: application/json
```


```json
{
  "personalizations": [
    { "to": [{ "email": "dana@example.co.il", "name": "דנה כהן" }] }
  ],
  "from": { "email": "service@example.co.il", "name": "קליניקת הדר" },
  "subject": "אפשר לבקש חוות דעת קצרה?",
  "content": [
    {
      "type": "text/plain",
      "value": "שלום דנה,\n\nתודה על האמון בקליניקת הדר.\nאפשר להשאיר חוות דעת קצרה כאן:\nhttps://www.google.com/maps/search/?api=1&query={BUSINESS_NAME}&query_place_id=ChIJ...\n\nלהסרה מרשימת הודעות כאלה, אפשר להשיב הסרה."
    }
  ]
}
```

#### Example response

Expected success: HTTP `202 Accepted` with an empty body.

#### Common errors

| HTTP | Meaning | Action |
|---:|---|---|
| 400 | Bad email payload | Validate recipient, sender, content type, and subject. |
| 401 | Invalid API key | Rotate key and check permissions. |
| 403 | Sender not verified | Complete domain authentication. |
| 413 | Payload too large | Remove attachments; send plain text. |
| 429 | Rate limit | Queue and retry. |

## Rating-platform destinations

### Google Business Profile / Google Maps destination link

Google Business Profile APIs reference: <https://developers.google.com/my-business/>

Google Maps Place IDs reference: <https://developers.google.com/maps/documentation/places/web-service/place-id>

Official Maps destination URL pattern:

```text
https://www.google.com/maps/search/?api=1&query={BUSINESS_NAME}&query_place_id={PLACE_ID}
```

Example:

```text
https://www.google.com/maps/search/?api=1&query=Example+Business&query_place_id=ChIJN1t_tDeuEmsRUsoyG83frY4
```

Operational notes:

- Test on Android, iOS, and desktop.
- Keep the Place ID stable in configuration.
- Do not ask only happy customers to post publicly in a misleading way.
- Do not offer incentives for positive ratings.
- Use Google Business Profile management APIs for profile data when authorized; do not scrape Google pages.
- Direct write-review shortcuts found on the web are not documented as the official Maps URL pattern in the validation pass. Use the official Maps URL by default, and only use a write-review shortcut after manual browser testing and platform-terms review.

### Facebook Page reviews / recommendations

Graph API reference: <https://developers.facebook.com/docs/graph-api/>

Destination URL pattern:

```text
https://www.facebook.com/{page-id-or-slug}/reviews/
```

Operational notes:

- Page review availability depends on page settings and Meta product changes.
- Use Graph API for owned-page metadata where permitted.
- Do not automate posting on behalf of customers.

### Zap

Zap is a prominent Israeli comparison and review destination. Public write-review APIs are not generally available for arbitrary businesses.

Destination pattern:

```text
https://www.zap.co.il/clientcard.aspx?siteid={SITE_ID}
```

Operational notes:

- Use the verified business/product page URL.
- Test the link manually.
- Avoid automated scraping.
- Maintain a monthly URL verification task.

### Easy

Easy is a local Israeli business directory and discovery platform. Public write-review APIs are not generally available for arbitrary businesses.

Destination pattern:

```text
https://easy.co.il/page/{PAGE_ID}
```

Operational notes:

- Use the verified business page.
- Send customers to the profile page only when the review entry point is visible and stable.
- Keep Google as fallback when Easy does not expose a reliable review entry point.

### Midrag

Midrag is relevant for many service-provider categories in Israel. Public write-review APIs are not generally available for arbitrary businesses.

Operational notes:

- Use the business profile URL supplied by the platform.
- Check platform rules for who may review and how review invitations may be sent.
- Do not submit reviews on behalf of customers.

### B144

B144 is an Israeli business directory. Public write-review APIs are not generally available for arbitrary businesses.

Operational notes:

- Use the business profile URL.
- Treat the profile URL as a destination, not an API.
- Re-check profile pages after listing updates.

### Custom first-party testimonial form

Use a first-party form when:

- The service is sensitive.
- The business needs explicit testimonial approval.
- The public platform has no stable link.
- A private-first flow is required.

Example form fields:

```json
{
  "customer_name": "דנה כהן",
  "rating": 5,
  "testimonial_text": "שירות מקצועי, נעים ומהיר.",
  "publish_approval": true,
  "display_name_preference": "first_name_only",
  "approval_date": "03/06/2026"
}
```

## Israeli legal and regulatory sources

### Communications Law, Section 30A (“Spam Law”)

Primary source: Communications Law (Telecommunications and Broadcasting), 5742-1982, Section 30A. Official government/legal database versions should be checked before launch.

Operational impact:

- Commercial messages generally require consent unless a statutory exception applies.
- Opt-out must be simple and honored.
- Messages that combine feedback with promotional content can become advertising.
- Keep evidence of consent and opt-out handling.

Safe implementation:

```json
{
  "consent_basis": "transaction_followup",
  "source": "appointment_booking",
  "captured_at": "03/06/2026",
  "opt_out_text": "להסרה: השב/י הסר",
  "suppression_checked": true
}
```

### Protection of Privacy Law, 5741-1981

Primary source: Protection of Privacy Law, 5741-1981. Check current version and regulator guidance from the Privacy Protection Authority before production.

Operational impact:

- Collect only required personal data.
- Define purpose: feedback collection and service improvement.
- Restrict access to contact lists, ratings, and testimonial approvals.
- Handle deletion, access, correction, and opt-out requests.
- Review current database registration, notification, and security obligations.

### Protection of Privacy Regulations (Data Security), 5777-2017

Primary source: Protection of Privacy Regulations (Data Security), 5777-2017.

Operational impact:

- Maintain data-security procedures.
- Limit permissions.
- Log access where required.
- Protect exports and API keys.
- Delete stale campaign files.

Minimum control table:

| Control | Minimum practice |
|---|---|
| API keys | Environment variables or secret manager; no source control. |
| Exports | Encrypted storage or restricted drive permissions. |
| Logs | No sensitive service details in message logs. |
| Access | Named users only; no shared generic account. |
| Retention | Delete campaign files after defined period. |

### Consumer Protection Law, 5741-1981

Primary source: Consumer Protection Law, 5741-1981.

Operational impact:

- Avoid misleading testimonials.
- Do not fabricate reviews.
- Do not hide material connections.
- Do not edit testimonials in a way that changes meaning.
- Do not imply a review represents typical results unless supportable.

Approval record example:

```json
{
  "testimonial_text": "שירות מקצועי ומהיר.",
  "approved_by": "דנה כהן",
  "approved_at": "2026-06-03T10:15:00+03:00",
  "display_name": "דנה",
  "publication": "website_homepage",
  "source_message_id": "email_123"
}
```

### Accessibility: Equal Rights for Persons with Disabilities framework and Israeli Standard 5568

Primary sources: Equal Rights for Persons with Disabilities Law and accessibility regulations; Israeli Standard 5568 aligns web accessibility with WCAG principles.

Operational impact:

- Feedback forms should be accessible by keyboard and screen readers.
- Link text should be meaningful.
- SMS and WhatsApp messages should avoid image-only instructions.
- Email should include plain-text content.
- Public testimonial pages should meet applicable accessibility obligations.

### Defamation and professional confidentiality

Primary sources: Israeli defamation law and sector-specific confidentiality/professional rules may apply.

Operational impact:

- Do not include sensitive facts in public prompts.
- Do not respond to negative reviews by revealing private customer details.
- For health, therapy, finance, legal, minors, or education contexts, use privacy-preserving wording and private-first routing.

## Data model reference

### Contact

```json
{
  "full_name": "דנה כהן",
  "phone": "+972501234567",
  "email": "dana@example.co.il",
  "consent": true,
  "preferred_channel": "whatsapp",
  "last_interaction_date": "03/06/2026",
  "tags": ["clinic", "appointment-complete"]
}
```

### Delivery plan item

```json
{
  "contact": "דנה כהן",
  "channel": "whatsapp",
  "to": "+972501234567",
  "review_url": "https://www.google.com/maps/search/?api=1&query={BUSINESS_NAME}&query_place_id=ChIJ...",
  "body": "שלום דנה...",
  "warnings": [],
  "send_after": "03/06/2026 17:00"
}
```

## Error table for the helper client

| Error | Cause | Fix |
|---|---|---|
| `InvalidPhoneNumber` | Local phone could not normalize to `+972` | Check number format and mobile prefix. |
| `MissingReviewDestination` | Platform selected without required Place ID/URL | Add platform-specific URL or Place ID. |
| `ConsentRequired` | Contact has `consent=false` | Do not send; obtain lawful basis first. |
| `QuietTimeBlocked` | Send time falls in Israeli quiet-time rules | Reschedule to next safe window. |
| `HebrewValidationWarning` | Message lacks Hebrew or has poor structure | Start with Hebrew and use tested templates. |
| `UnsubscribeMissing` | Message lacks opt-out wording | Add `להסרה: השב/י הסר` or equivalent. |
| `ProviderRejected` | Channel API rejected request | Inspect provider error and retry only when safe. |
