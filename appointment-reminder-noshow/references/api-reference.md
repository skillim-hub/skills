# API and Regulation Reference

Access date for all sources: 2026-06-05.

This reference summarizes public Israeli regulatory sources and messaging provider endpoints used by the appointment reminder workflow. Treat this file as implementation guidance, not legal advice.

## Validated Israeli rates and thresholds

| Item | Current value for this skill | Source | Short source quote |
|---|---:|---|---|
| VAT rate | 18% from 01-01-2025 | Knesset press release: https://main.knesset.gov.il/EN/News/PressReleases/Pages/press12324w.aspx | “VAT rate will be increased from 17% to 18%” |
| VAT amounts and rates page | Use Tax Authority page for rate tables and reporting periods | Israel Tax Authority: https://www.gov.il/en/pages/vat-rate-amount-new | “amounts and rates set out in VAT legislation” |
| Small business owner / exempt-dealer threshold | About 122,833 ₪ for 2026 | Tax Authority FAQ: https://www.gov.il/he/pages/faq-small-business-owner | “נכון לשנת 2026, מחזור העסקאות יהיה כ-122,833 ₪” |
| Exempt dealer online opening service | Use official online service, not a scraped form | Gov.il service: https://www.gov.il/he/service/request-open-exempt-dealer-via-internet | “להגיש בקשה לפתיחת תיק עוסק פטור” |

### How these values affect appointment reminders

- Display prices with VAT only when the business is an authorized VAT dealer and the price presentation requires VAT inclusion.
- Do not add VAT to an exempt dealer invoice line. Use the threshold only as an advisory configuration value; do not determine tax status from reminder data.
- Prefer `DD-MM-YYYY` in Hebrew messages and show ₪ before or after the amount consistently, for example `₪250`.

## Israeli privacy and database obligations

| Topic | Implementation rule | Source | Short source quote |
|---|---|---|---|
| Data security regulations | Apply privacy safeguards to customer and appointment records | Privacy Protection Authority: https://www.gov.il/he/pages/protection_of_privacy_regulations_data_security | “לקוחות, עובדים, ספקים, ילדים, מטופלים” |
| Database registration | Check whether the customer/appointment database requires registration or notice | Registration service: https://www.gov.il/he/service/registration_in_the_database | “בקשה לרישום מאגר מידע” |
| Database notice obligation | Use the online notice path when the statutory notice route applies | Notice obligation: https://www.gov.il/he/service/notice-obligation | “חובת הודעה לרשות להגנת הפרטיות” |
| Online privacy form | Use the Ministry of Justice form for notice details | Form page: https://mojforms.justice.gov.il/mojaemprivacyprotectionauthority/noticeobligation.html | “שם המאגר” |

### Privacy implementation requirements

- Store the smallest useful record: customer ID, name, phone, appointment time, channel consent, provider status, attendance result, and audit timestamps.
- Avoid storing sensitive service notes in reminder text or provider payloads.
- Keep consent proof: source, timestamp, channel, language, and operator or form ID.
- Delete or anonymize no-show history when retention is no longer justified by service operations.
- Keep provider callbacks authenticated and log only message IDs, not full message bodies, where feasible.

## Israeli spam, marketing, and calling controls

| Topic | Rule | Source | Short source quote |
|---|---|---|---|
| Spam law FAQ | Treat promotional WhatsApp/SMS as advertising that usually needs consent | Gov.il FAQ: https://www.gov.il/he/departments/faq/17052018_7 | “סעיף חוק הספאם, הינו סעיף 30א” |
| Do Not Call Me registry | Check before marketing phone calls; do not use reminders as sales calls | Gov.il DNC page: https://www.gov.il/he/pages/dont_call_me_fta | “לא יפנה בפנייה שיווקית” |
| DNC business portal | Register business access before using the DNC API | Portal URL from official API document: https://dnc.fta.gov.il/business | “הרישום לפורטל וביצוע פעולות” |
| DNC API document | Use the official API document for interface details | API PDF: https://www.gov.il/BlobFolder/news/cpfta_dncapi/he/%D7%9E%D7%A1%D7%9E%D7%9A%20%D7%9E%D7%9E%D7%A9%D7%A7%D7%99%20API%20%D7%9C%D7%97%D7%91%D7%A8%D7%95%D7%AA%20%D7%98%D7%9C%D7%9E%D7%A8%D7%A7%D7%98%D7%99%D7%A0%D7%92%20-%20%D7%90%D7%9C%20%D7%AA%D7%AA%D7%A7%D7%A9%D7%A8%20%D7%90%D7%9C%D7%99%20V5.pdf | “ממשק של פרויקט אל תתקשר אליי” |

### Transactional reminder boundary

A reminder for a booked appointment is generally operational, not a promotion. Keep it operational by limiting content to date, time, location, confirmation, cancellation, and re-booking for the same missed appointment. Add discounts, new packages, upgrades, or unrelated services only after marketing consent is documented.

## Consumer cancellation and no-show fees

| Topic | Implementation rule | Source | Short source quote |
|---|---|---|---|
| Cancellation fee guidance | Display cancellation and no-show terms before booking or payment | Gov.il consumer guide PDF: https://www.gov.il/BlobFolder/generalpage/information-olim-consumerism/he/smart-consumerism-en.pdf | “5% of the transaction or NIS 100” |

### Fee handling rule

Do not automatically charge a no-show fee from this skill. Flag the record for manual review unless the booking flow clearly disclosed the fee, the customer accepted it, the service category permits it, and the business has a lawful payment basis.

## Messaging provider endpoint paths

### Meta WhatsApp Cloud API

| Operation | Method and path | Notes | Source |
|---|---|---|---|
| Send message | `POST https://graph.facebook.com/{version}/{phone-number-id}/messages` | Use approved utility templates for business-initiated reminders outside the customer-service window. | Meta get started: https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started |
| Send service message | Same Messages API path | Use free-form messages only inside the service window. | Meta messages docs: https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages |
| Utility reminders | Template category should match appointment-reminder use | Utility messages can include appointment reminders. | WhatsApp utility messages: https://whatsappbusiness.com/products/conversation-categories/utility/ |

Common WhatsApp Cloud errors:

| Error | Meaning | Recommended handling |
|---|---|---|
| `400` | Invalid payload, missing template parameter, or bad phone format | Validate template name, language, variables, and E.164 phone. |
| `401` | Invalid or expired token | Rotate token and check app permissions. |
| `403` | Phone number, WABA, or template not allowed | Check business verification, number registration, and template status. |
| `429` | Rate or quality limit | Back off and reduce nonessential sends. |
| `5xx` | Provider service issue | Retry with exponential backoff and avoid duplicate reminders. |

### Twilio Programmable Messaging

| Operation | Method and path | Notes | Source |
|---|---|---|---|
| Send SMS/WhatsApp | `POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json` | Send SMS with `To`, `From` or `MessagingServiceSid`, and `Body`. | Twilio Message Resource: https://www.twilio.com/docs/messaging/api/message-resource |
| Delete message log | `DELETE https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages/{Sid}.json` | Use only when retention and provider rules permit deletion. | Twilio Message Resource: https://www.twilio.com/docs/messaging/api/message-resource |
| Status callback | Provider sends `POST` to configured `StatusCallback` URL | Store `MessageStatus` and `ErrorCode`, not full body. | Twilio status callbacks: https://www.twilio.com/docs/messaging/guides/track-outbound-message-status |

Common Twilio statuses and handling:

| Status | Meaning | Recommended handling |
|---|---|---|
| `queued` | Accepted for delivery queue | Keep scheduled record open. |
| `sent` | Accepted by upstream carrier | Wait for delivery callback. |
| `delivered` | Delivery confirmation received | Mark reminder delivered, not attended. |
| `undelivered` | Carrier/device delivery failure | Try permitted fallback channel or manual call. |
| `failed` | Provider could not send | Store error code and stop automated retries after the retry limit. |
| `read` | WhatsApp/RCS read event where available | Use as engagement signal, not attendance proof. |

### Israel Data.gov.il CKAN API

| Operation | Method and path | Use in this skill | Source |
|---|---|---|---|
| Search packages | `GET https://data.gov.il/api/3/action/package_search?q={query}` | Find public datasets such as calendars or municipal resources when needed. | Data Gov API docs: https://data.gov.il/docs |
| Search datastore | `GET https://data.gov.il/api/3/action/datastore_search?resource_id={id}` | Query a chosen public dataset after validating its schema. | Data Gov API docs: https://data.gov.il/docs |

Use public datasets only for non-sensitive enrichment, such as holiday avoidance or public branch lookup. Do not upload customer lists to public data endpoints.

### Israel Tax Authority lookup service

| Operation | Public path | Use in this skill | Source |
|---|---|---|---|
| VAT trader details lookup | https://www.gov.il/en/service/vat-apply-online | Validate a displayed supplier name/status manually during setup. | Gov.il VAT trader lookup: https://www.gov.il/en/service/vat-apply-online |

This service is a user-facing online service. Do not scrape it unless a documented API and terms allow automation.

## Provider payload examples

### WhatsApp utility template payload

```json
{
  "messaging_product": "whatsapp",
  "to": "+972501234567",
  "type": "template",
  "template": {
    "name": "appointment_reminder_he",
    "language": {"code": "he"},
    "components": [
      {
        "type": "body",
        "parameters": [
          {"type": "text", "text": "יעל"},
          {"type": "text", "text": "18-06-2026"},
          {"type": "text", "text": "15:30"}
        ]
      }
    ]
  }
}
```

### Twilio SMS form body

```text
To=%2B972501234567&From=ExampleSender&Body=...
```

## Error tables

### Validation errors

| Code | Trigger | Fix |
|---|---|---|
| `PHONE_INVALID` | Phone cannot be normalized to Israeli mobile E.164 | Request a valid mobile number, for example `050-123-4567`. |
| `CONSENT_MISSING` | No allowed channel has documented consent | Capture opt-in or use manual contact. |
| `QUIET_HOURS` | Reminder calculated between 21:00 and 08:00 | Move according to policy before provider handoff. |
| `PAST_SEND_TIME` | Reminder time is earlier than `now` | Skip that reminder or send only a same-day manual note. |
| `TEMPLATE_MISSING` | WhatsApp template name is absent | Configure an approved utility template. |
| `MARKETING_WITHOUT_CONSENT` | Message contains promotion without marketing opt-in | Remove promotional content or capture consent. |

### Provider errors

| Code | Provider | Typical cause | Fix |
|---|---|---|---|
| `AUTH_FAILED` | Any | Bad token, SID, secret, or signature | Rotate credentials and verify environment variables. |
| `RATE_LIMITED` | Any | Too many sends or quality throttling | Back off and batch sends. |
| `TEMPLATE_REJECTED` | WhatsApp | Template category or content mismatch | Rewrite as utility appointment reminder. |
| `UNDELIVERED` | SMS/WhatsApp | Device unreachable, blocked sender, carrier filter | Try permitted fallback or manual contact. |
| `CALLBACK_UNVERIFIED` | Any | Callback signature validation failed | Reject callback and investigate. |

## Deployment checklist

1. Configure environment variables for provider credentials.
2. Register and approve WhatsApp templates before production use.
3. Configure status callbacks over HTTPS.
4. Validate phone normalization on import.
5. Test Hebrew SMS length and segmentation costs.
6. Store consent and opt-out events.
7. Review privacy database obligations with a qualified adviser for sensitive or large-scale records.
8. Review cancellation/no-show fee policy before automated billing.
